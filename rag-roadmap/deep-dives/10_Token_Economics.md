# Deep Dive: Token Economics — "Harry Kane" Query Walkthrough

> Prerequisite: [[00_Closed_Loop_Search]]
> See also: [[02_Query_Processing]], [[03_Hybrid_Search]], [[04_Reranking]], [[06_LLM_Generation]]

## The Core Question

When a user types "Harry Kane", how many LLM API calls happen? What costs tokens? What's free?

---

## TL;DR: API Call Inventory

| # | API Call | When | Token Cost | Required? |
|---|----------|------|------------|-----------|
| 1 | **Full question refinement** | Multi-turn conversations with `refine_multiturn` enabled | ~200-500 tokens (chat LLM) | No — only if multi-turn + enabled |
| 2 | **Cross-language translation** | `cross_languages` config set | ~100-300 tokens (chat LLM) | No — only if enabled |
| 3 | **Metadata filter** (AI mode) | `meta_data_filter` with auto method | ~200 tokens (chat LLM) | No — only if AI filtering enabled |
| 4 | **Keyword extraction** | `keyword` config set | ~150 tokens (chat LLM) | No — only if enabled |
| 5 | **Query embedding** | Always (if KB retrieval) | ~2 tokens (embedding API) | Yes — every retrieval query |
| 6 | **Reranking** | `rerank_mdl` configured | query tokens + all chunk tokens | No — only if reranker configured |
| 7 | **TOC enhancement** | `toc_enhance` config set | ~300-500 tokens (chat LLM) | No — only if enabled |
| 8 | **Knowledge graph retrieval** | `use_kg` config set | ~200-400 tokens (chat LLM) | No — only if enabled |
| 9 | **Final LLM generation** | Always | system prompt + context + history + response (1000-5000+ tokens) | Yes — every query |
| 10 | **Citation insertion** | Auto-citation when LLM didn't cite | ~2 tokens (embedding) per chunk | No — only if LLM didn't produce citations |

**Minimum for a simple "Harry Kane" query: 2 API calls (embed + generate)**
**Maximum with all features: 6-8 API calls**

---

## Walkthrough: "Harry Kane" — Default Config

Assumptions:
- First message (no history), `refine_multiturn` off
- No `cross_languages`, no `keyword` extraction, no `toc_enhance`
- Reranker enabled (Jina)
- Knowledge base has 50 chunks about football
- Chat model: GPT-4, Embedding: text-embedding-ada-002

```
User types "Harry Kane"
         │
         │  ┌─────────────────────────────────────────┐
         │  │ PHASE 1: QUERY PREPROCESSING             │
         │  │ Token cost: 0 (no LLM calls)             │
         │  └─────────────────────────────────────────┘
         │
         ▼
    Step 1.1: Refine multi-turn question?
         │  NOT triggered (first message, no history)
         │  Condition: len(messages) > 1 AND refine_multiturn=True
         │  If triggered → 1 Chat LLM call, ~300 tokens
         │
         ▼
    Step 1.2: Cross-language translation?
         │  NOT triggered (not configured)
         │  If triggered → 1 Chat LLM call, ~200 tokens
         │  Example output: "Harry Kane===Harry Kane===Harry Kane"
         │  (original + translated variants joined by "===")
         │
         ▼
    Step 1.3: Metadata filtering (AI)?
         │  NOT triggered
         │  If triggered → 1 Chat LLM call to decide which docs match
         │
         ▼
    Step 1.4: Keyword extraction?
         │  NOT triggered (not configured)
         │  If triggered → 1 Chat LLM call, ~150 tokens
         │  Output appended to query: "Harry Kane, football, striker, Tottenham"
         │
         ▼  Query is still just "Harry Kane"
```

