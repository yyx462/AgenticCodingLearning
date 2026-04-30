# Entry & Bootstrap Layer

> How Claude Code starts up from `main.tsx` to the REPL being ready for your input.

---

## Startup Sequence

```
main.tsx (CLI entry, ~300 lines of imports)
  │
  ├─ profileCheckpoint('main_tsx_entry')     ← First thing: mark timestamp
  ├─ startMdmRawRead()                       ← Fire MDM subprocess in parallel
  ├─ startKeychainPrefetch()                  ← Fire macOS keychain reads in parallel
  │
  ├─ Commander.js CLI parsing                 ← Flags: --model, --permission-mode, etc.
  │
  ├─ setup.ts:setup()                         ← Environment initialization
  │   ├─ Node.js version check (>= 18)
  │   ├─ UDS messaging server start
  │   ├─ Teammate snapshot capture
  │   ├─ Terminal backup restoration
  │   ├─ setCwd(cwd)                         ← Lock working directory
  │   ├─ captureHooksConfigSnapshot()        ← Snapshot hooks config for safety
  │   ├─ Worktree creation (if --worktree)
  │   ├─ initSessionMemory()                 ← Register memory hooks
  │   ├─ getCommands() prefetch              ← Load slash commands
  │   ├─ loadPluginHooks() prefetch           ← Load plugin hooks
  │   ├─ lockCurrentVersion()                ← Prevent deletion by other processes
  │   ├─ Bypass permissions safety checks
  │   └─ checkForReleaseNotes()
  │
  ├─ init()                                   ← Telemetry & auth initialization
  │   ├─ initializeGrowthBook()              ← Feature flags
  │   ├─ initializeTelemetryAfterTrust()
  │   ├─ loadPolicyLimits()                  ← Enterprise policy
  │   └─ loadRemoteManagedSettings()
  │
  ├─ REPL mounting
  │   ├─ createRoot()                         ← Ink terminal root
  │   └─ launchRepl()                         ← Mount <App><REPL/></App>
  │       ├─ App.tsx                          ← Theme, providers, global state
  │       └─ REPL.tsx                         ← Main interactive screen
  │           ├─ Mounts PromptInput           ← Ready for user typing
  │           ├─ Loads conversation history   ← For /resume
  │           ├─ Connects MCP servers         ← Tool extensions
  │           └─ Shows welcome/logo
  │
  └─ REPL is ready. Waiting for input → [[The Closed Loop - Input to Output Flow]]
```

---

## File Descriptions

### `src/main.tsx` (~785KB, the monster file)

**Why it exists separately:** This is the CLI entry point. It handles ALL the startup complexity: parsing 40+ CLI flags, configuring auth, loading settings, choosing models, and branching between interactive mode (REPL), print mode (`-p`), and SDK mode.

**Key functions:**
- **Top-level code** (not a function): Registers Commander.js commands, parses CLI arguments
- **`logSessionTelemetry()`**: Logs skill/plugin telemetry for the session
- **Various action handlers**: Each CLI flag triggers a handler that may call `setup()`, `launchRepl()`, or `runHeadless()`

**What it calls:** Everything. `setup.ts`, `replLauncher.tsx`, `commands.ts`, `services/api/`, `services/mcp/`, `utils/auth/`, etc.

---

### `src/setup.ts`

**Why separate:** Isolates environment setup from CLI parsing. `main.tsx` decides *what* to do; `setup()` makes the environment *ready*.

**Key functions:**
- **`setup(cwd, permissionMode, ...)`**: The main setup function
  - Validates Node.js version
  - Starts UDS messaging server (for teammate communication)
  - Sets working directory
  - Captures hooks config snapshot (anti-tampering)
  - Creates worktree if requested
  - Initializes session memory
  - Launches background prefetch jobs

---

### `src/replLauncher.tsx`

**Why separate:** Keeps the REPL mounting logic isolated so `main.tsx` doesn't need React imports in its main logic.

**Key functions:**
- **`launchRepl(root, appProps, replProps, renderAndRun)`**: Dynamically imports `App` and `REPL` components, wraps them in the Ink root, and renders.

---

### `src/ink.ts`

**Why separate:** This is a re-export barrel file that wraps the custom Ink framework with theme support. Every component imports `Box`, `Text`, `useInput`, etc. from here.

**What it does:** Wraps all Ink `render()` and `createRoot()` calls with `ThemeProvider` so themed components work without manual wrapping at every call site.

**Exports:** `render()`, `createRoot()`, `Box`, `Text`, `useInput`, `useStdin`, `useApp`, etc.

---

### `src/ink/` directory

The custom Ink framework — a fork/customization of [Ink](https://github.com/vadimdemedes/ink) (React for CLI). This is a full React reconciler for terminal output.

| Subdirectory | Purpose |
|---|---|
| `ink/root.ts` | Create Ink root, render React tree to terminal |
| `ink/components/` | Box, Text, Button, Newline, Spacer, StdinContext |
| `ink/hooks/` | useInput, useApp, useStdin, useInterval, useTerminalViewport |
| `ink/layout/` | Yoga-based flexbox layout for terminal |
| `ink/termio/` | Terminal I/O: raw mode, escape sequences, OSC commands |
| `ink/events/` | Click events, input events, terminal focus events |

---

### `src/bootstrap/state.ts`

**Why separate:** Global mutable state for the session. This is the "shared brain" — session ID, CWD, model selection, permission mode, tool context, etc.

**Key getters/setters (all module-level state):**
- `getSessionId()` / `switchSession()`
- `getCwd()` / `setCwdState()`
- `getProjectRoot()` / `setProjectRoot()`
- `getInitialMainLoopModel()` / `setInitialMainLoopModel()`
- `getIsNonInteractiveSession()`
- `getCurrentTurnTokenBudget()`
- Various feature flag state

---

### `src/cli/` directory

| File | Purpose |
|---|---|
| `print.ts` | Print mode (`claude -p "query"`). Runs headless, no REPL. Streams output to stdout. |
| `structuredIO.ts` | Structured JSON output for SDK mode. Used by `claude --output-format json`. |
| `remoteIO.ts` | I/O handling for remote sessions (CCR/teleport). |
| `exit.ts` | Exit handlers: cleanup, flush analytics, save session costs. |
| `update.ts` | Auto-updater logic. Checks for new versions, prompts to update. |
| `transports/` | Communication transports: WebSocket, SSE, Hybrid, UDS. |

---

## Cross-References

- `main.tsx` → [[Tool System]] (calls `getTools()` to build the tool pool)
- `main.tsx` → [[Conversation Loop and State]] (launches REPL which drives the query loop)
- `setup.ts` → [[Services and Utilities]] (calls many service init functions)
- `ink.ts` → [[UI Components]] (provides rendering primitives)
