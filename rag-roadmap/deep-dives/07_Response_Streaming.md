# Deep Dive: Response Streaming (SSE)

> Part of: [[00_Closed_Loop_Search]] — Step 8

## What Happens

LLM tokens stream from backend to frontend via Server-Sent Events (SSE). The frontend renders tokens incrementally and displays source citations as interactive elements.

## Key Files

| File | Role |
|------|------|
| `api/apps/restful_apis/chat_api.py` | SSE response generator |
| `web/src/hooks/use-send-message.ts` | Frontend SSE consumer |
| `web/src/utils/chat.ts` | Message formatting utilities |

## SSE Protocol

Backend sends events in this format:

```
data: {"code": 0, "data": {"answer": "RAG", "reference": {}}}\n\n
data: {"code": 0, "data": {"answer": "Flow ", "reference": {}}}\n\n
data: {"code": 0, "data": {"answer": "supports ", "reference": {}}}\n\n
...
data: {"code": 0, "data": {"answer": "", "reference": {"total": 3, "chunks": [...]}}}\n\n
```

## Backend SSE Generation

```python
# From chat_api.py
@token_required
async def session_completion():
    req = await request.get_json()
    stream_mode = req.pop("stream", True)

    if stream_mode:
        async def _stream():
            async for ans in async_chat(dia, msg, True, **req):
                ans = _format_answer(ans)
                yield "data:" + json.dumps({
                    "code": 0,
                    "data": ans
                }, ensure_ascii=False) + "\n\n"

        return Response(_stream(), content_type="text/event-stream")
```

## Frontend SSE Consumption

```typescript
// Simplified from use-send-message.ts
function useSendMessageBySSE() {
    const sendMessage = async (message: string) => {
        const response = await fetch('/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                messages: [{ role: 'user', content: message }],
                stream: true,
                conversation_id: conversationId
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split('\n');

            for (const line of lines) {
                if (line.startsWith('data:')) {
                    const data = JSON.parse(line.slice(5));
                    if (data.code === 0) {
                        // Append token to displayed answer
                        appendAnswer(data.data.answer);

                        // Store reference info
                        if (data.data.reference?.total > 0) {
                            setReference(data.data.reference);
                        }
                    }
                }
            }
        }
    };
}
```

## Citation Display

```typescript
// Citation references are rendered as interactive chips
// User can click to see source chunk and highlight in original PDF

interface Reference {
    total: number;
    chunks: Array<{
        chunk_id: string;
        content_ltks: string;
        content_with_weight: string;
        doc_id: string;
        docnm_kwd: string;      // Document name
        kb_id: string;
        similarity: number;
        position_int: number[][]; // For PDF highlight
    }>;
    doc_aggs: Array<{
        doc_id: string;
        doc_name: string;
        count: number;          // How many chunks from this doc
    }>;
}
```

## Latency Breakdown (Typical)

```
User sends query                    0ms
    │
    ▼ API receives & authenticates   ~50ms
    │
    ▼ Embedding generation           ~200ms
    │
    ▼ Hybrid search (ES)             ~100ms
    │
    ▼ Reranking (if enabled)         ~300ms
    │
    ▼ First token from LLM           ~500ms  ← Time-to-first-token
    │
    ▼ Full answer streamed           ~2-5s   (depends on length)
    │
    Total: ~1-2s to first token, 3-7s for complete answer
```

## Connection to Previous Steps

This is the final step in the closed loop. The user now sees the answer and can:
- Ask follow-up questions (loop restarts)
- Click citations to view source documents
- Review the conversation history

Back to [[00_Closed_Loop_Search]].
