# Deep Dive: Pre-flight Pipeline — Context Management

> How Claude Code manages context window limits before each API call. This runs inside [[The Closed Loop - Input to Output Flow]] at Step 6a.

---

## Overview

Before every API call, the query loop runs a "pre-flight" check. If the conversation is approaching the context window limit, one or more compaction strategies fire to shrink the message history. The strategies are ordered cheapest-to-most-expensive so the system tries the lightest fix first.

```
Messages growing...
      │
      ▼
┌─────────────────────────┐
│  1. Token Budget Check  │  ← Is user's token budget exhausted?
│     tokenBudget.ts      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  2. Snip Compact        │  ← Remove old verbose tool output
│     snipCompact.ts      │     (cheapest, no API call)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  3. Microcompact        │  ← Cache-editing compaction
│     (config gates)      │     (edits cached system prompt)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  4. Context Collapse    │  ← Archive old messages into summaries
│     contextCollapse/    │     (feature-gated)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  5. Auto-compact        │  ← Full conversation summary via API call
│     autoCompact.ts      │     (most expensive)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  6. Reactive Compact    │  ← Emergency compaction after prompt-too-long error
│     reactiveCompact.ts  │     (last resort)
└─────────────────────────┘
```

---

## 1. Token Budget Check

**File:** `src/query/tokenBudget.ts`

### Functions

| Function | Signature | What it does |
|----------|-----------|-------------|
| `createBudgetTracker()` | `() => BudgetTracker` | Creates a new tracker instance for tracking token usage across turns |
| `checkTokenBudget()` | `(tracker, usage) => TokenBudgetDecision` | Decides whether to continue or stop based on token consumption |

### How it works

- Tracks cumulative token usage across conversation turns
- **`COMPLETION_THRESHOLD = 0.9`** — if 90% of budget is used, considers stopping
- **`DIMINISHING_THRESHOLD = 500`** — if recent turns produced <500 tokens of progress, triggers "diminishing returns" stop
- Returns a `TokenBudgetDecision` telling the loop to continue or stop

### User-facing budget commands

**File:** `src/utils/tokenBudget.ts`

Users can set token budgets via natural language in their prompt:
- `"use 500k tokens"` or `"+500k"` — shorthand notation
- `"spend 1m tokens"` or `"+1m"` — verbose form
- Multipliers: `k` = 1,000 / `m` = 1,000,000 / `b` = 1,000,000,000

`getBudgetContinuationMessage()` generates progress messages showing percentage of budget consumed.

---

## 2. Snip Compact

**File:** `src/services/compact/snipCompact.ts`

### What it does

The cheapest compaction strategy. Removes old, verbose tool output from the conversation history without making any API call. Tool results that are large and old get "snipped" — replaced with a note that the output was removed.

### When it runs

Every pre-flight cycle, before any other compaction. It's essentially free (no API tokens spent).

### Key logic

