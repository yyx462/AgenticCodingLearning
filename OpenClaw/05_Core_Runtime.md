# OpenClaw Core Runtime

## High-Level Summary

The OpenClaw core runtime provides the foundational infrastructure that powers the entire system. Located in `/workspace/src/`, this layer encompasses the Gateway WebSocket server, channel management, session handling, configuration system, plugin infrastructure, and CLI. The runtime is written in TypeScript and provides both the server-side processing and the command-line interface for controlling the system.

## Core Runtime Files

### Entry Point

Location: `/workspace/src/entry.ts`

The main entry point initializes:
- Dotenv loading
- Environment variable normalization
- PATH setup for OpenClaw CLI
- Console capture
- Runtime support validation
- CLI program building and parsing

### Runtime Environment

Location: `/workspace/src/runtime.ts`

```typescript
export type RuntimeEnv = {
  log: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
  exit: (code: number) => void;
};

export const defaultRuntime: RuntimeEnv = {
  log: (...args) => { /* clear progress, log */ },
  error: (...args) => { /* clear progress, error */ },
  exit: (code) => { /* restore terminal, exit process */ }
};
```

## Gateway Server

### Overview

The Gateway is the central WebSocket server that handles all client connections and message routing. Located in `/workspace/src/gateway/`, it contains 234 files.

### Server Implementation

Location: `/workspace/src/gateway/server.impl.ts`

Key responsibilities:
- WebSocket server lifecycle
- Client connection management
- Message routing
- Channel coordination

### HTTP Server

Location: `/workspace/src/gateway/server-http.ts`

Provides:
- Control UI HTTP endpoints
- Health check endpoints
- Configuration reload endpoints
- Plugin HTTP registration

### WebSocket Runtime

Location: `/workspace/src/gateway/server-ws-runtime.ts`

Manages:
- WebSocket connection state
- Message streaming
- Client heartbeats
- Connection cleanup

### Server Methods

Location: `/workspace/src/gateway/server-methods.ts`

RPC methods available to clients:

```typescript
// Core methods
- sessions.send(message)
- sessions.list()
- sessions.history(id)
- channels.list()
- channels.send(...)
- agents.invoke(...)
- config.get()
- config.set()
- plugins.list()
- plugins.install(...)
- skills.list()
```

## Channel Layer

### Overview

The channel system (`/workspace/src/channels/`) handles message routing across 20+ platforms. Contains 63 files organized into:
- `transport/` - Transport abstractions
- `plugins/` - Platform plugins
- `telegram/`, `web/`, etc. - Platform-specific implementations

### Session Management

Location: `/workspace/src/channels/session.ts`

```typescript
interface Session {
  id: string;
  channelId: string;
  accountId: string;
  participants: Participant[];
  createdAt: Date;
  lastMessageAt: Date;
  metadata: Record<string, any>;
}
```

### Channel Registry

Location: `/workspace/src/channels/registry.ts`

Manages channel registration and lookup:

```typescript
class ChannelRegistry {
  channels: Map<string, Channel>;
  register(channel: Channel): void;
  get(id: string): Channel | undefined;
  list(): Channel[];
  unregister(id: string): void;
}
```

### Account Management

Location: `/workspace/src/channels/account-snapshot-fields.ts`

Tracks account state:
- Online/offline status
- Presence information
- Capabilities
- Connection health

### Message Handling

Key files for message processing:

| File | Purpose |
|------|---------|
| `typing.ts` | Typing indicator lifecycle |
| `ack-reactions.ts` | Message acknowledgment |
| `thread-binding-id.ts` | Thread management |
| `reply-prefix.ts` | Reply formatting |

## Plugin System

### Overview

The plugin system (`/workspace/src/plugins/`) provides extensibility through dynamic plugin loading. Contains 65 files.

### Plugin Discovery

Location: `/workspace/src/plugins/discovery.ts`

Discovers available plugins:
- Scans plugin directories
- Reads manifest files
- Validates compatibility

### Plugin Loader

Location: `/workspace/src/plugins/loader.ts`

Dynamic plugin loading:
- Imports plugin modules
- Initializes plugin context
- Registers with system

### Plugin Lifecycle

Location: `/workspace/src/plugins/install.ts`, `uninstall.ts`, `update.ts`

- **Installation**: Download, validate, install dependencies
- **Loading**: Instantiate, call register(), initialize
- **Update**: Version check, download, migrate, restart
- **Uninstallation**: Stop, cleanup, remove files

