# Deep Dive: Input Processing Pipeline

> How Claude Code processes user input — from keystroke to well-formed message ready for the query loop. This covers [[The Closed Loop - Input to Output Flow]] Steps 1-4.

---

## Overview

Input processing transforms raw keystrokes into typed `Message` objects. It handles slash commands, file references, image pastes, hooks, and context assembly.

```
User types in PromptInput
      │
      ▼
┌──────────────────────────────────────┐
│  handlePromptSubmit()                │
│  (handlePromptSubmit.ts)             │
│                                       │
│  - Validate input                    │
│  - Expand pasted text references     │
│  - Handle exit/quit                  │
│  - Route immediate JSX commands      │
│  - Queue if busy                     │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  processUserInput()                  │
│  (processUserInput/processUserInput) │
│                                       │
│  1. Execute pre-submit hooks         │
│  2. Route by input type              │
│  3. Build attachments                │
└────────────┬─────────────────────────┘
             │
      ┌──────┼──────────────┐
      │      │              │
      ▼      ▼              ▼
  Slash    Bash         Regular
  Command  Command      Text
      │      │              │
      ▼      ▼              ▼
  process  process     processText
  Slash    Bash        Prompt
  Command  Command
      │      │              │
      └──────┴──────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  createUserMessage()                 │
│  (messages.ts)                       │
│  - Create typed Message object       │
│  - Add UUID, timestamp, metadata     │
│  - Attach context (memory, skills)   │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  addToHistory() + Context Assembly   │
│  - Record in history                 │
│  - Load system context               │
│  - Load user context (CLAUDE.md)     │
└──────────────────────────────────────┘
```

---

## 1. Input Capture: PromptInput Component

**File:** `src/components/PromptInput/PromptInput.tsx`

### What it does

The React component that manages the input bar. It:
- Maintains the input buffer state
- Handles paste operations (including image pastes)
- Shows command suggestions and autocomplete
- Manages vim/emacs input modes
- Delegates to `handlePromptSubmit` on submission

### Key features

- **Vim mode**: Controlled by `inputModes.ts` — supports insert/normal/visual modes
- **History navigation**: Up/Down arrows cycle through prompt history
- **Multi-line input**: Enter submits, Shift+Enter adds newline
- **Image paste**: Detects pasted images, validates format, optionally resizes

### Early input capture

**File:** `src/utils/earlyInput.ts`

`seedEarlyInput()` / `consumeEarlyInput()` — captures input typed before the REPL is fully rendered. Ensures no keystrokes are lost during startup.

---

## 2. Submission Handler

**File:** `src/utils/handlePromptSubmit.ts`

### Functions

| Function | What it does |
|----------|-------------|
| `handlePromptSubmit()` | Main UI handler — validates, expands, routes input |
| `executeUserInput()` | Core execution without UI concerns |

### Flow

```
handlePromptSubmit()
      │
      ├─ Is it exit/quit? → handle exit
      │
      ├─ Is it a local JSX command? → execute synchronously
      │   (returns immediately, no query needed)
      │
      ├─ Is system busy? → enqueue for later
      │
      ├─ Expand pasted text references
      │   (expandPastedTextRefs)
      │
      └─ Route to processUserInput()
```

### Immediate commands

Some commands execute synchronously and never reach the query loop:
- `/clear`, `/compact`, `/help`, `/cost`, `/exit`, `/status`, `/config`, etc.
- These return JSX UI directly (local-jsx command type)

### Queue management

If the query loop is already processing (busy state), new input is enqueued. The queue drains during post-tool processing in the query loop.

---

## 3. Main Input Processor

**File:** `src/utils/processUserInput/processUserInput.ts`

### Functions

| Function | What it does |
|----------|-------------|
| `processUserInput()` | Main entry — runs hooks, routes by type, returns processed messages |
| `processUserInputBase()` | Core routing logic without hook execution |

### Input Type Routing

```
processUserInputBase()
      │
      ├─ Bridge-origin remote message? → Handle remote/mobile command
      │   (lines 429-453)
      │
      ├─ Ultraplan keyword detected? → Route through /ultraplan
      │   (lines 467-493)
      │
      ├─ Mode is 'bash'? → processBashCommand()
      │   (lines 517-529)
      │
      ├─ Starts with '/'? → processSlashCommand()
      │   (lines 533-551)
      │
      └─ Otherwise → processTextPrompt()
          (lines 576-588)
```

### Hook Execution

`processUserInput()` runs **pre-submit hooks** before routing:

```
executeUserPromptSubmitHooks()
      │
      ├─ Blocking error → cancel submission, show error
      │
      ├─ Additional context from hooks → add as attachments
      │
      └─ Hook success → add as attachment message
```

---

## 4. Slash Command Parsing

**File:** `src/utils/slashCommandParsing.ts`