- Scans message history for old tool result blocks
- Identifies results that exceed a size threshold
- Replaces them with a placeholder like `[output removed for context management]`
- Preserves the most recent tool results (they're likely still relevant)

---

## 3. Microcompact

**File:** Gated by `src/query/config.ts` (feature flags)

### What it does

Edits the cached system prompt entries to reduce their size. Rather than re-summarizing the conversation, it modifies the cache breakpoints to exclude old cached content.

### When it runs

Controlled by feature gates in `QueryConfig`. Not always enabled — depends on GrowthBook feature flags.

### Connection to config

`buildQueryConfig()` in `src/query/config.ts` creates a configuration snapshot per query that includes:
- `streamingToolExecution` — whether tools can start while model is still streaming
- `emitToolUseSummaries` — whether to generate tool-use summaries
- `fastModeEnabled` — whether fast mode is active

---

## 4. Context Collapse

**File:** `src/services/contextCollapse/`

### What it does

Archives granular individual messages into higher-level summaries. Instead of keeping 20 messages about a file edit, collapse them into a single "User edited X, Y, Z files" summary.

### Feature-gated

Controlled by the `CONTEXT_COLLAPSE` feature flag. When active, it **disables** auto-compact to prevent the two systems from conflicting.

### Thresholds

- **Commit threshold:** 90% of context window — triggers collapse
- **Blocking threshold:** 95% of context window — hard stop

---

## 5. Auto-compact

**File:** `src/services/compact/autoCompact.ts`

### Functions

| Function | Signature | What it does |
|----------|-----------|-------------|
| `getEffectiveContextWindowSize()` | `() => number` | Calculates available context tokens after reserving space for output |
| `getAutoCompactThreshold()` | `() => number` | Returns the token count at which auto-compact triggers |
| `calculateTokenWarningState()` | `() => TokenWarningState` | Computes warning/error thresholds |
| `isAutoCompactEnabled()` | `() => boolean` | Checks if auto-compact is enabled (respects feature flags) |
| `shouldAutoCompact()` | `() => Promise<boolean>` | Decides if compaction should run now |
| `autoCompactIfNeeded()` | `(messages, ...) => Promise<...>` | Executes compaction if needed |

### Key Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `AUTOCOMPACT_BUFFER_TOKENS` | 13,000 | Triggers auto-compact when this many tokens remain free |
| `WARNING_THRESHOLD_BUFFER_TOKENS` | 20,000 | Shows warning to user |
| `ERROR_THRESHOLD_BUFFER_TOKENS` | 20,000 | Hard error threshold |
| `MANUAL_COMPACT_BUFFER_TOKENS` | 3,000 | Buffer preserved for manual `/compact` |
| `MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES` | 3 | Circuit breaker — stops trying after 3 failures |
| `MAX_OUTPUT_TOKENS_FOR_SUMMARY` | 20,000 | Max tokens for the summary generation |

### How it works

1. Checks if token usage exceeds `AUTOCOMPACT_BUFFER_TOKENS` threshold
2. If so, tries **session memory compaction** first (faster, preserves some structure)
3. Falls back to **traditional compaction** via `compactConversation()` if session memory fails
4. Has a circuit breaker — after 3 consecutive failures, stops trying
5. Skipped entirely when context collapse mode is active

### The compact engine itself

**File:** `src/services/compact/compact.ts` (1706 lines)

| Function | What it does |
|----------|-------------|
| `compactConversation()` | Main compaction — summarizes old messages while preserving recent history |
| `partialCompactConversation()` | Partial compaction around a selected message |
| `streamCompactSummary()` | Streams summary generation (avoids blocking) |
| `stripImagesFromMessages()` | Removes images before summarization (saves tokens) |
| `stripReinjectedAttachments()` | Removes attachments that will be re-added after compaction |
| `truncateHeadForPTLRetry()` | Drops oldest messages when compact itself hits prompt-too-long |
| `buildPostCompactMessages()` | Constructs the final message list after compaction |
| `createPostCompactFileAttachments()` | Restores recently accessed files (up to 5) |
| `createPlanAttachmentIfNeeded()` | Preserves active plan files |
| `createSkillAttachmentIfNeeded()` | Preserves invoked skill hints |
| `createAsyncAgentAttachmentsIfNeeded()` | Tracks background agent status |

### Post-compaction restoration

After compaction removes old messages, the system re-injects:
- **Up to 5 recently accessed files** (max 5,000 tokens each, 50k total budget)
- **Active skill hints** (max 5,000 tokens each, 25k budget)
- **Plan files** if a plan is active
- **Background agent status** if agents are running

This ensures the model doesn't lose critical context that was in the compacted messages.

---

## 6. Reactive Compact

**File:** `src/services/compact/reactiveCompact.ts`

### What it does

Emergency compaction triggered **after** a `prompt_too_long` API error. This is the last resort — the normal pre-flight pipeline failed to prevent the overflow.

### When it runs

Only when the API returns a prompt-too-long error, meaning the pre-flight checks didn't catch the context overflow in time. This can happen when:
- A very large file was added to context between turns
- Multiple tools returned large results simultaneously
- The context window was already near capacity

---

## The Compaction Command

**File:** `src/commands/compact/compact.ts`

Users can manually trigger compaction with `/compact`. This command:

1. If no custom instructions → tries session memory compaction first
2. If in reactive-only mode → routes to `compactViaReactive()`
3. Otherwise → traditional compaction with microcompact fallback
4. Shows compaction result to user (how many tokens saved)

---

## Cross-References

- This pipeline runs inside: [[The Closed Loop - Input to Output Flow]] (Step 6a)
- API error that triggers reactive compact: [[Deep Dive - API Streaming Layer]]
- Tool results that fill up context: [[Deep Dive - Tool Execution Pipeline]]
- Config gates that control microcompact: `src/query/config.ts`
- Full compaction engine: `src/services/compact/compact.ts`
