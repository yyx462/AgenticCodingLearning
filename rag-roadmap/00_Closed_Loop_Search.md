# Closed Loop: What Happens When You Search

> [!info] TL;DR
> User types query → Frontend sends SSE request → API receives query → Embeds query vector → Hybrid search (vector + keyword) against Elasticsearch/Infinity → Reranks results → Builds context from top chunks → LLM generates answer with citations → Streams response back via SSE → Frontend renders with source links.

---

## The Full Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER TYPES QUERY                         │
│                    "What is RAGFlow?"                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. FRONTEND — SSE Request                                      │
│  web/src/hooks/use-send-message.ts                              │
│  POST /api/v1/chat/completions (stream: true)                   │
│  Deep dive → [[01_Query_Reception]]                             │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. API LAYER — Chat API                                        │
│  api/apps/restful_apis/chat_api.py                              │
│  Authenticates user, resolves dialog session, delegates         │
│  to async_chat()                                                │
│  Deep dive → [[02_Query_Processing]]                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. QUERY EMBEDDING                                             │
│  rag/llm/embedding_model.py                                     │
│  Query text → 1536-dim vector (e.g. OpenAI text-embedding)     │
│  Optional: cross-language translation before embedding          │
│  Deep dive → [[03_Hybrid_Search]]                               │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. HYBRID SEARCH                                               │
│  rag/nlp/search.py → Dealer.retrieval()                        │
│  Two parallel searches:                                         │
│    • Vector similarity: cosine(q_vec, chunk_vec)                │
│    • Keyword match: BM25-style full-text search                 │
│  Results merged with weighted score:                            │
│    score = vector_weight * vec_sim + (1-vw) * text_sim          │
│  Deep dive → [[03_Hybrid_Search]]                               │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. RERANKING (optional but recommended)                        │
│  rag/llm/rerank_model.py                                       │
│  Top-N candidates sent to reranker (Jina, Cohere, etc.)        │
│  Reranker produces relevance scores → re-sort results           │
│  Deep dive → [[04_Reranking]]                                   │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. CONTEXT BUILDING                                            │
│  api/db/services/dialog_service.py → async_chat()               │
│  Top-K chunks formatted as:                                     │
│    "------\nchunk_text_1\n------\nchunk_text_2\n------"        │
│  Metadata filters applied. Citation info preserved.             │
│  Deep dive → [[05_Context_Building]]                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. LLM GENERATION                                              │
│  rag/llm/chat_model.py                                          │
│  System prompt + retrieved context + user query → LLM          │
│  Streaming tokens via OpenAI-compatible API                     │
│  Citation markers injected into response text                   │
│  Deep dive → [[06_LLM_Generation]]                              │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. SSE STREAMING RESPONSE                                      │
│  Frontend receives SSE events, renders tokens incrementally     │
│  Source citations displayed as clickable links                  │
│  Deep dive → [[07_Response_Streaming]]                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Concrete Example

**User asks**: `"How does RAGFlow handle PDF parsing?"`

| Step | What happens | Key data |
|------|-------------|----------|
| 1. Frontend | `useSendMessageBySSE()` posts to `/api/v1/chat/completions` | `{messages: [{role: "user", content: "How does RAGFlow handle PDF parsing?"}], stream: true}` |
| 2. API | `session_completion()` validates auth, resolves dialog config | Dialog has `kb_ids: ["kb_abc"]`, `llm_id: "gpt-4"`, `similarity_threshold: 0.2` |
| 3. Embed | Query text → embedding model → `[0.0123, -0.0456, ...]` (1536 dims) | Uses configured embedding model for the knowledge base |
| 4. Search | Vector search finds chunks with similar embeddings. Keyword search finds chunks containing "PDF", "parsing", "RAGFlow" | Returns ~1024 candidates, scored by hybrid formula |
| 5. Rerank | Top 64 candidates sent to reranker model | Reranker returns relevance scores, results re-sorted |
| 6. Context | Top 6-8 chunks assembled with `------` separators | `"------\nRAGFlow uses DeepDOC for PDF parsing...\n------\nThe PDF parser supports OCR..."` |
| 7. Generate | System prompt + context + query sent to GPT-4 | Streams back: `"RAGFlow uses its DeepDOC engine for PDF parsing, which includes OCR capabilities..."` |
| 8. Display | Frontend renders streaming tokens, shows source citations | User sees answer with clickable source links |

---

## Where Do the Chunks Come From?

The search only works because documents were previously ingested. That pipeline runs **before** any search:

```
File Upload → Parser (deepdoc) → Chunker (naive.py) → Embedding → Store in ES/Infinity
```

See [[08_Document_Ingestion]] for the full ingestion deep dive.

---

## Agent Mode Alternative

Instead of the simple dialog flow, RAGFlow also supports an **Agent** mode where queries flow through a custom DAG of components (retrieval, LLM, categorization, etc.).

See [[09_Agent_Workflow]] for details.
