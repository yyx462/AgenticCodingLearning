# Deep Dive: Document Ingestion Pipeline

> Prerequisite for: [[00_Closed_Loop_Search]] — explains how chunks end up in the search index

## What Happens

Documents are uploaded, parsed, chunked, embedded, and stored in Elasticsearch/Infinity so they can be searched later.

## Pipeline Overview

```
File Upload → Parser Selection → Document Parsing → Chunking → Embedding → Storage
```

## Key Files

| File | Role |
|------|------|
| `api/apps/restful_apis/file_api.py` | File upload endpoint |
| `rag/app/naive.py` | Main chunking logic |
| `rag/svr/task_executor.py` | Task orchestration (parse → chunk → embed → store) |
| `rag/llm/embedding_model.py` | Vector embedding |
| `deepdoc/parser/` | Format-specific parsers |

## Step 1: File Upload

```python
# POST /api/files
# File stored in MinIO/S3, metadata in MySQL

# File record:
{
    "id": "file_abc123",
    "parent_id": "folder_xyz",
    "tenant_id": "tenant_456",
    "location": "/minio/tenant_456/document.pdf",
    "type": "pdf",          # auto-detected
    "size": 2048576         # bytes
}
```

## Step 2: Document Creation & Parser Selection

When a file is linked to a knowledge base:

```python
# File → Document conversion
doc = Document.create(
    kb_id="kb_789",
    file_id="file_abc123",
    parser_id="naive",      # Selected based on file type
    # pdf → "naive" or "resume" or "paper" or "book" or "laws" or "manual" or "qa"
    # docx → "naive"
    # txt → "naive"
    # csv/excel → "table"
    # md → "naive"
)

# Parser config includes:
parser_config = {
    "chunk_token_num": 512,     # max tokens per chunk
    "delimiter": "\n!?。；！？", # text split delimiters
    "html4excel": False,
    "layout_recognize": "DeepDOC",  # or "Docling", "MinerU", "Plain Text"
    "raptor": {"use_raptor": False}  # recursive abstractive processing
}
```

## Step 3: Parsing (`deepdoc/`)

Different parsers handle different formats:

### PDF Parsing (DeepDOC)

```python
# deepdoc/parser/pdf_parser.py
class Pdf:
    def __call__(self, filename, from_page=0, to_page=100000):
        # 1. OCR — extract text from images
        #    Supports: Tesseract, PaddleOCR
        #
        # 2. Layout Recognition — identify structure
        #    Detects: text blocks, tables, figures, headers, footers
        #    Model: layoutlmv3 or similar
        #
        # 3. Table Extraction — structured data from tables
        #    Returns HTML tables from detected table regions
        #
        # 4. Image Handling — extract and store images
        #    Images stored separately, referenced in chunks
```

### Example: PDF Parse Output

```
Input: product_manual.pdf (10 pages)

Page 1:
  - Layout: [title "Product Manual"], [text "Introduction..."]
  - OCR: (if scanned) extracted text from image regions

Page 3:
  - Layout: [table "Specifications"], [text "The table shows..."]
  - Table: "<table><tr><td>Feature</td><td>Value</td></tr>...</table>"

Output sections:
[
    {"type": "text", "page": 1, "content": "Product Manual\nIntroduction to..."},
    {"type": "text", "page": 2, "content": "Getting Started\nFirst, install..."},
    {"type": "table", "page": 3, "content": "<table>...</table>", "html": "<table>...</table>"},
    {"type": "image", "page": 4, "content": "[image: architecture_diagram.png]"},
]
```

## Step 4: Chunking (`rag/app/naive.py`)

The `chunk()` function splits parsed content into searchable segments:

```python
def chunk(filename, binary, from_page=0, to_page=MAXIMUM, lang="Chinese", **kwargs):
    """
    Returns: list of {
        "content_with_weight": str,    # The chunk text
        "content_ltks": str,           # Tokenized version for search
        "image": Optional[bytes],      # Associated image
        "position_int": list,          # Page + bbox for citation
        "doc_id": str,
    }
    """
```

### Chunking Algorithm (Naive Parser)

```
1. Split text by delimiters (configurable: \n ! ? 。 ；)
   → segments: ["Paragraph 1...", "Paragraph 2...", ...]

2. Merge segments up to chunk_token_num (default 512 tokens)
   → Accumulate segments until token limit reached
   → If adding next segment exceeds limit → flush current chunk

3. Handle special content:
   → Tables: kept as single chunk (not split)
   → Images: chunk includes surrounding text context
   → Headers: prepended to following text

4. Track positions:
   → Each chunk records which page(s) and bounding boxes it came from
   → Enables PDF citation highlighting later
```

### Example: Chunking

