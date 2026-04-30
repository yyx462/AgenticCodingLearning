# Deep Dive: Hybrid Search Engine

> Part of: [[00_Closed_Loop_Search]] — Step 4

## What Happens

RAGFlow runs **two complementary searches** and fuses their scores. This catches both semantic matches (vector) and exact keyword hits (BM25).

## Key File: `rag/nlp/search.py`

### `Dealer` class — the search orchestrator

```python
class Dealer:
    def __init__(self, dataStore: Base):
        self.qryr = dataStore  # Elasticsearch or Infinity client

    async def retrieval(self, question, embd_mdl, tenant_ids, kb_ids,
                        page, page_size, similarity_threshold=0.2,
                        vector_similarity_weight=0.3, top=1024,
                        rerank_mdl=None, ...):
```

### Step-by-step inside `retrieval()`

```
1. Build the query
   ├── Embed query text → query_vector
   ├── Extract keywords from query
   └── Compute rank features (optional)

2. Execute search (self.search())
   ├── Build ES query with:
   │   ├── knn clause (vector similarity)
   │   ├── match clause (keyword BM25)
   │   ├── filter by kb_ids, tenant_ids
   │   └── rank_feature boosters
   └── Execute against all tenant indices

3. Post-process results
   ├── Apply similarity_threshold
   ├── Rerank if model provided
   ├── Paginate (page, page_size)
   └── Return {total, chunks, doc_aggs}
```

## Vector Search Deep Dive

**Index structure** in Elasticsearch:
```json
{
    "mappings": {
        "properties": {
            "q_1536_vec": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil"
                }
            },
            "content_with_weight": { "type": "text" },
            "content_ltks": { "type": "text" },
            "docnm_kwd": { "type": "keyword" },
            "kb_id": { "type": "keyword" },
            "position_int": { "type": "integer" }
        }
    }
}
```

**kNN query:**
```python
# search() builds this:
{
    "size": top,
    "query": {
        "bool": {
            "filter": [
                {"terms": {"kb_id": kb_ids}},
                {"terms": {"tenant_id": tenant_ids}}
            ],
            "should": [
                {
                    "knn": {
                        "field": f"q_{dim}_vec",
                        "query_vector": query_embedding,
                        "k": top,
                        "num_candidates": top * 2
                    }
                },
                {
                    "match": {
                        "content_ltks": {
                            "query": question,
                            "minimum_should_match": "30%"
                        }
                    }
                }
            ]
        }
    }
}
```

## Score Computation

### Internal Rerank (no external model)

```python
def rerank(self, sres, question, tkweight, vtweight, rank_feature=None):
    """
    tkweight = 1 - vector_similarity_weight  (keyword weight)
    vtweight = vector_similarity_weight       (vector weight)
    """
    # sres contains both similarity types
    for i in range(len(sres)):
        sim = tkweight * text_sim[i] + vtweight * vec_sim[i]

        # Apply rank feature if configured
        if rank_feature:
            # PageRank-style boost
            sim += rank_feature_weight * feature_score

        sres.similarity[i] = sim
```

### Example with Numbers

```
Query: "What chunking methods does RAGFlow support?"

Vector search results (top 5):
  chunk_A: cosine_sim = 0.91  "RAGFlow supports token-based and delimiter-based chunking..."
  chunk_B: cosine_sim = 0.87  "Chunking configuration includes token_num and overlap..."
  chunk_C: cosine_sim = 0.83  "The naive parser splits text by configurable delimiters..."
  chunk_D: cosine_sim = 0.79  "PDF layout recognition identifies sections..."
  chunk_E: cosine_sim = 0.72  "Knowledge bases store embedded chunks..."

Keyword search results (top 5):
  chunk_C: bm25_score = 0.88  ← contains "chunking", "delimiter", "naive"
  chunk_F: bm25_score = 0.82  ← contains "chunking methods"
  chunk_A: bm25_score = 0.75  ← contains "chunking", "RAGFlow"
  chunk_G: bm25_score = 0.71  ← contains "chunking"
  chunk_B: bm25_score = 0.68  ← contains "chunking", "token"

Fused scores (vw=0.3):
  chunk_A: 0.3*0.91 + 0.7*0.75 = 0.798  ← #1
  chunk_C: 0.3*0.83 + 0.7*0.88 = 0.865  ← #1 (keyword champion)
  chunk_B: 0.3*0.87 + 0.7*0.68 = 0.737
  chunk_F: 0.3*0.00 + 0.7*0.82 = 0.574  (no vector match)
```

## Special Retrieval Modes

### TOC-Based Retrieval (`retrieval_by_toc()`)
- Finds table-of-contents chunks
- Uses LLM to pick relevant sections
- Adds supplementary context from TOC entries

### Parent-Child Retrieval (`retrieval_by_children()`)
- Groups child chunks under parent chunks
- Uses average similarity for parent selection
- Reduces redundancy — returns parent with all children

## Connection to Next Step

After scoring, top candidates are optionally sent to a reranker. See [[04_Reranking]].
