# Deep Dive: Tool Execution Pipeline

> How Claude Code executes tools requested by the model — concurrency, permissions, streaming execution, and result handling. This runs inside [[The Closed Loop - Input to Output Flow]] at Step 6c.

---

## Overview

When the model responds with `tool_use` blocks, the query loop hands them to the tool execution pipeline. This pipeline must:

1. Decide which tools can run in parallel vs serially
2. Check permissions for each tool
3. Execute the tools
4. Format results back into messages the model can read

```
Model returns tool_use blocks
      │
      ▼
┌────────────────────────────────────────┐
│  Partition Tool Calls                   │
│  (toolOrchestration.ts)                │
│                                         │
│  Read-only tools → concurrent batch    │
│  Write tools → serial (one at a time)  │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  For each tool:                         │
│                                         │
│  ┌──────────────────────┐              │
│  │  1. Validate input   │  Zod schema  │
│  │  2. Run pre-tool     │  hooks       │
│  │     hooks            │              │
│  │  3. Check perms      │  canUseTool  │
│  │     ┌─────────────┐  │              │
│  │     │ Permission  │  │              │
│  │     │ Dialog UI   │  │  (if needed) │
│  │     └─────────────┘  │              │
│  │  4. Execute tool     │  tool.call() │
│  │  5. Run post-tool    │  hooks       │
│  │     hooks            │              │
│  │  6. Format result    │              │
│  └──────────────────────┘              │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  Tool Result Storage                    │
│  - Small results: inline               │
│  - Large results: persist to disk      │
│    with PERSISTED_OUTPUT_TAG markers   │
└────────────────────────────────────────┘
```

---

## 1. Tool Orchestration

**File:** `src/services/tools/toolOrchestration.ts`

### Key Functions

| Function | Signature | What it does |
|----------|-----------|-------------|
| `getMaxToolUseConcurrency()` | `() => number` | Returns max concurrent tools (default 10, configurable via `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`) |
| `runTools()` | `async function*` | Main orchestrator — partitions and executes tool calls |
| `partitionToolCalls()` | `(toolCalls) => ToolCallBatch[]` | Groups tool calls into concurrent-safe batches |
| `runToolsSerially()` | `async function*` | Executes tools one at a time |
| `runToolsConcurrently()` | `async function*` | Executes multiple tools with concurrency limit |

### Partitioning Logic

Tools are split into batches:

```
Batch 1: [ReadTool, GlobTool, GrepTool]     ← All read-only → run concurrently
Batch 2: [WriteTool]                         ← Write tool → run alone, serially
Batch 3: [ReadTool, ReadTool]                ← Read-only again → concurrent
```

The `isConcurrencySafe()` method on each tool determines if it can run in parallel. A tool is concurrency-safe if:
- It's read-only (doesn't modify filesystem, state, or shared resources)
- It doesn't have side effects that could conflict with other running tools

---

## 2. Streaming Tool Executor

**File:** `src/services/tools/StreamingToolExecutor.ts`

### Why "Streaming"

The StreamingToolExecutor starts executing tools **before the model finishes** streaming all tool_use blocks. This reduces latency — the first tools begin while the model is still producing the last ones.

### Functions

| Function | What it does |
|----------|-------------|
| `addTool()` | Adds a tool to the execution queue |
| `getCompletedResults()` | Yields completed results in the order they were received |
| `getRemainingResults()` | Waits for all remaining tools to complete |

### State Machine

Each tool goes through states:

```
queued → executing → completed → yielded
```

### Concurrency Control

- `canExecuteTool()` checks if a new tool can start based on:
  - Current number of executing tools
  - Whether the new tool is concurrency-safe
  - Whether any executing tool is non-concurrent-safe
- Non-concurrent tools block all subsequent tools until they complete
- Concurrent tools can run together if all are marked safe

### Interruption

Tracks in-progress tool IDs for interruption handling. When the user presses Escape, running tools can be cancelled with proper cleanup.

---

## 3. Single Tool Execution

**File:** `src/services/tools/toolExecution.ts`

### Functions