```
Input text (2 pages, 2000 tokens total):
"Introduction. RAGFlow is a RAG engine. It supports document understanding.
 Getting Started. First install the dependencies. Then configure the database.
 Configuration. The main config file is docker/.env. Set DOC_ENGINE to
 elasticsearch or infinity. Features include hybrid search, chunking, and
 LLM integration."

With chunk_token_num=100, delimiter=". ":

Chunk 1 (95 tokens):
  "Introduction. RAGFlow is a RAG engine. It supports document understanding."
  position: [[1, 0, 720, 100, 300]]  (page 1, bbox)

Chunk 2 (88 tokens):
  "Getting Started. First install the dependencies. Then configure the database."
  position: [[1, 0, 720, 310, 500]]

Chunk 3 (92 tokens):
  "Configuration. The main config file is docker/.env. Set DOC_ENGINE to
   elasticsearch or infinity."
  position: [[2, 0, 720, 100, 280]]

Chunk 4 (75 tokens):
  "Features include hybrid search, chunking, and LLM integration."
  position: [[2, 0, 720, 290, 400]]
```

## Step 5: Embedding (`rag/svr/task_executor.py`)

```python
async def embedding(docs, mdl, parser_config=None, callback=None):
    """
    Embed all chunks using the configured model.

    Batch processing:
    - texts split into batches of model.batch_size (typically 16)
    - Each batch sent to embedding API
    - Results concatenated
    """
    texts = [d["content_with_weight"] for d in docs]

    # Batch embed
    embeddings, total_tokens = mdl.encode(texts)
    # embeddings: np.array shape (num_chunks, embedding_dim)
    # e.g., (50, 1536) for 50 chunks with OpenAI ada-002

    for i, doc in enumerate(docs):
        doc[f"q_{embeddings.shape[1]}_vec"] = embeddings[i].tolist()
```

### Supported Embedding Models

| Model | Dimensions | Batch Size | Token Limit |
|-------|-----------|------------|-------------|
| OpenAI text-embedding-ada-002 | 1536 | 16 | 8191 |
| OpenAI text-embedding-3-small | 1536 | 16 | 8191 |
| BAAI/bge-m3 | 1024 | 4 | 8192 |
| Qwen text_embedding_v2 | 1024 | 4 | 2048 |
| Jina jina-embeddings-v3 | 1024 | 4 | 8192 |

## Step 6: Storage

```python
async def insert_chunks(task_id, tenant_id, dataset_id, chunks, callback):
    """
    Bulk insert chunks into Elasticsearch or Infinity.

    Index name: ragflow_{tenant_id}
    """
    # Each chunk stored as:
    {
        "id": "chunk_uuid",
        "doc_id": "doc_456",
        "kb_id": "kb_789",
        "content_with_weight": "RAGFlow is a RAG engine...",
        "content_ltks": "ragflow is a rag engine",
        "docnm_kwd": "product_manual.pdf",
        "q_1536_vec": [0.012, -0.034, 0.078, ...],  # embedding vector
        "position_int": [[1, 0, 720, 100, 300]],
        "create_timestamp_flt": 1714000000.0,
        "tag_kwd": ["rag", "search"]
    }

    # Bulk insert
    await store.insert_chunks(index_name, chunks)
```

## Task Orchestration (`rag/svr/task_executor.py`)

```python
async def do_handle_task(task):
    """Main task processor — runs for each document."""

    # 1. Parse document → get sections
    chunks = await build_chunks(task, progress_callback)

    # 2. Build chunk objects with metadata
    docs = []
    for i, chunk in enumerate(chunks):
        docs.append({
            "id": uuid4(),
            "doc_id": task.doc_id,
            "kb_id": task.kb_id,
            "content_with_weight": chunk["content_with_weight"],
            "position_int": chunk.get("position_int", []),
        })

    # 3. Embed all chunks
    await embedding(docs, embd_mdl, parser_config)

    # 4. Store in search index
    await insert_chunks(task.id, task.tenant_id, task.dataset_id, docs)

    # 5. Update document status
    await DocumentService.update_by_id(task.doc_id, {"progress": 1.0})
```

## End-to-End Example

```
Upload: "api_docs.pdf" (5MB, 50 pages)
    │
    ▼ Parse (DeepDOC): 50 pages → 120 sections
    │   - 95 text sections
    │   - 15 tables
    │   - 10 images
    │
    ▼ Chunk (naive, 512 tokens): 120 sections → 87 chunks
    │   - Each chunk: text + position + doc metadata
    │
    ▼ Embed (OpenAI ada-002): 87 chunks → 87 × 1536-dim vectors
    │   - 6 batches of 16, last batch of 7
    │   - Total: ~44,000 tokens embedded
    │
    ▼ Store (Elasticsearch): 87 documents inserted
    │   - Index: ragflow_tenant_456
    │   - Ready for hybrid search
    │
    Total time: ~2-5 minutes for a 50-page PDF
```

Back to [[00_Closed_Loop_Search]].