### Hook System

Location: `/workspace/src/plugins/hooks.ts`

Plugin hooks for lifecycle events:

```typescript
interface Hook {
  name: string;
  phase: 'pre' | 'post';
  handler: (context: HookContext) => Promise<void>;
}

// Available hooks:
// - before-agent-start
// - after-agent-finish
// - before-tool-call
// - after-tool-call
// - before-message-send
// - after-message-receive
```

### Configuration Schema

Location: `/workspace/src/plugins/config-schema.ts`

Zod-based schema validation for plugin configs.

## Configuration System

### Configuration Storage

Location: `/workspace/src/config/`

- JSON-based configuration
- Hot reload support
- Environment variable interpolation

### Config Location

Default: `~/.openclaw/openclaw.json`

### Runtime Config

Location: `/workspace/src/gateway/server-runtime-config.ts`

Hot-reloadable runtime configuration:
- Channel settings
- Agent parameters
- Security settings

### Config Reload

Location: `/workspace/src/gateway/config-reload.ts`

Graceful configuration updates without restart.

## Session Management

### Session Store

Location: `/workspace/src/sessions/`

Persistent session storage:
- Message history
- User preferences
- State snapshots

### Session Resolution

Location: `/workspace/src/gateway/sessions-resolve.ts`

Maps incoming messages to sessions:
- Channel + account + thread
- User identity
- Time-based rules

## Security

### Authentication

Location: `/workspace/src/gateway/auth.ts`

Multiple auth modes:
- Token-based (default)
- OAuth flows
- Browser-based (for control UI)

### Rate Limiting

Location: `/workspace/src/gateway/auth-rate-limit.ts`

- Per-user rate limits
- Per-IP rate limits
- Configurable thresholds

### Credential Management

Location: `/workspace/src/gateway/credentials.ts`

Secure credential storage and retrieval.

### Origin Checking

Location: `/workspace/src/gateway/origin-check.ts`

CORS and origin validation for HTTP endpoints.

## Memory System

### Core Memory

Location: `/workspace/src/memory/`

- Session-based memory
- Context window management
- History management

### Memory Extensions

| Extension | Purpose |
|-----------|---------|
| `memory-core` | Core memory API |
| `memory-lancedb` | LanceDB vector storage |

## CLI System

### CLI Entry

Location: `/workspace/src/cli/`

Commands:
- `openclaw gateway` - Start Gateway server
- `openclaw channels` - Channel management
- `openclaw plugins` - Plugin management
- `openclaw config` - Configuration
- `openclaw onboard` - Onboarding wizard

### Progress Display

Location: `/workspace/src/terminal/progress-line.ts`

Consistent CLI progress indication.

## Providers

### LLM Provider Integration

Location: `/workspace/src/providers/`

Supported providers:
- OpenAI
- Anthropic
- Google Gemini
- Ollama
- And others

### Provider Configuration

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-...",
      "model": "gpt-4"
    }
  }
}
```

## Event System

### Gateway Events

Location: `/workspace/src/gateway/events.ts`

Event types:
- `client.connect`
- `client.disconnect`
- `message.received`
- `message.sent`
- `agent.started`
- `agent.finished`
- `channel.status`

### Event Broadcasting

Location: `/workspace/src/gateway/server-broadcast.ts`

Broadcast events to connected clients.

## Cron System

### Scheduled Tasks

Location: `/workspace/src/cron/`

- Periodic maintenance
- Scheduled messages
- Health checks

### Cron Implementation

Location: `/workspace/src/gateway/server-cron.ts`

Cron job management within Gateway.

## Browser Integration

### Browser Automation

Location: `/workspace/src/browser/`

- Headless browser for web channels
- Session management
- DOM interaction

## Data Flow

```
User Message (Platform)
    ↓
Extension (Channel Handler)
    ↓
Channel Layer (Normalization)
    ↓
Session Resolution
    ↓
Agent Processing
    ↓
Tool Invocation (Skills)
    ↓
LLM Provider
    ↓
Response Generation
    ↓
Channel Layer (Formatting)
    ↓
Extension (Platform Adapter)
    ↓
User (Platform)
```

## Related Sections

- [[01_Architecture]] - System-level architecture
- [[03_Extensions]] - Platform integrations
- [[04_Skills]] - Tool capabilities
- [[02_Agents]] - Agent implementation
- [[06_UI_Layer]] - Control UI
