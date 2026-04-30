# Services and Utilities

> Supporting infrastructure: API calls, compaction, analytics, settings, and the vast `utils/` directory.

---

## Services Layer (`src/services/`)

### API Communication (`services/api/`)

| File | Purpose |
|---|---|
| `claude.ts` | Main API client. `callModel()` streams responses from Anthropic API. Handles retries, fallbacks, usage tracking. |
| `bootstrap.ts` | Fetch initial configuration from API on startup |
| `filesApi.ts` | Upload/download session files |
| `errors.ts` | API error classification (rate limit, prompt-too-long, auth) |
| `withRetry.ts` | Retry logic for transient API failures |
| `logging.ts` | API request/response logging |
| `dumpPrompts.ts` | Dump prompts for debugging (ant-only) |

### Context Compaction (`services/compact/`)

| File | Purpose |
|---|---|
| `autoCompact.ts` | Automatically compact when approaching context limits. Returns summary messages. |
| `compact.ts` | Core compaction logic. Summarizes conversation into shorter form. |
| `reactiveCompact.ts` | Compact in response to prompt-too-long errors (reactive rather than proactive) |
| `snipCompact.ts` | Remove old verbose tool results (cheapest form of context reduction) |
| `snipProjection.ts` | Project snip results for analysis |

**Compaction hierarchy** (cheapest to most expensive):
1. **Snip** — Remove old tool output
2. **Microcompact** — Cache-editing compaction
3. **Context collapse** — Archive granular messages into summaries
4. **Auto-compact** — Full conversation summary via API call
5. **Reactive compact** — Emergency compaction after API error

### MCP (Model Context Protocol) (`services/mcp/`)

| File | Purpose |
|---|---|
| `client.ts` | MCP client manager. Connects to MCP servers, discovers tools/resources. |
| `config.ts` | Parse MCP server configurations from settings |
| `types.ts` | MCP type definitions |
| `officialRegistry.ts` | Official MCP server registry |
| `claudeai.ts` | Claude.ai MCP config fetching |

### Analytics (`services/analytics/`)

| File | Purpose |
|---|---|
| `index.ts` | `logEvent()` — the main analytics function |
| `growthbook.ts` | Feature flag system (GrowthBook integration) |
| `config.ts` | Analytics configuration |
| `sink.ts` | Analytics event sink |

### Other Services

| Service | Purpose |
|---|---|
| `services/extractMemories/` | Extract and store memories from conversations |
| `services/SessionMemory/` | Session-scoped memory management |
| `services/PromptSuggestion/` | Suggest prompts based on context |
| `services/AgentSummary/` | Summarize agent task results |
| `services/MagicDocs/` | Document processing |
| `services/lsp/` | Language Server Protocol manager |
| `services/oauth/` | OAuth authentication flow |
| `services/plugins/` | Plugin lifecycle management |
| `services/policyLimits/` | Enterprise policy enforcement |
| `services/remoteManagedSettings/` | Remote settings management |
| `services/settingsSync/` | Settings synchronization across devices |
| `services/teamMemorySync/` | Team memory synchronization |
| `services/tips/` | Tip registry and display |
| `services/toolUseSummary/` | Generate tool use summaries |
| `services/tools/` | Tool execution infrastructure (see [[Tool System]]) |

---

## Utilities (`src/utils/`)

The largest directory (~300 files). Key areas:

### Input Processing

| File | Purpose |
|---|---|
| `processUserInput/processUserInput.ts` | Main input processor — detects commands, parses refs, handles images |
| `processUserInput/processTextPrompt.ts` | Process plain text prompts |
| `slashCommandParsing.ts` | Parse `/command` syntax |
| `handlePromptSubmit.ts` | Handle prompt submission logic |
| `attachments.ts` | Build attachment messages (memory, skills, file changes) |

### Message Handling

| File | Purpose |
|---|---|
| `messages.ts` (193KB!) | Message creation, normalization, formatting. The biggest util file. |
| `messages/mappers.ts` | Map messages to SDK-compatible formats |
| `messages/systemInit.ts` | Build system initialization messages |

### Model & Context

| File | Purpose |
|---|---|
| `model/model.ts` | Model selection, parsing, resolution |
| `model/modelCapabilities.ts` | Model capability detection |
| `model/modelStrings.ts` | Model display name strings |
| `model/providers.ts` | Cloud provider detection (Bedrock, Vertex, etc.) |
| `context.ts` | Context window management |
| `tokens.ts` | Token counting and estimation |
| `api.ts` | `prependUserContext()`, `appendSystemContext()` for API calls |

### Settings & Configuration

| File | Purpose |
|---|---|
| `config.ts` (63KB!) | Global/project settings management. `getGlobalConfig()`, `saveGlobalConfig()` |
| `settings/settings.ts` | Settings loading and validation |
| `settings/changeDetector.ts` | Detect and react to settings changes |
| `settings/mdm/` | Mobile Device Management settings |

### Git & GitHub

| File | Purpose |
|---|---|
| `git.ts` | Git operations (branch, status, diff, commit) |
| `github/` | GitHub integration (PR, issues, auth) |
| `githubRepoPathMapping.ts` | Map GitHub URLs to local paths |

### Permissions

| File | Purpose |
|---|---|
| `permissions/permissionSetup.ts` | Permission mode initialization |
| `permissions/PermissionUpdate.ts` | Apply permission changes |
| `permissions/filesystem.ts` | File permission rules |
| `permissions/PermissionMode.ts` | Mode types and constants |

### Hooks System

| File | Purpose |
|---|---|
| `hooks.ts` (159KB!) | Hook execution engine. Runs user-configured hooks at various lifecycle points. |
| `hooks/hookHelpers.ts` | Hook execution helpers |
| `hooks/fileChangedWatcher.ts` | Watch for file changes and trigger hooks |
| `hooks/postSamplingHooks.ts` | Hooks that run after model sampling |
| `hooks/hooksConfigSnapshot.ts` | Snapshot hooks config for anti-tampering |

### Other Key Utils

| File | Purpose |
|---|---|
| `sessionStorage.ts` (180KB!) | Session persistence, transcript recording, session search |
| `claudemd.ts` (46KB) | CLAUDE.md file loading and parsing |
| `auth.ts` (65KB) | Authentication (API keys, OAuth, AWS, GCP) |
| `teleport.tsx` (175KB) | Remote session teleportation |
| `worktree.ts` (50KB) | Git worktree management |
| `ide.ts` (46KB) | IDE integration (VS Code, JetBrains) |
| `forkedAgent.ts` | Fork agent for background tasks |
| `systemPrompt.ts` | Build the effective system prompt |
| `queryProfiler.ts` | Profile query execution timing |
| `gracefulShutdown.ts` | Clean shutdown with cleanup |
| `sandbox/` | Sandbox execution environment |
| `cronScheduler.ts` | Cron job scheduling |
| `earlyInput.ts` | Capture input before REPL is ready |
| `backgroundHousekeeping.ts` | Periodic cleanup tasks |
| `ultraplan/` | Advanced planning system |

---

## Cross-References

- `services/api/` → [[The Closed Loop - Input to Output Flow]] (Step 6b: API call)
- `services/compact/` → [[The Closed Loop - Input to Output Flow]] (Step 6a: Pre-flight)
- `services/mcp/` → [[Tool System]] (MCP tools are added to the tool pool)
- `utils/processUserInput/` → [[The Closed Loop - Input to Output Flow]] (Step 2)
- `utils/messages.ts` → [[The Closed Loop - Input to Output Flow]] (Step 3, 7)
