# Deep Dive: Context Building

> Part of: [[00_Closed_Loop_Search]] — Step 6

## What Happens

Top-K retrieved chunks are assembled into a single context string that gets injected into the LLM prompt. This is where raw search results become usable knowledge.

## Key File: `api/db/services/dialog_service.py`

## Context Assembly

After `retrieval()` returns `kbinfos`, the dialog service builds the knowledge string:

```python
# Simplified from dialog_service.py
kbinfos = await retrievaler.retrieval(question, embd_mdl, ...)

# Build knowledge context
knowledges = ""
for i, chunk in enumerate(kbinfos["chunks"][:top_n]):
    knowledges += f"""
------
{chunk["content_with_weight"]}
"""

# knowledges now looks like:
# ------
# RAGFlow uses DeepDOC for PDF parsing with OCR support...
# ------
# The naive parser splits text by configurable delimiters and token limits...
# ------
# Chunking strategies include token-based and delimiter-based approaches...
```

## System Prompt Construction

The context is injected into the system prompt using configurable templates:

```python
# Default prompt structure
system_prompt = f"""You are an intelligent assistant. Please summarize the content of the knowledge base to answer the question. Please list the data in the knowledge base and answer in detail. When all knowledge base content is irrelevant to the question, your answer must include the sentence "The answer you are looking for is not found in the knowledge base!" Answers need to consider chat records/context.

-----knowledge-----
{knowledges}
-----"""

# Full message sequence sent to LLM:
messages = [
    {"role": "system", "content": system_prompt},
    # ... chat history ...
    {"role": "user", "content": question}
]
```

## Citation Tracking

Each chunk carries metadata for citation:

```python
# Each chunk in kbinfos has:
{
    "chunk_id": "chunk_abc123",
    "content_with_weight": "RAGFlow supports hybrid search...",
    "content_ltks": "ragflow support hybrid search",  # tokenized for search
    "doc_id": "doc_456",
    "docnm_kwd": "user_guide.pdf",          # source document name
    "kb_id": "kb_789",
    "similarity": 0.89,                     # final score
    "position_int": [[1, 0, 720, 40, 560]], # page 1, bbox for PDF highlight
    "tag_kwd": ["rag", "search"],           # optional tags
}
```

After LLM generates answer, citations are matched:

```python
# Citation insertion logic (simplified)
# LLM response contains markers like "##0$$" "##1$$"
# These are replaced with actual source references:
answer = answer.replace("##0$$", "")
# And the reference map is preserved:
reference = {
    0: {"chunk_id": "chunk_abc", "doc_name": "user_guide.pdf", "page": 1}
}
```

## Metadata Filtering

Before context building, metadata filters can narrow results:

```python
# From agent/tools/retrieval.py
if self._param.meta_data_filter != {}:
    doc_ids = await apply_meta_data_filter(
        self._param.meta_data_filter,
        metas,          # available document metadata
        query,
        chat_mdl,       # LLM for AI-based filtering
        doc_ids,
        _resolve_manual_filter  # for manual filters
    )
```

### Example: Manual Filter

```python
meta_data_filter = {
    "field": "department",
    "operator": "in",
    "value": ["engineering", "product"]
}

# Only returns chunks from documents tagged with
# department: engineering OR department: product
```

### Example: AI-Based Filter

```python
meta_data_filter = {
    "method": "auto",
    "description": "Filter for documents about frontend development"
}

# LLM analyzes query and available metadata to decide which docs are relevant
```

## Context Window Management

```python
# Token budget management (simplified)
max_context_tokens = llm.max_tokens - answer_budget  # e.g., 4096 - 1024 = 3072

total_tokens = 0
selected_chunks = []
for chunk in sorted_chunks:  # sorted by similarity desc
    chunk_tokens = count_tokens(chunk["content_with_weight"])
    if total_tokens + chunk_tokens > max_context_tokens:
        break
    selected_chunks.append(chunk)
    total_tokens += chunk_tokens

# Only highest-scoring chunks that fit in context window are included
```

## Connection to Next Step

Context string + chat history → sent to LLM for answer generation. See [[06_LLM_Generation]].
