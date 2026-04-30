# The Closed Loop: How Your Input Travels Through Claude Code

> **This is the highest-priority document.** It traces every step from when you type a message in the terminal to when Claude finishes responding and waits for your next input.

---

## The Loop at a Glance

```
User types input
      │
      ▼
┌─────────────────────────────────────┐
│  1. TERMINAL INPUT                  │
│  src/components/PromptInput/        │
│  src/ink/hooks/use-input.js         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. INPUT PROCESSING                │
│  src/utils/processUserInput/        │
│  - Detect slash commands            │
│  - Parse file references (@file)    │
│  - Handle image pastes              │
│  - Run pre-submit hooks             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. MESSAGE CREATION                │
│  src/utils/messages.ts              │
│  - createUserMessage()              │
│  - createCommandInputMessage()      │
│  - Attachments added                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. HISTORY & CONTEXT               │
│  src/history.ts                     │
│  - addToHistory()                   │
│  - expandPastedTextRefs()           │
│  - parseReferences()               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  5. QUERY ENTRY (REPL → query())    │
│  src/screens/REPL.tsx               │
│  - Calls query() from query.ts      │
│  - Passes messages + system prompt  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  6. THE QUERY LOOP (query.ts:queryLoop)             │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  6a. PRE-FLIGHT                               │  │
│  │  - Token budget check (src/query/tokenBudget) │  │
│  │  - Snip compaction (services/compact/snip)    │  │
│  │  - Microcompact (query/config.ts gates)       │  │
│  │  - Context collapse (contextCollapse/)         │  │
│  │  - Auto-compact (services/compact/autoCompact)│  │
│  │  - Block if context window full               │  │
│  └──────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  6b. API CALL (deps.callModel())              │  │
│  │  src/services/api/claude.ts                   │  │
│  │  - Streams response from Anthropic API        │  │
│  │  - Yields assistant messages as they arrive   │  │
│  │  - Collects tool_use blocks                   │  │
│  │  - Handles model fallback                     │  │
│  └──────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  6c. TOOL EXECUTION                           │  │
│  │  src/services/tools/toolOrchestration.ts      │  │
│  │  - StreamingToolExecutor or runTools()         │  │
│  │  - Permission check per tool                  │  │
│  │  - Execute tool.call()                        │  │
│  │  - Yield tool_result messages                 │  │
│  └──────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  6d. POST-TOOL PROCESSING                     │  │
│  │  - Attach queued commands                     │  │
│  │  - Memory prefetch consume                    │  │
│  │  - Skill discovery prefetch                   │  │
│  │  - Tool use summary generation                │  │
│  │  - Refresh MCP tools                          │  │
│  └──────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  6e. LOOP DECISION                            │  │
│  │  - If model requested tools → CONTINUE LOOP   │  │
│  │  - If model stopped → check stop hooks        │  │
│  │  - If max turns → EXIT                        │  │
│  │  - If aborted → EXIT                          │  │
│  └──────────────────┬────────────────────────────┘  │
│                      │                               │
│     ← (continues to 6a with accumulated messages) → │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────┐
│  7. STREAMING OUTPUT                │
│  src/utils/messages.ts              │
│  - handleMessageFromStream()        │
│  - Each yielded message rendered    │
│  - Thinking blocks displayed        │
│  - Tool results shown               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  8. UI RENDER (React/Ink)           │
│  src/components/Message.tsx         │
│  src/components/messages/           │
│  - AssistantTextMessage             │
│  - AssistantThinkingMessage         │
│  - UserToolResultMessage            │
│  - MessageRow layout                │
│  - VirtualMessageList scroll        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  9. COST TRACKING                   │
│  src/cost-tracker.ts                │
│  - Accumulate token usage           │
│  - Calculate cost per turn          │
│  - Cost summary in prompt           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  10. SESSION PERSISTENCE            │
│  src/utils/sessionStorage.ts        │
│  - recordTranscript()               │
│  - flushSessionStorage()            │
│  - Session title generation         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  11. READY FOR NEXT INPUT           │
│  src/components/PromptInput/        │
│  - PromptInput re-enabled           │
│  - Cursor visible, input focused    │
│  → Back to Step 1                   │
└─────────────────────────────────────┘
```

---

## Step-by-Step Deep Dive

### Step 1: Terminal Input Capture

**Files:** `src/components/PromptInput/`, `src/ink/hooks/use-input.js`, `src/ink/termio/`

When you type in the Claude Code terminal:
- **Ink** (custom React-for-terminal framework at `src/ink/`) captures raw stdin
- `useInput` hook processes keystrokes (vim mode, keybindings, etc.)
- The `PromptInput` React component manages the input buffer, auto-complete suggestions, and submission
- `src/utils/earlyInput.ts` can capture input even before the REPL is fully rendered (seedEarlyInput/consumeEarlyInput)

