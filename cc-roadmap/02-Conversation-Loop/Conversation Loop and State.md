# Conversation Loop and State

> The engine room: how messages flow through the system, how state is managed, and how the agentic loop works.

---

## The Core Loop: `query.ts`

**File:** `src/query.ts` (~1730 lines)
**Why it exists separately:** This is the heart of Claude Code. It's a single async generator function (`queryLoop`) that implements the agentic turn: call the API → execute tools → call the API again → repeat until done.

**Key insight:** `query()` is an `async function*` (async generator). The REPL `for await`s over it. Each `yield` is one message/event streamed to the UI in real-time. This is the architectural keystone — no callbacks, no event emitters, clean pull-based flow.

### Functions

| Function | What it does |
|---|---|
| `query(params)` | Entry point. Wraps `queryLoop`, handles command completion notifications. |
| `queryLoop(params, consumedCommandUuids)` | The `while(true)` loop. Manages the full agentic turn. |
| `yieldMissingToolResultBlocks()` | Generates error tool_results for orphaned tool_use blocks (e.g., after abort). |
| `isWithheldMaxOutputTokens()` | Checks if an error message should be withheld from the stream for recovery. |

### Loop Iteration (simplified)

```
while (true):
  1. Check token budget
  2. Snip old tool results (cheap)
  3. Microcompact (cache editing)
  4. Context collapse (archive old messages)
  5. Auto-compact (summarize if approaching limits)
  6. Block if context full
  7. Stream API response (deps.callModel())
  8. Collect tool_use blocks
  9. Execute tools (runTools or StreamingToolExecutor)
  10. Attach queued commands + memory + skills
  11. Refresh MCP tools
  12. If tools were used → continue loop (state = old + assistant + toolResults)
  13. If no tools → check stop hooks → return
```

### State Object

Carried between iterations:

```typescript
type State = {
  messages: Message[]              // Full conversation for this turn
  toolUseContext: ToolUseContext    // Permissions, file cache, abort controller
  autoCompactTracking: ...         // Compaction state
  maxOutputTokensRecoveryCount: 0  // Token limit recovery attempts
  hasAttemptedReactiveCompact: bool
  maxOutputTokensOverride: number | undefined
  pendingToolUseSummary: Promise   // Background summary generation
  stopHookActive: bool
  turnCount: number
  transition: Continue | undefined // Why the previous iteration continued
}
```

---

## The Query Engine: `QueryEngine.ts`

**File:** `src/QueryEngine.ts`
**Why separate:** Provides a higher-level wrapper around `query()` for SDK/headless use. While `query.ts` is used by the REPL, `QueryEngine` adds SDK-specific concerns: transcript recording, usage accumulation, slash command handling.

**Key functions:**
- **`QueryEngine` class**: Wraps `query()` with SDK lifecycle management
- **`ask(query, options)`**: One-shot query convenience function
- Handles `maxTurns`, `maxBudgetUsd`, `jsonSchema` for SDK consumers

---

## State Management: `src/state/`

| File | Purpose |
|---|---|
| `AppStateStore.ts` | Central React state: messages, tools, MCP clients, permissions, model, effort, cost |
| `store.ts` | `createStore()` utility for creating observable state stores |
| `onChangeAppState.ts` | Side effects when app state changes (analytics, UI updates) |

**AppState** is the single source of truth for the REPL's React tree:
- `messages: Message[]` — conversation history
- `toolPermissionContext` — current permission mode and rules
- `mcp.clients` / `mcp.tools` — MCP server connections
- `fastMode`, `effortValue`, `advisorModel` — user settings
- `backgroundTasks` — running background agent tasks

---

## Task System: `src/Task.ts` + `src/tasks.ts`

### `Task.ts`

**Why separate:** Defines the `Task` interface and types for background work (agents, shells, workflows). Tasks run independently of the main query loop.

**Key types:**
- **`TaskType`**: `'local_bash' | 'local_agent' | 'remote_agent' | 'in_process_teammate' | 'local_workflow' | 'monitor_mcp' | 'dream'`
- **`TaskStatus`**: `'pending' | 'running' | 'completed' | 'failed' | 'killed'`
- **`Task` interface**: `{ name, type, kill(taskId, setAppState) }`
- **`generateTaskId(type)`**: Creates prefixed IDs (e.g., `b8abc1234` for bash, `a7def5678` for agent)

### `tasks.ts`

**Why separate:** Registry of all task types. Returns task handlers by type.

**Key function:**
- **`getAllTasks()`**: Returns `[LocalShellTask, LocalAgentTask, RemoteAgentTask, DreamTask, ...]`
- **`getTaskByType(type)`**: Find a task handler by type

---

## Commands: `src/commands.ts`

**Why separate:** Central registry for all slash commands and skills. Loads from multiple sources (built-in, skills dirs, plugins, MCP, workflows).

**Key functions:**
- **`getCommands(cwd)`**: Returns all available commands (memoized, filtered by auth/availability)
- **`findCommand(name, commands)`**: Look up a command by name or alias
- **`getSkillToolCommands(cwd)`**: Commands the model can invoke (skills)
- **`isBridgeSafeCommand(cmd)`**: Whether a command works over remote bridge

---

## Context: `src/context.ts`

**Why separate:** Assembles the system and user context injected into every API call. This is where CLAUDE.md files, git status, and dates get added.

**Key functions:**
- **`getSystemContext()`**: Returns `{ gitStatus, cacheBreaker }` — memoized per conversation
- **`getUserContext()`**: Returns `{ claudeMd, currentDate }` — memoized per conversation
- **`getGitStatus()`**: Runs git commands (branch, status, log) — memoized

---

## History: `src/history.ts`

**Why separate:** Manages command history for the Up-arrow and Ctrl+R picker. Persists to `~/.claude/history.jsonl`.

**Key functions:**
- **`addToHistory(command)`**: Appends to history file (async, buffered)
- **`getHistory()`**: Yields history entries for current project, newest first
- **`getTimestampedHistory()`**: For Ctrl+R picker with timestamps
- **`removeLastFromHistory()`**: Undo the last entry (used by Esc/restore)
- **`parseReferences(input)`**: Parse `[Pasted text #N]` references
- **`expandPastedTextRefs(input, pastedContents)`**: Replace paste refs with content

---

## Coordinator Mode: `src/coordinator/coordinatorMode.ts`

**Why separate:** Implements multi-worker orchestration. In coordinator mode, the model doesn't use tools directly — it spawns workers via `AgentTool` and coordinates them.

**Key functions:**
- **`isCoordinatorMode()`**: Checks env var `CLAUDE_CODE_COORDINATOR_MODE`
- **`getCoordinatorUserContext(mcpClients)`**: Injects tool availability info
- **`getCoordinatorSystemPrompt()`**: Full system prompt for coordinator behavior
- **`matchSessionMode(sessionMode)`**: Restore correct mode on session resume

---

## Cross-References

- `query.ts` → [[Tool System]] (executes tools via `runTools()`)
- `query.ts` → [[Services and Utilities]] (compact, API, attachments)
- `AppState` → [[UI Components]] (drives all React rendering)
- `commands.ts` → `src/commands/*` (each command is a separate file)
- `coordinatorMode.ts` → [[Tool System#AgentTool]] (spawns workers)
