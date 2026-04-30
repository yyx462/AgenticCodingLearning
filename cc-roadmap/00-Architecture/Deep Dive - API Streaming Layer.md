# Deep Dive: API Streaming Layer

> How Claude Code communicates with the Anthropic API — streaming, retries, model selection, caching, and error handling. This runs inside [[The Closed Loop - Input to Output Flow]] at Step 6b.

---

## Overview

The API layer is the bridge between the query loop and the Anthropic API. It handles:

```
query.ts calls deps.callModel()
      │
      ▼
┌──────────────────────────────────┐
│  src/services/api/claude.ts      │
│                                   │
│  1. Build request                │
│     - prependUserContext()       │
│     - appendSystemContext()      │
│     - addCacheBreakpoints()      │
│     - configureTaskBudget()      │
│                                   │
│  2. Stream request               │
│     - queryModelWithStreaming()  │
│     - SSE event processing       │
│     - Token-by-token yield       │
│                                   │
│  3. Handle errors                │
│     - withRetry() wrapper        │
│     - Model fallback             │
│     - Auth refresh               │
│                                   │
│  4. Track usage                  │
│     - accumulateUsage()          │
│     - updateUsage()              │
└──────────────────────────────────┘
```

---

## 1. Request Construction

### Context Injection

**File:** `src/utils/api.ts`

| Function | What it does |
|----------|-------------|
| `prependUserContext(messages, context)` | Injects a system reminder with environment info (OS, shell, git status) before messages |
| `appendSystemContext(systemPrompt, context)` | Appends key-value context pairs to the system prompt |

### Cache Configuration

**File:** `src/services/api/claude.ts`

| Function | What it does |
|----------|-------------|
| `getPromptCachingEnabled(model)` | Checks if prompt caching is enabled for the given model |
| `getCacheControl({scope?, querySource?})` | Returns cache control params: `{type: 'ephemeral', ttl?: '1h', scope?: 'global' \| 'org'}` |
| `addCacheBreakpoints(systemBlocks)` | Marks system prompt blocks for caching |

**Cache eligibility:**
- Enabled by default for eligible users (Claude Pro subscribers)
- 1-hour TTL for allowlisted query sources (`repl_main_thread*` patterns)
- Global disable via `DISABLE_PROMPT_CACHING` env var
- 3P Bedrock users can opt in via env var

### Task Budget

`configureTaskBudgetParams(taskBudget?, outputConfig?, betas?)` — merges token budget settings into the API request configuration.

---

## 2. Streaming Implementation

### Core Function: `queryModelWithStreaming()`

This is the main streaming function. It's an **async generator** that yields messages as they arrive from the API.

### SSE Event Processing

The Anthropic API uses Server-Sent Events (SSE). Events arrive in this order:

```
message_start          ← Message metadata, initial usage stats
    │
    ▼
content_block_start    ← New content block begins (text, tool_use, thinking)
    │
    ▼
content_block_delta    ← Incremental content (many of these per block)
    │                  ← Types: text_delta, input_json_delta, thinking_delta,
    │                      signature_delta, citations_delta
    ▼
content_block_stop     ← Content block complete → YIELD message to consumer
    │
    ▼
(message_delta)        ← Final usage stats, stop reason
    │
    ▼
message_stop           ← Stream complete
```

### What happens per event type

| Event | Processing |
|-------|-----------|
| `message_start` | Sets up partial message state, captures initial usage, records Time-To-First-Token (TTFT) |
| `content_block_start` | Initializes content block. Detects advisor tool blocks specially |
| `content_block_delta` | Appends incremental content: text → string concat, JSON → streaming parse, thinking → thinking buffer |
| `content_block_stop` | **Yields the complete message** to the query loop. Normalizes content format |
| `message_delta` | Updates final usage statistics and stop reason on the last message |
| `message_stop` | Final cleanup and resource release |

### Stream Stall Detection

If no event arrives for **30+ seconds**, the system logs a streaming stall warning. This helps diagnose API responsiveness issues.

### Resource Cleanup

`cleanupStream()` properly cancels HTTP responses and releases native resources to prevent memory leaks. Critical for long-running sessions.

---

## 3. Model Selection & Fallback

### Primary vs Fallback

| Model | Role | Special handling |
|-------|------|-----------------|
| **Opus** | Primary for subscribers | Capacity issues → fall back to Sonnet |
| **Sonnet** | Default for most users | Fallback for Opus overload |
| **Haiku** | Fast/cheap operations | Used by tool-use summary generation |

### Fallback Triggers