**Why separate files:** The terminal input layer is isolated because it handles OS-specific terminal I/O, raw mode, escape sequences, and vim emulation — none of which should leak into business logic.

---

### Step 2: Input Processing

> **Deep dive:** [[Deep Dive - Input Processing Pipeline]] — full routing logic, hook execution, attachment building

**Files:** `src/utils/processUserInput/processUserInput.ts`, `src/utils/processUserInput/processTextPrompt.ts`, `src/utils/slashCommandParsing.ts`

`processUserInput()` is the gateway. It determines what kind of input you gave:
- **Slash commands** (`/commit`, `/help`) → parsed by `parseSlashCommand()`, dispatched to command handlers in `src/commands/`
- **File references** (`@file.ts`) → `parseReferences()` resolves paths
- **Image pastes** → validated by `isValidImagePaste()`, resized by `maybeResizeAndDownsampleImageBlock()`
- **Regular text** → passed through to message creation
- **Pre-submit hooks** fire here (`executeUserPromptSubmitHooks`)

**Why separate:** Input processing must handle many input types (text, commands, images, drag-drop) before they become messages. Keeping this separate means the query loop only ever deals with well-formed messages.

---

### Step 3: Message Creation

**Files:** `src/utils/messages.ts`

`createUserMessage()` wraps the processed input into a typed `Message` object:
- Adds UUID, timestamp, session metadata
- Creates content blocks (text, image, tool_result)
- `createCommandInputMessage()` wraps slash command output
- `createAttachmentMessage()` wraps memory files, skill hints, MCP resources

**Why separate:** Messages are the universal currency of the system. Every component (UI, API, storage, tools) operates on the same `Message` type. Having a single factory ensures consistency.

---

### Step 4: History & Context

**Files:** `src/history.ts`, `src/context.ts`, `src/utils/claudemd.ts`

Before the query:
- `addToHistory()` records the message for session persistence
- `getSystemContext()` collects environment info (OS, shell, git branch, project structure)
- `getUserContext()` gathers user-specific context (CLAUDE.md files, memory files)
- `getMemoryFiles()` loads `.claude/memory/` contents
- `buildEffectiveSystemPrompt()` assembles the full system prompt from all parts

**Why separate:** Context assembly is complex — it pulls from CLAUDE.md, settings, project config, MCP resources, and memory. Isolating it prevents the query loop from needing to know where context comes from.

---

### Step 5: REPL → query()

**Files:** `src/screens/REPL.tsx` (line ~146: `import { query } from '../query.js'`)

The REPL component calls `query()` with:
- `messages`: The full conversation history plus the new user message
- `systemPrompt`: The assembled system prompt
- `userContext` / `systemContext`: Environment variables injected as API `user` context
- `tools`: The filtered tool pool (from `getTools()` + MCP tools)
- `canUseTool`: Permission checker callback
- `toolUseContext`: Current tool permissions, file cache, abort controller

**Why separate:** The REPL is a React component. It should orchestrate UI and state, not implement the query algorithm. The `query()` function is pure logic.

---

### Step 6: The Query Loop

**File:** `src/query.ts` — the **heart of Claude Code**

This is a `while(true)` async generator loop (`queryLoop()`) that drives the entire agentic turn:

#### 6a. Pre-flight (context management)

> **Deep dive:** [[Deep Dive - Pre-flight Pipeline]] — token budget, snip, microcompact, context collapse, auto-compact, reactive compact

Before calling the API, the loop checks and optimizes the context window:

| Stage | File | What it does |
|-------|------|-------------|
| Token budget | `src/query/tokenBudget.ts` | Check if the turn budget is exhausted |
| Snip | `services/compact/snipCompact.ts` | Remove old verbose tool results |
| Microcompact | `query/config.ts` gates | Cache-editing compaction |
| Context collapse | `services/contextCollapse/` | Archive old messages into summaries |
| Auto-compact | `services/compact/autoCompact.ts` | Summarize conversation when approaching context limits |
| Block check | `calculateTokenWarningState()` | Hard-stop if context is completely full |

**Why this order:** Snip runs first (cheapest, removes old tool output). Microcompact edits cache entries. Collapse archives granular context. Auto-compact is the nuclear option (full summary). Each progressively more expensive.

#### 6b. API Call

> **Deep dive:** [[Deep Dive - API Streaming Layer]] — SSE events, retry logic, model fallback, prompt caching, error classification

**File:** `deps.callModel()` → `src/services/api/claude.ts`

Streams the response from Anthropic's API:
- `prependUserContext()` injects environment variables into the message array
- `appendSystemContext()` appends dynamic context to the system prompt
- The response is streamed token-by-token via SSE
- `assistantMessages` collect the model's response blocks
- `toolUseBlocks` collect any tool_use requests from the model
- If the model fails, `FallbackTriggeredError` triggers fallback to a different model

**Why separate:** API communication involves streaming, retries, error handling, model selection, and cache management. Isolating this from the loop keeps the control flow clean.

