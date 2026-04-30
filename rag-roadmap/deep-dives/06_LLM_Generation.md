# Deep Dive: LLM Answer Generation

> Part of: [[00_Closed_Loop_Search]] — Step 7

## What Happens

The LLM (GPT-4, Claude, etc.) receives the system prompt with injected context and generates a streaming answer with citation markers.

## Key File: `rag/llm/chat_model.py`

## LLM Architecture

```
All LLM providers use OpenAI-compatible API
    │
    ├── OpenAI (GPT-4, GPT-3.5)
    ├── Anthropic (Claude) — via OpenAI-compatible wrapper
    ├── Local models (Ollama, vLLM)
    ├── ZhipuAI (GLM)
    ├── Qwen (Tongyi)
    └── Any OpenAI-compatible endpoint
```

## `LLMBundle` — Tenant-Aware Wrapper

```python
class LLMBundle:
    """Wraps LLM with tenant-specific configuration.
    Handles model selection, API keys, and parameter overrides."""

    def __init__(self, tenant_id, llm_type):
        # Loads tenant's configured model, API key, base_url
        self.max_tokens = model_config.max_tokens
        self.llm_type = llm_type  # chat, embedding, rerank, tts
```

## Streaming Generation

```python
# From chat_model.py Base class
async def async_chat_streamly_delta(self, system, history, gen_conf={}):
    """
    Streams answer tokens one by one.

    Args:
        system: System prompt with injected context
        history: Previous conversation messages
        gen_conf: {temperature: 0.7, top_p: 0.9, max_tokens: 2048}

    Yields:
        delta tokens as they arrive
    """
    gen_conf = self._clean_conf(gen_conf)  # Remove None values

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.extend(history)

    async for delta_ans, total_tokens in self._async_chat_streamly(
        messages, gen_conf
    ):
        yield delta_ans

    yield total_tokens  # Final yield has total token count
```

## Error Handling & Retry

```python
async def _async_chat_streamly(self, messages, gen_conf, max_retries=5):
    for attempt in range(max_retries):
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                **gen_conf
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, 0
            yield "", total_tokens
            return

        except Exception as e:
            error_type = self._classify_error(e)
            # Rate limit → wait and retry
            # Auth error → raise immediately
            # Timeout → retry with backoff
            delay = self.base_delay * (2 ** attempt)
            await asyncio.sleep(delay)

    raise LLMError("Max retries exceeded")
```

### Error Classification

```python
def _classify_error(self, error):
    """Maps API errors to retry strategies."""
    if "rate_limit" in str(error).lower():
        return "rate_limit"       # Retry with backoff
    if "authentication" in str(error).lower():
        return "auth"             # Fail immediately
    if "timeout" in str(error).lower():
        return "timeout"          # Retry
    if "context_length" in str(error).lower():
        return "context_overflow" # Reduce context and retry
    return "unknown"              # Retry with backoff
```

## Citation Injection

The LLM prompt instructs it to mark which chunks it used:

```python
# System prompt includes citation instruction:
"...When using knowledge base content, mark citations as ##N$$ where N is the chunk index..."

# LLM output:
# "RAGFlow supports hybrid search##0$$. The system uses both vector and keyword matching##1$$."

# Post-processing replaces markers:
# "RAGFlow supports hybrid search [1]. The system uses both vector and keyword matching [2]."
```

## Example: Full Generation

```
Input to LLM:
  System: "You are an intelligent assistant...
           -----knowledge-----
           ------
           RAGFlow uses DeepDOC for PDF parsing...
           ------
           Hybrid search combines vector and keyword matching...
           -----"

  History: [
    {"role": "user", "content": "What search methods does RAGFlow use?"}
  ]

LLM Output (streamed):
  "RAGFlow"     → SSE event: {"answer": "RAGFlow"}
  " supports"   → SSE event: {"answer": " supports"}
  " hybrid"     → SSE event: {"answer": " hybrid"}
  " search##0$$"→ SSE event: {"answer": " search##0$$"}
  ", which"     → SSE event: {"answer": ", which"}
  ...

Final answer (after citation processing):
  "RAGFlow supports hybrid search [1], which combines vector similarity
   with keyword matching [1] for optimal retrieval quality."
```

## Connection to Next Step

Generated tokens stream back to the frontend via SSE. See [[07_Response_Streaming]].
