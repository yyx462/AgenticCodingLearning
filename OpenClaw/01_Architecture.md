# OpenClaw Architecture Overview

## High-Level Summary

OpenClaw is a self-hosted personal AI assistant gateway that connects multiple messaging platforms (WhatsApp, Telegram, Discord, iMessage, Slack, and 20+ others) to AI coding agents. The architecture follows a modular monorepo structure using pnpm workspaces, with TypeScript as the primary language. The system provides a Gateway as its control plane, companion apps for macOS/iOS/Android, voice interaction capabilities, and a live Canvas for visual workspace collaboration.

## Core Architectural Components

### Monorepo Structure

The OpenClaw repository is organized as a pnpm monorepo with the following top-level structure:

```
openclaw/
├── .agent/           # Agent workflow configurations
├── .agents/          # Agent definitions
├── apps/             # Platform-specific applications
├── docs/             # Documentation (Mintlify-based)
├── extensions/       # Plugin extensions for messaging platforms
├── packages/         # Shared internal packages
├── skills/           # Configurable skill modules (52 skills)
├── src/              # Core source code (48 subdirectories)
├── ui/               # User interface components (Vite-based)
├── vendor/           # External dependencies
├── scripts/          # Build and utility scripts
└── test/             # Test files
```

### Technology Stack

- **Runtime**: Node.js 22+
- **Language**: TypeScript (primary), Swift (macOS/iOS), Kotlin (Android)
- **Build Tools**: pnpm (package manager), Vite (frontend), Turborepo concepts
- **Testing**: Vitest (multiple configurations: unit, e2e, channels, extensions, gateway, live, scoped)
- **Container**: Docker, docker-compose
- **UI Framework**: Custom TUI + Web components

## Key Module Relationships

### Gateway (src/gateway/)

The Gateway is the central control plane managing all incoming and outgoing communications. Located in `/workspace/src/gateway/`, it contains 234 files organized into:

- **server/** - WebSocket server implementation
- **protocol/** - Communication protocols
- **server-methods/** - RPC method definitions

Key files:
- `server.ts` - Main Gateway entry point
- `server.impl.ts` - Server implementation details
- `server-http.ts` - HTTP endpoints for control UI
- `server-channels.ts` - Channel management
- `server-chat.ts` - Chat session handling
- `ws-runtime.ts` - WebSocket runtime state

For Gateway implementation details, see [[05_Core_Runtime]].

### Channel Layer (src/channels/)

The channel system handles message routing across 20+ platforms. Located in `/workspace/src/channels/`, it contains:

- **transport/** - Transport layer abstractions
- **plugins/** - Platform-specific plugins
- **telegram/**, **web/**, and other platform directories

Key components:
- `session.ts` - Session management
- `registry.ts` - Channel registry
- `account-snapshot-fields.ts` - Account state tracking
- `typing.ts` - Typing indicator lifecycle

### Plugin System (src/plugins/)

The plugin system extends OpenClaw functionality. Located in `/workspace/src/plugins/`, it includes:

- `loader.ts` - Dynamic plugin loading
- `discovery.ts` - Plugin discovery
- `install.ts` / `uninstall.ts` - Plugin lifecycle management
- `hooks.ts` - Hook system for plugin integration
- `registry.ts` - Plugin registry
- `config-schema.ts` - Configuration validation

For plugin runtime lifecycle details, see [[05_Core_Runtime]].

### Runtime Core (src/)

The core runtime (`/workspace/src/`) provides foundational services:

| Directory | Purpose |
|-----------|---------|
| `runtime.ts` | Process runtime environment management |
| `agents/` | Agent definitions and management |
| `cli/` | Command-line interface |
| `config/` | Configuration management |
| `memory/` | Memory/persistence layer |
| `secrets/` | Secret management |
| `sessions/` | Session state management |
| `providers/` | LLM provider integrations |

## Data Flow Architecture

### Message Flow

1. **Inbound**: External message arrives via platform-specific extension (e.g., Slack, WhatsApp)
2. **Channel Processing**: Channel layer normalizes message format, applies gating/allowlist policies
3. **Session Resolution**: Session registry maps message to appropriate session context
4. **Agent Processing**: Message routed to active agent for processing
5. **Tool Execution**: Agent invokes tools (skills) as needed
6. **Response Generation**: LLM generates response
7. **Outbound**: Response sent back through channel layer to originating platform

### Configuration Flow

1. User modifies `~/.openclaw/openclaw.json` or uses CLI
2. Configuration reload triggered via hot reload mechanism
3. Gateway receives configuration patch
4. Affected components (channels, plugins, agents) reconfigure
5. State preserved where possible

## Extension Points

### Extension Architecture

Extensions are plugins that integrate messaging platforms. Each extension in `/workspace/extensions/` follows a standard structure:

```
extensions/<name>/
├── src/                    # Implementation
├── index.ts                # Entry point with register() function
├── openclaw.plugin.json    # Plugin manifest
└── package.json            # Dependencies
```

The registration pattern:
```typescript
export default {
  id: 'slack',
  name: 'Slack',
  description: 'Slack messaging integration',
  configSchema: z.object({...}),
  register(api: OpenClawPluginApi) {
    api.registerChannel(slackPlugin);
  }
};
```

For detailed extension implementation, see [[03_Extensions]].

### Skills Architecture

Skills in `/workspace/skills/` provide tool capabilities. Each skill is a directory containing `SKILL.md` that defines the skill's capabilities. There are 52 skills organized by category:

- **Productivity**: notion, obsidian, bear-notes, apple-notes, trello, canvas
- **Communication**: slack, discord, telegram, whatsapp, signal, imessage
- **Media**: spotify-player, sonoscli, video-frames, camsnap
- **AI/ML**: coding-agent, gemini, openai-image-gen, openai-whisper
- **Developer**: github, tmux, gog, eightctl

For skills details, see [[04_Skills]].

## Deployment Architecture

### Local Deployment

```
┌─────────────────────────────────────────────────┐
│                 OpenClaw Gateway                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Channel │  │ Channel │  │ Channel │  ...   │
│  │ Handler │  │ Handler │  │ Handler │        │
│  └─────────┘  └─────────┘  └─────────┘        │
│         │            │            │             │
│  ┌──────────────────────────────────────┐      │
│  │         Agent Runtime                │      │
│  │  ┌────────┐  ┌────────┐             │      │
│  │  │ Skills │  │ Tools  │             │      │
│  │  └────────┘  └────────┘             │      │
│  └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
         │
    WebSocket
         │
┌─────────────────────────────────────────────────┐
│              Control UI (Web)                    │
│          http://127.0.0.1:18789/                │
└─────────────────────────────────────────────────┘
```

### Multi-Node Deployment

OpenClaw supports distributed deployments:
- **Gateway Server**: Main control plane (Node.js)
- **Mobile Nodes**: iOS and Android companion apps
- **macOS Agent**: Native voice and screen interaction

## Security Architecture

### Authentication

- Token-based authentication for control UI
- OAuth flows for platform integrations (Slack, Discord, etc.)
- Device pairing for mobile nodes
- Secret management via encrypted configuration

### Network Security

- Origin checking for HTTP endpoints
- CORS policies for control UI
- Rate limiting on authentication endpoints
- Webhook signature verification

## Configuration Management

Configuration is stored in `~/.openclaw/openclaw.json` with support for:

- **Channels**: Platform-specific credentials and settings
- **Plugins**: Extension configurations
- **Agents**: Agent behavior customization
- **Security**: Tokens, allowlists, rate limits

Runtime configuration is hot-reloadable via the Gateway's configuration reload system.

## Cross-Component Integration

### WebSocket Protocol

The Gateway communicates with clients via WebSocket:
- `server-ws-runtime.ts` - WebSocket runtime
- Bidirectional message streaming
- Event-based notifications (agent events, channel status)

### Hook System

The plugin hook system (`src/plugins/hooks.ts`) allows extensions to intercept:
- Before/after agent start
- Before/after tool calls
- Message incoming/outgoing
- Session lifecycle events

For hook runtime implementation, see [[05_Core_Runtime]].

### IPC Mechanisms

- **Direct imports**: Internal packages share code via TypeScript imports
- **Plugin API**: Extensions use `OpenClawPluginApi` for integration
- **CLI commands**: User-facing commands in `src/cli/`

## Related Sections

- [[05_Core_Runtime]] - Gateway implementation details
- [[03_Extensions]] - Platform integrations
- [[04_Skills]] - Skills architecture
- [[02_Agents]] - Agent system overview