```
         │  ┌─────────────────────────────────────────┐
         │  │ PHASE 2: RETRIEVAL                       │
         │  │ Token cost: embedding + reranking        │
         │  └─────────────────────────────────────────┘
         │
         ▼
    Step 2.1: Query Embedding ← FIRST API CALL (Embedding)
         │
         │  Input:  "Harry Kane"
         │  Tokens: ~2 tokens (BPE: ["Harry", " Kane"])
         │  API:    POST to OpenAI /embeddings
         │  Cost:   2 embedding tokens ≈ $0.0000001
         │
         │  Output: [0.0234, -0.0156, 0.0891, ...]  (1536 floats)
         │
         ▼
    Step 2.2: Hybrid Search ← NO TOKEN COST
         │
         │  Two parallel queries against Elasticsearch:
         │
         │  (a) Vector search (kNN):
         │      Query: {knn: {field: "q_1536_vec", query_vector: [...], k: 1024}}
         │      Cost: 0 tokens — this is a database operation
         │      Returns: chunks sorted by cosine similarity
         │
         │  (b) Keyword search (BM25):
         │      Query: {match: {content_ltks: "Harry Kane"}}
         │      Cost: 0 tokens — database full-text search
         │      Returns: chunks sorted by text relevance
         │
         │  Fusion:
         │    final_score = 0.3 * vector_sim + 0.7 * keyword_sim
         │    Cost: 0 tokens — arithmetic in Python
         │
         │  Result: ~1024 candidates, filtered by similarity_threshold=0.2
         │  After filtering: ~30-80 chunks remain
         │
         ▼
    Step 2.3: Reranking ← SECOND API CALL (Reranker)
         │
         │  Input:  query="Harry Kane", texts=[top 30-64 chunks]
         │  API:    POST to Jina/Cohere rerank endpoint
         │
         │  Token computation:
         │    query tokens:     2    ("Harry Kane")
         │    chunk tokens:     ~30 chunks × ~200 tokens/chunk = ~6,000 tokens
         │    ─────────────────────
         │    Total rerank:     ~6,002 tokens
         │
         │  Cost: ~6,002 rerank tokens ≈ $0.006 (Jina pricing)
         │
         │  Output: relevance_score for each chunk, re-sorted
         │
         ▼
    Step 2.4: Select top_n chunks
         │
         │  Top 6-8 chunks selected (configurable via dialog.top_n)
         │  Example chunks:
         │    1. "Harry Kane is an English professional footballer..."  (180 tokens)
         │    2. "Kane began his career at Tottenham Hotspur..."       (210 tokens)
         │    3. "In 2023, Kane transferred to Bayern Munich..."       (195 tokens)
         │    4. "Kane is the all-time top scorer for Tottenham..."    (165 tokens)
         │    5. "Harry Kane has scored 58 goals for England..."       (140 tokens)
         │    6. "Kane's playing style combines physicality..."        (175 tokens)
         │
         │  Total selected: ~1,065 tokens of chunk text
```

```
         │  ┌─────────────────────────────────────────┐
         │  │ PHASE 3: CONTEXT BUILDING                │
         │  │ Token cost: 0 (string operations only)   │
         │  └─────────────────────────────────────────┘
         │
         ▼
    Step 3.1: Format context
         │
         │  knowledges = "------
         │    Harry Kane is an English professional footballer...
         │    ------
         │    Kane began his career at Tottenham Hotspur...
         │    ------
         │    ...
         │    ------"
         │
         │  No API calls. Pure string formatting.
         │
         ▼
    Step 3.2: Build system prompt
         │
         │  system = "You are an intelligent assistant...
         │    -----knowledge-----
         │    ------
         │    [chunk 1 text]
         │    ------
         │    [chunk 2 text]
         │    ...
         │    -----
         │    When all knowledge base content is irrelevant...
         │    [citation instructions]"
         │
         │  Token count:
         │    Base prompt:      ~150 tokens
         │    Knowledge chunks: ~1,065 tokens
         │    Citation instruc: ~50 tokens
         │    ────────────────────
         │    System prompt:    ~1,265 tokens
         │
         ▼
    Step 3.3: Fit in context window
         │
         │  message_fit_in() truncates history if total exceeds max_tokens * 0.95
         │  For "Harry Kane" (first message, no history):
         │    msg = [system_prompt(1265), user_msg(2)] = 1,267 tokens — fits easily
```

