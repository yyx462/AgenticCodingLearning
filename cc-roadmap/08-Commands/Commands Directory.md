# Commands Directory

> Every slash command available in Claude Code, organized by category.

---

## Command Types

Commands can be:
- **`local`**: Returns text output directly
- **`local-jsx`**: Renders an Ink UI component
- **`prompt`**: Expands to text injected into the model prompt (these are "skills")

---

## Session Management

| Command | File | What it does |
|---|---|---|
| `/clear` | `commands/clear/` | Clear conversation history |
| `/compact` | `commands/compact/` | Manually trigger context compaction |
| `/resume` | `commands/resume/` | Resume a previous session |
| `/session` | `commands/session/` | Show QR code for remote session |
| `/rewind` | `commands/rewind/` | Undo recent messages |
| `/exit` | `commands/exit/` | Exit Claude Code |

## Project & Files

| Command | File | What it does |
|---|---|---|
| `/init` | `commands/init.js` | Initialize CLAUDE.md for project |
| `/add-dir` | `commands/add-dir/` | Add additional directory to context |
| `/files` | `commands/files/` | List tracked files |
| `/diff` | `commands/diff/` | Show file diffs |
| `/context` | `commands/context/` | Show current context window usage |

## Git & GitHub

| Command | File | What it does |
|---|---|---|
| `/commit` | `commands/commit.js` | Create a git commit |
| `/review` | `commands/review.js` | Review a PR |
| `/pr_comments` | `commands/pr_comments/` | View PR comments |
| `/branch` | `commands/branch/` | Branch management |
| `/install-github-app` | `commands/install-github-app/` | Install GitHub app |

## Configuration

| Command | File | What it does |
|---|---|---|
| `/config` | `commands/config/` | View/edit settings |
| `/model` | `commands/model/` | Switch AI model |
| `/permissions` | `commands/permissions/` | Manage permission rules |
| `/hooks` | `commands/hooks/` | Manage hooks |
| `/mcp` | `commands/mcp/` | Manage MCP servers |
| `/vim` | `commands/vim/` | Toggle vim mode |
| `/theme` | `commands/theme/` | Change terminal theme |
| `/keybindings` | `commands/keybindings/` | Manage keybindings |
| `/fast` | `commands/fast/` | Toggle fast mode |
| `/effort` | `commands/effort/` | Set reasoning effort level |

## Tools & Agents

| Command | File | What it does |
|---|---|---|
| `/agents` | `commands/agents/` | Manage custom agents |
| `/skills` | `commands/skills/` | List available skills |
| `/tasks` | `commands/tasks/` | List running background tasks |
| `/plugin` | `commands/plugin/` | Manage plugins |
| `/plan` | `commands/plan/` | Toggle plan mode |
| `/doctor` | `commands/doctor/` | Diagnose issues |

## Information

| Command | File | What it does |
|---|---|---|
| `/help` | `commands/help/` | Show help |
| `/cost` | `commands/cost/` | Show session cost |
| `/usage` | `commands/usage/` | Show usage statistics |
| `/status` | `commands/status/` | Show current status |
| `/stats` | `commands/stats/` | Show detailed stats |
| `/memory` | `commands/memory/` | View/manage memory files |

## Output & Sharing

| Command | File | What it does |
|---|---|---|
| `/export` | `commands/export/` | Export conversation |
| `/copy` | `commands/copy/` | Copy last response |
| `/share` | `commands/share/` | Share session |
| `/feedback` | `commands/feedback/` | Send feedback |
| `/output-style` | `commands/output-style/` | Change output format |

## Auth

| Command | File | What it does |
|---|---|---|
| `/login` | `commands/login/` | Log in to Anthropic |
| `/logout` | `commands/logout/` | Log out |
| `/upgrade` | `commands/upgrade/` | Upgrade plan |

## Misc

| Command | File | What it does |
|---|---|---|
| `/rename` | `commands/rename/` | Rename session title |
| `/voice` | `commands/voice/` | Voice mode |
| `/thinkback` | `commands/thinkback/` | Replay thinking |
| `/chrome` | `commands/chrome/` | Claude in Chrome integration |
| `/desktop` | `commands/desktop/` | Desktop app integration |
| `/ide` | `commands/ide/` | IDE integration |
| `/terminal-setup` | `commands/terminalSetup/` | Terminal configuration |
| `/release-notes` | `commands/release-notes/` | Show changelog |

---

## How Commands Are Loaded

1. `commands.ts` registers all built-in commands in a memoized `COMMANDS()` array
2. `getCommands(cwd)` merges: bundled skills + plugin skills + skill dir commands + workflow commands + plugin commands + built-in commands
3. Commands are filtered by `meetsAvailabilityRequirement()` (auth) and `isCommandEnabled()` (feature flags)
4. `processUserInput()` routes `/command` input to the matching command's handler
