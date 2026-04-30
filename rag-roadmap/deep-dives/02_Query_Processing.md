# Deep Dive: Query Processing & Retrieval Orchestration

> Part of: [[00_Closed_Loop_Search]] — Step 2 & 3

## What Happens

The dialog service orchestrates retrieval: it embeds the query, performs hybrid search across knowledge bases, and collects relevant chunks.

## Key Files

| File | Role |
|------|------|
| `api/db/services/dialog_service.py` | Orchestration: `async_chat()` ties everything together |
| `rag/nlp/search.py` | Core search: `Dealer.retrieval()` |
| `rag/llm/embedding_model.py` | Query embedding |
| `agent/tools/retrieval.py` | Agent-mode retrieval with metadata filters |

## `async_chat()` Flow

This is the **brain** of the search loop. Simplified:

```python
async def async_chat(dialog, messages, stream=True, **kwargs):
    # 1. Load models
    chat_mdl, embd_mdl, rerank_mdl = get_models(dialog)

    # 2. Extract query from messages
    question = messages[-1]["content"]

    # 3. Optional: keyword extraction via LLM
    if prompt_config.get("keyword"):
        questions = await keyword_extraction(chat_mdl, question)
    else:
        questions = [question]

    # 4. Optional: cross-language translation
    if cross_languages:
        question = await cross_languages(tenant_id, None, question, langs)

    # 5. Retrieval
    kbinfos = await retrievaler.retrieval(
        question,
        embd_mdl,
        tenant_ids,
        kb_ids,
        page=1, page_size=top_n,
        similarity_threshold=0.2,
        vector_similarity_weight=0.3,
        rerank_mdl=rerank_mdl,
    )

    # 6. Build context string from chunks
    knowledges = "\n------\n".join(
        f"Source: {c['docnm_kwd']}\n{c['content_with_weight']}"
        for c in kbinfos["chunks"][:top_n]
    )

    # 7. Generate answer via LLM (see 06_LLM_Generation)
    async for token in chat_mdl.async_chat_streamly_delta(
        system=system_prompt_with_context(knowledges),
        history=messages[:-1],
        gen_conf={temperature, top_p, max_tokens}
    ):
        yield {"answer": token, "reference": kbinfos}
```

## Hybrid Search Details (`Dealer.retrieval()`)

Two searches run in parallel against Elasticsearch/Infinity:

### Vector Search
```
Query: "How does chunking work?"
  → Embedding model → [0.012, -0.034, 0.078, ...]  (1536 dims)
  → Elasticsearch kNN query: {
      "knn": {
        "field": "q_1536_vec",
        "query_vector": [0.012, -0.034, ...],
        "k": 1024,
        "num_candidates": 2048
      }
    }
  → Returns chunks ranked by cosine similarity
```

### Keyword Search
```
Query: "How does chunking work?"
  → Tokenized: ["how", "does", "chunk", "work"]
  → Elasticsearch match query against content_ltks field
  → BM25 scoring
  → Returns chunks ranked by text relevance
```

### Score Fusion
```python
# vector_similarity_weight (default 0.3)
final_score = vw * vector_sim + (1 - vw) * text_sim

# Example:
# chunk_A: vec_sim=0.92, text_sim=0.45 → 0.3*0.92 + 0.7*0.45 = 0.591
# chunk_B: vec_sim=0.71, text_sim=0.88 → 0.3*0.71 + 0.7*0.88 = 0.829  ← wins
```

### Filtering Pipeline

```
1024 candidates
    │ similarity_threshold filter (default 0.2)
    ▼
~50-200 remaining
    │ doc_ids filter (if user specified documents)
    ▼
~20-50 remaining
    │ metadata filter (if configured)
    ▼
~10-30 remaining
    │ reranking (if enabled) — see [[04_Reranking]]
    ▼
top_n results (default 6-8)
```

## Advanced: Cross-Language Search

```python
# If cross_languages enabled:
# Original: "什么是RAGFlow？"
# Translated: ["What is RAGFlow?", "Qu'est-ce que RAGFlow?"]
# Each variant embedded and searched separately
# Results merged and deduplicated
```

## Connection to Next Step

After retrieval, results go to reranking (if configured). See [[04_Reranking]].