```
         │  ┌─────────────────────────────────────────┐
         │  │ PHASE 4: LLM GENERATION                  │
         │  │ Token cost: input + output (Chat LLM)    │
         │  └─────────────────────────────────────────┘
         │
         ▼
    Step 4.1: Chat completion ← THIRD API CALL (Chat LLM)
         │
         │  Messages sent to GPT-4:
         │    [
         │      {role: "system",  content: "...1265 tokens..."},
         │      {role: "user",    content: "Harry Kane"}        ← 2 tokens
         │    ]
         │
         │  Input tokens:  1,267
         │  Output tokens: ~200-500 (typical answer)
         │
         │  Cost (GPT-4 pricing):
         │    Input:  1,267 × $0.03/1K = $0.038
         │    Output:   300 × $0.06/1K = $0.018
         │    ────────────────────────────────────
         │    Total: ~$0.056
         │
         │  Output (streamed):
         │    "Harry Kane##0$$ is an English professional footballer who
         │     plays as a striker for Bayern Munich##1$$ and captains the
         │     England national team##4$$. He is widely regarded as one
         │     of the best strikers in world football##3$$."
         │
         ▼
    Step 4.2: Citation processing ← MIGHT cost embedding tokens
         │
         │  If LLM produced citation markers (##0$$ etc.):
         │    → Parse markers, map to chunk indices, extract references
         │    → 0 tokens, pure string processing
         │
         │  If LLM did NOT produce citation markers:
         │    → insert_citations() embeds each chunk + answer text
         │    → Finds best chunk match for each sentence
         │    → Costs: ~6 embedding calls × ~200 tokens = ~1,200 embedding tokens
         │    → This is the AUTO-CITATION fallback
```

---

## Total Token Cost Summary

### Default Config ("Harry Kane", first message, reranker on)

| Phase | API Call | Token Type | Tokens | Cost (approx) |
|-------|----------|-----------|--------|---------------|
| Retrieval | Query embedding | Embedding | 2 | $0.0000001 |
| Retrieval | Reranking (30 chunks) | Rerank | ~6,002 | $0.006 |
| Generation | Chat completion input | Chat input | ~1,267 | $0.038 |
| Generation | Chat completion output | Chat output | ~300 | $0.018 |
| **Total** | **3 API calls** | | **~7,571** | **~$0.062** |

### Minimum Config (no reranker, no extras)

| Phase | API Call | Token Type | Tokens | Cost (approx) |
|-------|----------|-----------|--------|---------------|
| Retrieval | Query embedding | Embedding | 2 | $0.0000001 |
| Generation | Chat completion | Chat | ~1,567 | $0.056 |
| **Total** | **2 API calls** | | **~1,569** | **~$0.056** |

### Maximum Config (all features enabled, multi-turn)

| Phase | API Call | Tokens | Cost |
|-------|----------|--------|------|
| Preprocessing | Full question refinement (Chat) | ~400 | $0.036 |
| Preprocessing | Cross-language (Chat) | ~200 | $0.018 |
| Preprocessing | Keyword extraction (Chat) | ~150 | $0.014 |
| Retrieval | Query embedding (Embedding) | 2 | ~$0 |
| Retrieval | Reranking (Rerank) | ~6,000 | $0.006 |
| Retrieval | TOC enhancement (Chat) | ~400 | $0.036 |
| Retrieval | Knowledge graph (Chat) | ~300 | $0.027 |
| Generation | Chat completion (Chat) | ~1,567 | $0.056 |
| **Total** | **8 API calls** | **~9,019** | **~$0.193** |

---

## What Does NOT Cost Tokens

Many people assume everything in RAG is LLM-powered. Wrong:

| Operation | How it works | Token cost |
|-----------|-------------|------------|
| **Hybrid search** | Vector cosine similarity + BM25 text matching | **0 tokens** — database operations |
| **Score fusion** | Weighted arithmetic on scores | **0 tokens** — Python math |
| **Keyword tokenization** | `FulltextQueryer` tokenizes query into terms | **0 tokens** — rule-based tokenizer |
| **Context string formatting** | `"------\n".join(chunks)` | **0 tokens** — string concat |
| **Chunking during ingestion** | Delimiter-based text splitting | **0 tokens** — rule-based |
| **Similarity threshold filtering** | `if score > 0.2: keep` | **0 tokens** — comparison |
| **Pagination** | Slice array of results | **0 tokens** |
| **PDF layout recognition** | DeepDOC vision model | **0 LLM tokens** — uses its own model, not the chat LLM |

---

## Is Everything One-Shot?

**Yes, for default config.** The generation is a single LLM call:
```
[System prompt with context] + [Chat history] + [User query] → [Answer]
```

**Not one-shot when these features are enabled:**

| Feature | Extra LLM calls | Purpose |
|---------|----------------|---------|
| `refine_multiturn` | 1 before retrieval | Rewrites "who is he?" → "Who is Harry Kane?" using chat history |
| `cross_languages` | 1 before retrieval | Translates query to multiple languages for cross-lingual search |
| `keyword` | 1 before retrieval | Extracts keywords: "Harry Kane" → "Harry Kane, football, striker" |
| `toc_enhance` | 1 after retrieval | Uses LLM to pick relevant TOC sections |
| `use_kg` | 1 during retrieval | Knowledge graph query expansion |
| `reasoning` (Deep Research) | **Multiple** | Iterative research — retrieves → reflects → retrieves again |
| AI metadata filter | 1 before retrieval | LLM decides which docs match filter criteria |

The `reasoning` mode is the most expensive — it loops retrieval + LLM reflection multiple times before generating the final answer.

---

## Comparison: RAG vs Agentic Grep

### Agentic Grep (like Claude Code's Grep tool)

```
User: "Harry Kane"
    │
    ▼
grep "Harry Kane" across all files
    │  Token cost: 0 (no API calls)
    │  Returns: raw file matches
    │
    ▼
Agent (LLM) reads matches, decides if useful
    │  Token cost: input matches + output reasoning
    │
    ▼
Agent reads relevant files
    │  Token cost: file contents
    │
    ▼
Agent answers
    │  Token cost: answer generation
```

### Key Differences

| Aspect | RAG (RAGFlow) | Agentic Grep |
|--------|---------------|--------------|
| **Search method** | Vector similarity + BM25 fusion | Literal text match (regex) |
| **Semantic understanding** | Yes — "football striker" matches "Harry Kane" | No — only exact/near-exact matches |
| **Search cost** | Embedding API call + optional rerank | Free (local operation) |
| **Index required** | Yes — must pre-embed all documents | No — searches raw files |
| **Latency (search)** | ~300ms (network API + DB query) | ~50ms (local regex) |
| **Chunk quality** | Pre-processed, cleaned, positioned | Raw file content |
| **Handles typos** | Yes (vector similarity fuzzy-matches) | Only with explicit regex |
| **Cross-language** | Yes (embeddings are multilingual) | No |
| **Scalability** | Handles millions of chunks via ES | Slow on large codebases |
| **Token cost (search)** | ~6 tokens (embedding) + ~6,000 (rerank) | 0 |
| **Token cost (generation)** | ~1,500 input + ~300 output | Variable — agent reads full files |

### When Grep Wins

- Code search (exact symbol names, function signatures)
- Small document sets (<100 files)
- Need zero latency
- No embedding infrastructure

### When RAG Wins

- Natural language queries ("how does authentication work?")
- Large document sets (>1000 documents)
- Cross-language content
- Need semantic matching, not literal
- Pre-built knowledge bases with clean chunks

### The Hybrid Approach

RAGFlow actually uses **both**:
- Vector search = semantic understanding
- BM25 keyword search = exact matching (similar to grep)
- Fusion = best of both worlds

This is the whole point of "hybrid search" — you don't have to choose.

---

Back to [[00_Closed_Loop_Search]]