| Function | What it does |
|----------|-------------|
| `runToolUse()` | Main async generator — executes a single tool with full lifecycle |
| `streamedCheckPermissionsAndCallTool()` | Wraps permission check + execution in a stream |
| `checkPermissionsAndCallTool()` | Core: validate → hooks → permission → execute → post-hooks |
| `classifyToolError()` | Classifies tool errors for telemetry |

### Execution Flow (detailed)

```
1. findToolByName()          ← Locate tool definition in the tool pool
       │
       ▼
2. inputSchema.safeParse()   ← Zod validation of tool input
       │
       ▼
3. tool.validateInput?()     ← Tool-specific validation (optional)
       │
       ▼
4. runPreToolUseHooks()      ← Execute user-configured pre-tool hooks
       │
       ▼
5. resolveHookPermissionDecision()
       │
       ├─ allowed → execute
       │
       ├─ denied → return error result
       │
       └─ ask → render PermissionRequest UI
              │
              ├─ user approves → execute
              └─ user denies → return error result
       │
       ▼
6. tool.call()               ← Execute the tool's actual logic
       │
       ▼
7. processToolResultBlock()  ← Format the result
       │
       ▼
8. runPostToolUseHooks()     ← Execute user-configured post-tool hooks
       │
       ▼
9. Return ToolResultBlockParam
```

---

## 4. Permission System

**File:** `src/hooks/useCanUseTool.tsx`

### Permission Modes

| Mode | Behavior |
|------|----------|
| **Interactive** (default) | Shows permission dialog for each dangerous tool |
| **Auto** | Auto-approves based on rules, detects dangerous Bash patterns |
| **Plan** | Read-only tools auto-approved, writes blocked |
| **Coordinator/Swarm** | Different approval paths for multi-agent setups |

### Permission Check Flow

```
useCanUseTool()
      │
      ▼
createPermissionContext()       ← Build permission context
      │
      ▼
hasPermissionsToUseTool()       ← Check against permission rules
      │
      ├─ allowed → return
      │
      ├─ denied → log denial, return
      │
      └─ ask → interactive dialog
              │
              ├─ Speculative classifier check (Bash commands)
              ├─ PermissionRequest.tsx renders dialog
              ├─ User approves/denies/always-allow
              └─ Return decision
```

### Permission Persistence

When a user selects "Always allow", the permission is saved so future identical tool calls are auto-approved. This is stored in the permission rules configuration.

---

## 5. Tool Result Storage

**File:** `src/utils/toolResultStorage.ts`

### Why persist to disk

Large tool results (e.g., reading a big file) can consume significant context window space. Instead of truncating, results are persisted to disk with a reference marker.

### How it works

- Results exceeding a size threshold are written to `tool-results/` subdirectory in the session folder
- The message contains a `PERSISTED_OUTPUT_TAG` XML marker instead of the full content
- GrowthBook overrides allow dynamic threshold configuration per tool
- Preview snippets are generated for persisted results

### Size thresholds

| Tool | Default threshold | Notes |
|------|-------------------|-------|
| Bash | Configurable | Command output can be very large |
| FileRead | Configurable | Large files trigger persistence |
| Grep | Configurable | Search results can be extensive |

---

## 6. Tool Use Summary Generation

**File:** `src/services/toolUseSummary/toolUseSummaryGenerator.ts`

### What it does

Generates human-readable summaries of completed tool batches using Haiku (fast, cheap model). Creates concise labels for progress updates.

### Characteristics

- **30 character limit** on summary labels
- Uses past tense verbs and distinctive nouns (git-commit-subject style)
- Queries Haiku with structured system prompt
- Returns null if generation fails (non-critical feature)

### Example outputs

- "Edited auth middleware"
- "Searched 15 files for TODO"
- "Created new test file"

---

## Cross-References

- Runs inside: [[The Closed Loop - Input to Output Flow]] (Step 6c)
- Tools fill context window → triggers: [[Deep Dive - Pre-flight Pipeline]]
- Tool results stream from: [[Deep Dive - API Streaming Layer]]
- Permission UI renders in: [[UI Components]]
- Individual tool definitions: [[Tool System]]
- Hook system: `src/utils/hooks.ts`