#### 6c. Tool Execution

> **Deep dive:** [[Deep Dive - Tool Execution Pipeline]] — concurrency partitioning, StreamingToolExecutor, permission flow, result storage

**Files:** `src/services/tools/toolOrchestration.ts`, `src/services/tools/toolExecution.ts`, `src/services/tools/StreamingToolExecutor.ts`

When the model requests tools:
1. `runTools()` or `StreamingToolExecutor` processes tool_use blocks
2. Tools are partitioned into **concurrent-safe** (read-only) and **serial** (writes)
3. Each tool goes through:
   - `findToolByName()` — locate the tool definition
   - `canUseTool()` — permission check (see Step 6c-permission)
   - `tool.call()` — execute the tool's logic
   - Result wrapped as `tool_result` message
4. Permission-protected tools show a dialog to the user via `PermissionRequest` component

**Permission sub-flow:**
```
Tool requested
    → canUseTool() checks PermissionMode
    → If needs approval → PermissionRequest.tsx renders dialog
    → User approves/denies
    → If denied → tool_result with error
    → If approved → tool.call() executes
```

**Why separate:** Tool execution is the most security-sensitive part. Isolating it enables permission enforcement, concurrency control, and streaming execution without polluting the main loop.

#### 6d. Post-Tool Processing

After tools finish, the loop:
- Drains queued commands (task notifications, prompt submissions) via `getCommandsByMaxPriority()`
- Consumes memory prefetch results (`filterDuplicateMemoryAttachments`)
- Injects skill discovery results
- Refreshes MCP tool list if servers connected mid-turn
- Generates tool-use summaries (via Haiku in background)
- Checks max-turns limit

#### 6e. Loop Decision

- **Model requested tools** → state = accumulated messages → `continue` back to 6a
- **Model stopped (end_turn)** → check stop hooks → return
- **Aborted by user** → cleanup → return
- **Max turns** → yield max_turns_reached → return

---

### Step 7: Streaming Output

**Files:** `src/utils/messages.ts`

Every message yielded by the query generator is processed:
- `handleMessageFromStream()` extracts text content from streaming events
- Messages are normalized via `normalizeMessage()`
- Tool results are mapped via `mapToolResultToToolResultBlockParam()`

---

### Step 8: UI Rendering

**Files:** `src/components/Message.tsx`, `src/components/MessageRow.tsx`, `src/components/messages/`

Each message type has a dedicated React component:

| Message Type | Component | Renders |
|-------------|-----------|---------|
| Assistant text | `AssistantTextMessage.tsx` | Markdown, code blocks |
| Thinking | `AssistantThinkingMessage.tsx` | Collapsible thinking block |
| Tool result | `UserToolResultMessage.tsx` | Tool output, diffs |
| System | `SystemTextMessage.tsx` | Status messages |
| Error | `UserToolErrorMessage.tsx` | Error display |

`VirtualMessageList.tsx` handles efficient scrolling through thousands of messages.

---

### Step 9: Cost Tracking

**Files:** `src/cost-tracker.ts`, `src/costHook.ts`

After each API response:
- `accumulateUsage()` adds input/output tokens
- `getTotalCost()` calculates USD cost based on model pricing
- Cost displayed in the prompt area via `useCostSummary()`

---

### Step 10: Session Persistence

**Files:** `src/utils/sessionStorage.ts`

- `recordTranscript()` saves every message to the session log file
- `flushSessionStorage()` ensures all data is written
- `generateSessionTitle()` creates a title for session history
- Enables `/resume` to restore conversations

---

### Step 11: Ready for Next Input

The REPL re-enables the `PromptInput` component, shows the cursor, and waits.

**The loop is closed.** Your next keystroke starts the cycle again at Step 1.

---

## The Big Picture: File Dependency Chain

```
main.tsx                    ← CLI entry, Commander.js setup
  → setup.ts                ← Environment, permissions, auth
  → replLauncher.tsx        ← Mounts React tree
    → App.tsx               ← Root component, theme, providers
      → REPL.tsx            ← Main screen, state orchestration
        → query.ts          ← THE LOOP (async generator)
          → services/api/   ← Anthropic API streaming
          → services/tools/ ← Tool execution engine
            → tools/*       ← Individual tool implementations
          → services/compact/ ← Context management
        → components/       ← UI rendering
```

---

## Key Insight: Why It's a Generator

`query()` is an **async generator** (`async function*`). This is the architectural keystone:

- The REPL `for await`s over the generator
- Each `yield` is one message/event streamed to the UI in real-time
- The REPL can `abort()` the generator (user pressed Escape)
- Tool results feed back into the generator's state via the `while(true)` loop
- No callbacks, no event emitters — clean pull-based flow

This means the entire agentic turn (API call → tools → more API calls → more tools) is a single generator invocation that the REPL consumes at its own pace.
