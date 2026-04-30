# Tool System

> How Claude Code defines, registers, and executes tools. The bridge between the model and your filesystem/terminal.

---

## Core Files

### `src/Tool.ts` — Tool Interface

**Why separate:** Defines the universal `Tool` type that every tool implementation conforms to. This is the contract.

**Key types:**
- **`Tool<T>`**: Generic tool with input/output schemas, call method, and metadata
- **`ToolDef<T>`**: Partial definition that `buildTool()` completes with defaults
- **`ToolUseContext`**: Context passed to every tool call (permissions, file cache, messages, abort controller)

**Key functions:**
- **`buildTool(def)`**: Factory that applies defaults (`isEnabled: true`, `isConcurrencySafe: false`, `isReadOnly: false`)
- **`findToolByName(tools, name)`**: Search tool list by name
- **`toolMatchesName(tool, name)`**: Match by name or alias

---

### `src/tools.ts` — Tool Registry

**Why separate:** Central registry that assembles the available tool pool. Tools are filtered by permission mode and feature flags.

**Key functions:**
- **`getAllBaseTools()`**: Returns all built-in tools (respects feature flags)
- **`getTools(permissionContext, mode)`**: Filters tools by permission mode and simple/full mode
- **`filterToolsByDenyRules(tools, rules)`**: Removes tools denied by permission rules
- **`assembleToolPool(builtInTools, mcpTools, agentTools)`**: Combines built-in + MCP + agent tools
- **`getMergedTools(...)`**: Gets combined tool list for the current session

---

### `src/services/tools/toolOrchestration.ts` — Execution Engine

**Why separate:** Handles the actual execution of tool calls. Manages concurrency: read-only tools run in parallel, write tools run serially.

**Key function:**
- **`runTools(toolUseBlocks, assistantMessages, canUseTool, toolUseContext)`**: Async generator that:
  1. Partitions tools into concurrent-safe (read-only) and serial (write) batches
  2. Runs read-only batch concurrently
  3. Runs write batch serially
  4. Yields `MessageUpdate` for each result

### `src/services/tools/toolExecution.ts`

- **`runToolUse(toolBlock, canUseTool, toolUseContext)`**: Execute a single tool call with permission check

### `src/services/tools/StreamingToolExecutor.ts`

- Starts tool execution *while the model is still streaming*. If the model emits multiple tool_use blocks, they begin executing as each arrives rather than waiting for the full response.

---

## Tool Implementations (`src/tools/`)

| Tool | Directory | What it does |
|---|---|---|
| **BashTool** | `tools/BashTool/` | Execute shell commands with sandboxing, timeout, background mode |
| **FileReadTool** | `tools/FileReadTool/` | Read files (text, images, PDFs, notebooks) with pagination |
| **FileEditTool** | `tools/FileEditTool/` | Modify files with staleness checking and atomic edits |
| **FileWriteTool** | `tools/FileWriteTool/` | Create new files |
| **GrepTool** | `tools/GrepTool/` | Search file contents with ripgrep, multiple output modes |
| **GlobTool** | `tools/GlobTool/` | Find files by name pattern |
| **AgentTool** | `tools/AgentTool/` | Spawn subagents (workers, teammates, explore agents) |
| **WebFetchTool** | `tools/WebFetchTool/` | Fetch and read web URLs |
| **WebSearchTool** | `tools/WebSearchTool/` | Search the web |
| **AskUserQuestionTool** | `tools/AskUserQuestionTool/` | Ask the user a question (multi-choice) |
| **TaskCreateTool** | `tools/TaskCreateTool/` | Create a tracked task |
| **TaskUpdateTool** | `tools/TaskUpdateTool/` | Update task status |
| **TaskListTool** | `tools/TaskListTool/` | List all tasks |
| **TaskGetTool** | `tools/TaskGetTool/` | Get task details |
| **TaskOutputTool** | `tools/TaskOutputTool/` | Get task output |
| **TaskStopTool** | `tools/TaskStopTool/` | Stop a running task |
| **EnterPlanModeTool** | `tools/EnterPlanModeTool/` | Switch to plan mode |
| **ExitPlanModeTool** | `tools/ExitPlanModeTool/` | Exit plan mode |
| **EnterWorktreeTool** | `tools/EnterWorktreeTool/` | Create and enter a worktree |
| **ExitWorktreeTool** | `tools/ExitWorktreeTool/` | Leave worktree |
| **SkillTool** | `tools/SkillTool/` | Invoke a skill/slash command |
| **SendMessageTool** | `tools/SendMessageTool/` | Continue an existing agent |
| **ScheduleCronTool** | `tools/ScheduleCronTool/` | Schedule recurring tasks |
| **LSPTool** | `tools/LSPTool/` | Language Server Protocol queries |
| **NotebookEditTool** | `tools/NotebookEditTool/` | Edit Jupyter notebook cells |
| **PowerShellTool** | `tools/PowerShellTool/` | Windows PowerShell commands |
| **ConfigTool** | `tools/ConfigTool/` | Read/modify Claude Code settings |
| **MCPTool** | `tools/MCPTool/` | Call MCP server tools |
| **BriefTool** | `tools/BriefTool/` | Brief mode for concise output |
| **SleepTool** | `tools/SleepTool/` | Sleep/delay (triggers queue drain) |

---

## Tool Lifecycle

```
1. Model emits tool_use block with { name, input, id }
2. StreamingToolExecutor.addTool() or runTools() receives it
3. findToolByName() locates the tool definition
4. canUseTool() checks permissions:
   ├── Auto-allow (read-only tools in trusted mode)
   ├── Needs approval → PermissionRequest.tsx renders dialog
   │   ├── User approves → tool.call() executes
   │   └── User denies → tool_result with error
   └── Denied by rule → tool_result with error
5. tool.call(input, toolUseContext) executes
6. Result wrapped as tool_result message
7. Yielded back to query.ts → added to state → next API call
```

---

## Shared Utilities (`src/tools/shared/`)

| File | Purpose |
|---|---|
| `spawnMultiAgent.ts` | Shared logic for spawning subagents/teammates. Backend detection, env building, tmux integration |
| `gitOperationTracking.ts` | Track git commands for analytics |

---

## Cross-References

- Called by: [[Conversation Loop and State#query.ts]] (the query loop invokes tools)
- Calls: [[Permission System]] (canUseTool checks)
- Calls: [[Services and Utilities#API]] (some tools make API calls)
- AgentTool spawns: [[Conversation Loop and State#Task System]] (background tasks)