### Function: `parseSlashCommand()`

```
"/commit -m 'fix bug'" → { command: "commit", args: "-m 'fix bug'", isMCP: false }
"/mcp__server__tool"   → { command: "mcp__server__tool", args: "", isMCP: true }
```

- Removes leading `/`
- Detects MCP commands with `(MCP)` suffix
- Splits command name and arguments
- Returns `ParsedSlashCommand` object

### Command dispatch

After parsing, the command name is matched against the command registry (see [[Commands Directory]]). Commands can be:
- **`local`**: Returns text output directly
- **`local-jsx`**: Renders an Ink UI component
- **`prompt`**: Expands to text injected into the model prompt (these are "skills")

---

## 5. Text Prompt Processing

**File:** `src/utils/processUserInput/processTextPrompt.ts`

### Function: `processTextPrompt()`

Processes regular text prompts:
1. Creates a prompt ID and sets it for tracking
2. Analyzes prompt for negative/keep-going keywords
3. Handles mixed content (text + images)
4. Wraps input in `UserMessage` with proper metadata

### Special prompt detection

- **Negative keywords** (e.g., "stop", "cancel", "no") → may affect tool execution behavior
- **Keep-going keywords** → signal the model to continue working
- **Image attachments** → validated and optionally resized before inclusion

---

## 6. Attachment Building

**File:** `src/utils/attachments.ts`

### What are attachments

Attachments are extra context injected alongside the user message. They include:

| Attachment Type | What it adds |
|----------------|-------------|
| Memory files | Contents of `.claude/memory/` files |
| IDE selection | Currently selected text/range in VS Code/JetBrains |
| File diffs | Uncommitted changes in the working tree |
| Todo list | Current task list state |
| Skill hints | Hints about which skills are available |
| MCP resources | Resources from connected MCP servers |

### Why attachments exist

The model needs context beyond the user's text — what files are open, what's changed recently, what skills are available. Attachments bundle this context into the message without the user needing to type it.

---

## 7. Pre-Submit Hooks

**File:** `src/utils/hooks.ts`

### Functions

| Function | What it does |
|----------|-------------|
| `executeUserPromptSubmitHooks()` | Async generator yielding hook results |
| `getUserPromptSubmitHookBlockingMessage()` | Formats blocking error messages |

### Hook types

Hooks are user-configured shell commands that run at lifecycle points:
- **Pre-submit hooks** run before the message is sent to the model
- Can be **blocking** (cancel submission on error) or **non-blocking** (add context only)
- Support **prompt-based hooks** with ToolUseContext for advanced patterns

### Hook execution flow

```
executeUserPromptSubmitHooks()
      │
      ├─ For each configured hook:
      │   ├─ Execute shell command
      │   ├─ If blocking and fails → yield blocking error
      │   ├─ If non-blocking → yield additional context
      │   └─ If success → yield success message
      │
      └─ Return all collected results
```

---

## 8. Message Creation

**File:** `src/utils/messages.ts`

### Functions

| Function | What it does |
|----------|-------------|
| `createUserMessage()` | Creates the main `UserMessage` with content blocks |
| `createCommandInputMessage()` | Wraps slash command output into a message |
| `createAttachmentMessage()` | Wraps memory, skills, diffs as attachment messages |

### Message structure

```typescript
{
  type: "user",
  message: {
    role: "user",
    content: [
      { type: "text", text: "..." },
      { type: "image", source: { ... } },
      // ... more blocks
    ]
  },
  uuid: "...",
  timestamp: "...",
  // attachments added separately
}
```

---

## 9. History & Context Assembly

### History

**File:** `src/history.ts`

- `addToHistory()` — records the message to `~/.claude/history.jsonl`
- `expandPastedTextRefs()` — expands references to pasted content
- Enables up/down arrow history navigation in PromptInput

### System Context

**File:** `src/context.ts`

- `getSystemContext()` — collects: OS, shell, git branch, project structure, environment variables
- `getUserContext()` — gathers: CLAUDE.md files, memory files, skill definitions

### System Prompt Assembly

**File:** `src/utils/systemPrompt.ts`

- `buildEffectiveSystemPrompt()` — assembles the full system prompt from:
  - Base system prompt template (`constants/prompts.ts` — 54KB)
  - Tool descriptions
  - Context from `getSystemContext()` and `getUserContext()`

---

## Cross-References

- Starts at: [[The Closed Loop - Input to Output Flow]] (Steps 1-4)
- Message then enters: [[The Closed Loop - Input to Output Flow]] (Step 5 → query loop)
- Query loop: [[Deep Dive - API Streaming Layer]], [[Deep Dive - Tool Execution Pipeline]]
- Commands: [[Commands Directory]]
- Hooks system: `src/utils/hooks.ts`
- UI component: [[UI Components]] (PromptInput)
