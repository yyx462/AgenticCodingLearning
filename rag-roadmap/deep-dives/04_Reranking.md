# Deep Dive: Reranking

> Part of: [[00_Closed_Loop_Search]] — Step 5

## What Happens

After hybrid search returns candidates, an optional reranker model re-scores them for more accurate relevance. This is a **second-pass** scoring that considers query-document semantic similarity more deeply than vector cosine alone.

## Key File: `rag/llm/rerank_model.py`

## Why Reranking Helps

Vector search is fast but approximate. Reranking uses a cross-encoder that jointly processes query + document, producing a more accurate relevance score.

```
Without reranking:
  Query vec → cosine sim with chunk vec → score
  (embeddings computed independently, compared by angle)

With reranking:
  Query + Chunk text → cross-encoder model → relevance score
  (model sees BOTH texts together, can reason about match quality)
```

## Supported Rerankers

| Provider | Model Example | Notes |
|----------|--------------|-------|
| Jina | `jina-reranker-v2-base-multilingual` | Multilingual, fast |
| Cohere | `rerank-english-v3.0` | High quality for English |
| Voyage AI | `voyage-ref-2` | Specialized for technical docs |
| Local | Any OpenAI-compatible rerank endpoint | Self-hosted |

## Reranking Flow

```python
# In Dealer.retrieval():
if rerank_mdl and sres.total > 0:
    sim, tsim, vsim = self.rerank_by_model(
        rerank_mdl, sres, question,
        tkweight=1 - vector_similarity_weight,
        vtweight=vector_similarity_weight
    )
```

### `rerank_by_model()` internals

```python
def rerank_by_model(self, rerank_mdl, sres, query, tkweight, vtweight):
    # 1. Collect chunk texts
    texts = [sres.field[i]["content_with_weight"] for i in sres.ids]

    # 2. Call reranker API
    #    Truncates texts to 8196 chars to stay within token limits
    ranks, token_count = rerank_mdl.similarity(query, texts)

    # 3. Combine reranker score with keyword similarity
    #    reranker score replaces vector similarity in the fusion formula
    for i in range(len(ranks)):
        sim[i] = tkweight * text_sim[i] + vtweight * ranks[i]

    return sim, text_sim, ranks
```

## Example: Jina Reranker

```python
class Jina(Base):
    def similarity(self, query, texts):
        texts = [truncate(t, 8196) for t in texts]

        resp = requests.post(
            "https://api.jina.ai/v1/rerank",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model_name,
                "query": query,
                "documents": texts,
                "top_n": len(texts)
            }
        )

        # Returns relevance scores for each (query, doc) pair
        ranks = np.zeros(len(texts))
        for result in resp.json()["results"]:
            ranks[result["index"]] = result["relevance_score"]

        return ranks, token_count
```

## Score Fusion After Reranking

```
Before reranking (hybrid search scores):
  chunk_A: vec=0.91, kw=0.75 → fused=0.798
  chunk_C: vec=0.83, kw=0.88 → fused=0.865  ← top by hybrid
  chunk_B: vec=0.87, kw=0.68 → fused=0.737

After reranking (cross-encoder replaces vector score):
  chunk_A: rerank=0.95, kw=0.75 → 0.3*0.75 + 0.7*0.95 = 0.890  ← new #1
  chunk_C: rerank=0.72, kw=0.88 → 0.3*0.88 + 0.7*0.72 = 0.768
  chunk_B: rerank=0.81, kw=0.68 → 0.3*0.68 + 0.7*0.81 = 0.771

The cross-encoder decided chunk_A is actually more relevant despite
lower keyword match — it understood the semantic relationship better.
```

## Reranking Limits

```python
# From search.py — caps candidates to avoid expensive API calls
RERANK_LIMIT = max(30, ceil(64 / page_size) * page_size)
if rerank_mdl:
    RERANK_LIMIT = min(RERANK_LIMIT, top, 64)  # Max 64 candidates
```

Only top 30-64 candidates get reranked. This balances cost vs. quality.

## When to Use Reranking

| Scenario | Reranking? | Why |
|----------|-----------|-----|
| Small KB (<1000 chunks) | Optional | Vector search already accurate |
| Large KB (>10k chunks) | Recommended | More noise in initial results |
| Multi-language content | Recommended | Cross-encoder handles translation gaps |
| High-precision use cases | Required | Maximize relevance of top results |

## Connection to Next Step

After reranking, top-K chunks are formatted into context for the LLM. See [[05_Context_Building]].