1. **529 Overloaded** — After `MAX_529_RETRIES` (3 consecutive 529s), Opus falls back to Sonnet
2. **Fast mode rate limit** — Falls back to standard speed on rate limits
3. **Context overflow** — Adjusts max_tokens and retries with smaller output budget

### Fast Mode Fallback

- Short retries (<20 seconds) preserve cache
- Long retries (>20 seconds) switch to standard speed
- Cooldown period prevents immediate retry after rate limit

### Non-Streaming Fallback

`queryModelWithoutStreaming()` — used as fallback when streaming fails. Handles context overflow by dynamically adjusting max_tokens (minimum 3000 output tokens).

---

## 4. Retry Mechanism

**File:** `src/services/api/withRetry.ts`

### Error Classification

| Category | HTTP Status | Retryable? |
|----------|------------|------------|
| Server overload | 529 | Yes (with model fallback) |
| Rate limit | 429 | Yes (exponential backoff) |
| Timeout | 408 | Yes |
| Lock conflict | 409 | Yes |
| Server error | 5xx | Yes |
| Auth error | 401, 403 | Yes (with token refresh) |
| Bad request | 400 | No |
| Not found | 404 | No |

### Retry Strategy

```
delay = baseDelay * 2^(attempt-1) + jitter
maxDelay = 32 seconds (configurable)
```

- **Exponential backoff with jitter** — prevents thundering herd
- **Persistent retry mode** — for unattended/ant sessions, higher backoff limits (5 minutes)
- **Keep-alive yields** — during long retries, yields progress messages so the UI stays responsive

### Special Retry Scenarios

| Scenario | Handling |
|----------|----------|
| Auth token expired | Auto-refresh OAuth tokens, clear credential caches, force new client |
| Stale connection | Detect `ECONNRESET`/`EPIPE`, disable keep-alive pooling, reconnect |
| Cloud provider auth | AWS Bedrock: clear credential cache; GCP Vertex: clear token cache |
| Context overflow | Parse "input length and max_tokens exceed context limit" error, reduce max_tokens, retry |

---

## 5. Error Classification System

**File:** `src/services/api/errors.ts`

`classifyAPIError()` categorizes errors into standardized types:

| Type | When | Recovery |
|------|------|----------|
| `api_timeout` | Request timeout | Retry |
| `connection_error` | General connection failure | Retry with new connection |
| `ssl_cert_error` | SSL/TLS issue | User action required |
| `rate_limit` | 429 | Exponential backoff |
| `server_overload` | 529 | Model fallback |
| `prompt_too_long` | Context window exceeded | Trigger [[Deep Dive - Pre-flight Pipeline\|reactive compact]] |
| `pdf_too_large` | PDF page limit | User action required |
| `image_too_large` | Image size/dimensions | User action required |
| `invalid_api_key` | Bad API key | User must `/login` |
| `authentication_failed` | General auth failure | Auto-refresh attempt |
| `token_revoked` | OAuth token revoked | Re-auth required |
| `server_error` | 5xx | Retry |
| `repeated_529` | Multiple overload errors | Model fallback |

---

## 6. Dependency Injection

**File:** `src/query/deps.ts`

The query loop uses dependency injection so tests can swap the API layer:

```typescript
export type QueryDeps = {
  callModel: typeof queryModelWithStreaming    // The streaming function
  microcompact: typeof microcompactMessages    // Microcompact function
  autocompact: typeof autoCompactIfNeeded      // Auto-compact function
  uuid: () => string                           // UUID generator
}
```

- **Production**: Uses real implementations
- **Tests**: Inject mock/stub implementations
- **Benefit**: Test the query loop without hitting the real API

---

## 7. Message Conversion Utilities

| Function | What it does |
|----------|-------------|
| `userMessageToMessageParam()` | Converts internal `UserMessage` to API-compatible format |
| `assistantMessageToMessageParam()` | Converts internal `AssistantMessage` to API format |
| `stripExcessMediaItems()` | Limits media items in messages (strips oldest first) |
| `getMaxOutputTokensForModel()` | Returns max output tokens for a given model |

---

## Cross-References

- Called by: [[The Closed Loop - Input to Output Flow]] (Step 6b)
- Pre-flight that prevents prompt-too-long: [[Deep Dive - Pre-flight Pipeline]]
- Tool execution that follows API response: [[Deep Dive - Tool Execution Pipeline]]
- Usage tracking consumed by: `src/cost-tracker.ts` (Step 9 in the Closed Loop)
- Deps injection defined in: `src/query/deps.ts`
