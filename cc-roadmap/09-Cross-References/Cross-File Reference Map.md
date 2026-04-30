# Cross-File Reference Map

> How every major file and directory connects to every other. The dependency graph of Claude Code.

---

## Dependency Map

```
main.tsx
├── setup.ts                    ← Environment initialization
├── replLauncher.tsx            ← REPL mounting
│   ├── components/App.tsx      ← Root React component
│   └── screens/REPL.tsx        ← Main screen
├── bootstrap/state.ts          ← Global mutable state
├── commands.ts                 ← Slash command registry
│   └── commands/*              ← Individual command files (~80 commands)
├── tools.ts                    ← Tool registry
│   └── tools/*                 ← Individual tool implementations (~30 tools)
├── context.ts                  ← System/user context assembly
├── history.ts                  ← Prompt history
├── ink.ts                      ← Terminal UI framework
│   └── ink/*                   ← Custom Ink framework
├── services/analytics/         ← Telemetry
├── services/api/               ← API client
├── services/mcp/               ← MCP server management
├── services/compact/           ← Context compaction
├── services/policyLimits/      ← Enterprise policies
├── services/plugins/           ← Plugin system
├── services/oauth/             ← Authentication
├── utils/auth.ts               ← Auth helpers
├── utils/config.ts             ← Settings management
├── utils/permissions/          ← Permission system
├── utils/hooks.ts              ← Hook execution engine
└── utils/claudemd.ts           ← CLAUDE.md loading

screens/REPL.tsx
├── query.ts                    ← THE QUERY LOOP
│   ├── query/config.ts         ← Query configuration
│   ├── query/deps.ts           ← Dependency injection for testing
│   ├── query/stopHooks.ts      ← Stop hook handling
│   ├── query/tokenBudget.ts    ← Token budget tracking
│   ├── services/api/claude.ts  ← API streaming
│   ├── services/tools/toolOrchestration.ts ← Tool execution
│   │   ├── services/tools/toolExecution.ts
│   │   ├── services/tools/StreamingToolExecutor.ts
│   │   └── tools/* (each tool's call() method)
│   ├── services/compact/       ← Compaction pipeline
│   ├── services/contextCollapse/ ← Context archiving
│   ├── utils/messages.ts       ← Message creation
│   ├── utils/attachments.ts    ← Attachment building
│   └── utils/sessionStorage.ts ← Transcript persistence
├── components/permissions/     ← Permission dialogs
├── components/PromptInput/     ← Input component
├── components/messages/        ← Message renderers
├── hooks/useCanUseTool.ts      ← Permission checker
├── hooks/useMergedClients.ts   ← MCP client merger
├── hooks/useMergedTools.ts     ← Tool pool merger
├── cost-tracker.ts             ← Cost accumulation
├── state/AppStateStore.ts      ← Central state
└── history.ts                  ← Add to history

QueryEngine.ts
├── query.ts                    ← Uses the same query() function
├── utils/processUserInput/     ← Input processing for SDK
├── services/api/claude.ts      ← API calls
└── utils/sessionStorage.ts     ← Transcript recording
```

---

## Function Cross-Reference: Key Functions and Where They're Called

### `query()` (src/query.ts)
- **Called by:** `REPL.tsx`, `QueryEngine.ts`
- **Calls:** `deps.callModel()` (API), `runTools()` (tools), `deps.autocompact()` (compaction)

### `createUserMessage()` (src/utils/messages.ts)
- **Called by:** `processUserInput.ts`, `query.ts` (recovery messages), `QueryEngine.ts`
- **Used at:** Input processing, error recovery, meta-injection

### `getTools()` (src/tools.ts)
- **Called by:** `main.tsx` (startup), `REPL.tsx` (tool pool refresh)
- **Calls:** Each tool's `buildTool()`, `filterToolsByDenyRules()`

### `canUseTool()` (src/hooks/useCanUseTool.ts)
- **Called by:** `toolOrchestration.ts`, `StreamingToolExecutor.ts`
- **Uses:** `AppState.toolPermissionContext`, permission rules

### `processUserInput()` (src/utils/processUserInput/)
- **Called by:** `REPL.tsx` (on prompt submit), `print.ts` (headless mode)
- **Calls:** `parseSlashCommand()`, `createUserMessage()`, `executeUserPromptSubmitHooks()`

### `recordTranscript()` (src/utils/sessionStorage.ts)
- **Called by:** `QueryEngine.ts` (after each message)
- **Writes to:** Session JSONL files in `~/.claude/projects/`

### `addToHistory()` (src/history.ts)
- **Called by:** `REPL.tsx` (after prompt submit), `main.tsx` (resume)
- **Writes to:** `~/.claude/history.jsonl`

### `getSystemContext()` / `getUserContext()` (src/context.ts)
- **Called by:** `main.tsx` (startup), `query.ts` (each turn)
- **Calls:** `getGitStatus()`, `getClaudeMds()`, `getMemoryFiles()`

### `buildEffectiveSystemPrompt()` (src/utils/systemPrompt.ts)
- **Called by:** `REPL.tsx`
- **Uses:** `constants/prompts.ts` (54KB system prompt template), `context.ts`

### `handleMessageFromStream()` (src/utils/messages.ts)
- **Called by:** `REPL.tsx` (processes streaming events)
- **Returns:** Extracted text content from SSE events

---

## Data Flow: What Connects to What

```
User Input
    │
    ├── processUserInput() → createUserMessage() → addToHistory()
    │                                              → recordTranscript()
    │
    ├── query() → callModel() → Anthropic API
    │           ← streaming events ←
    │           → handleMessageFromStream() → UI render
    │           → runTools() → tool.call() → canUseTool()
    │                       ← PermissionRequest UI ←
    │                       → tool result → recordTranscript()
    │           → autocompact() → API call → summary messages
    │           → loop back to callModel() with tool results
    │
    └── Terminal output ← Ink render ← React state (AppState)
```

---

## Directory Purpose Quick Reference

| Directory | One-line purpose |
|---|---|
| `src/bootstrap/` | Global session state (session ID, CWD, model) |
| `src/cli/` | Headless/print mode execution |
| `src/commands/` | 80+ slash command implementations |
| `src/components/` | React/Ink UI components |
| `src/constants/` | System prompts, tool names, XML tags |
| `src/context/` | Stats context providers |
| `src/coordinator/` | Multi-worker orchestration mode |
| `src/entrypoints/` | SDK entry points |
| `src/hooks/` | React hooks for REPL state |
| `src/ink/` | Custom Ink terminal UI framework |
| `src/memdir/` | Memory directory management |
| `src/migrations/` | Settings migration scripts |
| `src/outputStyles/` | Output formatting styles |
| `src/plugins/` | Plugin system |
| `src/query/` | Query loop configuration and helpers |
| `src/remote/` | Remote session management |
| `src/schemas/` | JSON schemas for hooks |
| `src/screens/` | Top-level screen components (REPL) |
| `src/server/` | Direct connect server |
| `src/services/` | Service layer (API, MCP, analytics, etc.) |
| `src/skills/` | Skill system (bundled + discovered) |
| `src/state/` | AppState store and change handlers |
| `src/tasks/` | Task type implementations |
| `src/tools/` | Tool implementations |
| `src/types/` | TypeScript type definitions |
| `src/utils/` | Utility functions (~300 files) |
| `src/vim/` | Vim mode emulation |
| `src/voice/` | Voice mode |
