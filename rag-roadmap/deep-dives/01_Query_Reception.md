# Deep Dive: Query Reception (Frontend → API)

> Part of: [[00_Closed_Loop_Search]] — Step 1

## What Happens

User types a message in the chat UI. Frontend packages it as an SSE (Server-Sent Events) request and streams the response token-by-token.

## Key Files

| File | Role |
|------|------|
| `web/src/hooks/use-send-message.ts` | Core hook: builds message, sends SSE, handles response |
| `web/src/components/floating-chat-widget.tsx` | Chat UI component |
| `web/src/utils/api.ts` | API endpoint definitions |
| `api/apps/restful_apis/chat_api.py` | Backend: receives request, authenticates, delegates |

## Frontend Flow

```
User types query
    │
    ▼
useSendMessageBySSE()
    │  builds message object with uuid
    │  sets up EventSource connection
    ▼
POST /api/v1/chat/completions
    Headers: { Authorization: "Bearer <jwt>" }
    Body: {
        messages: [{ role: "user", content: "What is RAGFlow?" }],
        stream: true,
        conversation_id: "conv_123"   // existing or null for new
    }
    │
    ▼
EventSource receives SSE events
    data: {"code": 0, "data": {"answer": "RAG"}}
    data: {"code": 0, "data": {"answer": "Flow is"}}
    data: {"code": 0, "data": {"answer": " a RAG engine...", "reference": {...}}}
    │
    ▼
Frontend renders tokens incrementally
Source citations rendered as clickable chips
```

## Backend Reception

`chat_api.py` → `session_completion()`:

1. **Auth check**: Validates JWT token, resolves `current_user`
2. **Session resolution**: Loads or creates conversation record
3. **Config loading**: Gets dialog configuration (knowledge bases, LLM, thresholds)
4. **Delegation**: Calls `async_chat()` from `dialog_service.py`

```python
# Simplified from chat_api.py
@token_required
async def session_completion(conversation_id):
    req = await request.get_json()
    stream_mode = req.pop("stream", True)

    dia = await ConversationService.get_by_id(conversation_id)
    # dia contains: kb_ids, llm_id, prompt_config, similarity thresholds

    if stream_mode:
        async for ans in async_chat(dia, msg, True, **req):
            yield "data:" + json.dumps({"code": 0, "data": ans}) + "\n\n"
```

## Example: Full Request/Response

**Request:**
```http
POST /api/v1/chat/completions HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "messages": [{"role": "user", "content": "Explain chunking strategies"}],
    "stream": true,
    "conversation_id": "conv_abc123"
}
```

**SSE Response:**
```
data: {"code": 0, "data": {"answer": "RAGFlow", "reference": {}}}

data: {"code": 0, "data": {"answer": " supports multiple", "reference": {}}}

data: {"code": 0, "data": {"answer": " chunking strategies...", "reference": {
    "total": 3,
    "chunks": [
        {"chunk_id": "c1", "content_ltks": "chunking token...", "docnm_kwd": "docs.md"}
    ]
}}}
```

## Connection to Next Step

After auth and config resolution, the query moves to **query processing** — embedding generation and retrieval. See [[02_Query_Processing]].
