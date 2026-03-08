# OpenClaw Extensions System

## High-Level Summary

OpenClaw's extension system provides the integration layer for connecting to 20+ messaging platforms and adding extensibility features. Extensions are self-contained plugins located in the `/workspace/extensions/` directory, each following a standard plugin architecture with registration, configuration, and runtime management capabilities. This system enables OpenClaw to serve as a universal gateway bridging multiple communication channels to AI agents.

## Extension Architecture

### Directory Structure

Location: `/workspace/extensions/`

The extensions directory contains 40 extensions organized into categories:

```
extensions/
├── acpx              # Apple Continuity protocol
├── bluebubbles       # iMessage on Mac
├── copilot-proxy     # GitHub Copilot integration
├── device-pair       # Mobile device pairing
├── diagnostics-otel  # Observability
├── diffs             # Diff viewing
├── discord           # Discord chat
├── feishu           # Lark/Feishu (Chinese enterprise)
├── google-gemini-cli-auth  # Google auth
├── googlechat       # Google Chat
├── imessage         # Apple iMessage
├── irc              # Internet Relay Chat
├── line             # LINE messaging
├── llm-task         # LLM task execution
├── lobster          # Lobste.rs integration
├── matrix           # Matrix protocol
├── mattermost       # Mattermost
├── memory-core      # Core memory system
├── memory-lancedb   # LanceDB memory backend
├── minimax-portal-auth  # Minimax auth
├── msteams          # Microsoft Teams
├── nextcloud-talk   # Nextcloud Talk
├── nostr            # Nostr decentralized
├── open-prose       # Prose editor
├── phone-control    # Phone control
├── qwen-portal-auth # Qwen auth
├── shared           # Shared utilities
├── signal           # Signal messenger
├── slack            # Slack
├── synology-chat    # Synology Chat
├── talk-voice       # Voice talk
├── telegram         # Telegram
├── test-utils      # Testing utilities
├── thread-ownership # Thread management
├── tlon            # Tlon platform
├── twitch          # Twitch chat
├── voice-call      # Voice calling
├── whatsapp        # WhatsApp
├── zalo            # Zalo (Vietnamese)
└── zalouser        # Zalo user features
```

### Extension Structure Pattern

Each extension follows a consistent structure:

```
extensions/<extension-name>/
├── src/                    # Implementation source
├── index.ts                # Entry point with register()
├── openclaw.plugin.json    # Plugin manifest
└── package.json            # Node.js dependencies
```

### Plugin Manifest (openclaw.plugin.json)

```json
{
  "id": "slack",
  "name": "Slack",
  "version": "1.0.0",
  "description": "Slack messaging integration",
  "main": "index.js",
  "scripts": {
    "build": "tsc",
    "test": "vitest"
  }
}
```

## Messaging Platform Integrations

OpenClaw supports 20 messaging platform integrations:

### Direct Messaging Platforms

| Platform | Extension | Protocol |
|----------|-----------|----------|
| WhatsApp | `whatsapp` | WhatsApp Web Protocol |
| Telegram | `telegram` | Bot API |
| Discord | `discord` | Discord Bot API |
| Slack | `slack` | Slack Web API / RTM |
| Signal | `signal` | Signal Protocol |
| iMessage | `imessage`, `bluebubbles` | AppleMessages, BlueBubbles |
| SMS | `phone-control` | Carrier APIs |

### Enterprise Platforms

| Platform | Extension | Notes |
|----------|-----------|-------|
| Microsoft Teams | `msteams` | Bot Framework |
| Google Chat | `googlechat` | Google Chat API |
| Slack | `slack` | Enterprise features |
| Mattermost | `mattermost` | Self-hosted |
| Nextcloud Talk | `nextcloud-talk` | Self-hosted |
| Synology Chat | `synology-chat` | Synology NAS |

### Decentralized/Alternative Platforms

| Platform | Extension | Protocol |
|----------|-----------|----------|
| Matrix | `matrix` | Matrix Protocol |
| Nostr | `nostr` | Nostr Protocol |
| IRC | `irc` | IRC Protocol |
| LINE | `line` | LINE Messaging API |
| Feishu | `feishu` | Feishu Open API |
| Zalo | `zalo` | Zalo API |
| Twitch | `twitch` | Twitch Chat |

### Specialty Platforms

| Platform | Extension | Purpose |
|----------|-----------|---------|
| Tlon | `tlon` | Urbit-based communication |
| Lobste.rs | `lobster` | News aggregator |

## Extension Registration Pattern

### Entry Point (index.ts)

```typescript
import { SlackPlugin } from './src/plugin';

export default {
  id: 'slack',
  name: 'Slack',
  description: 'Slack messaging integration for OpenClaw',
  configSchema: z.object({
    botToken: z.string(),
    signingSecret: z.string(),
    appToken: z.string().optional(),
  }),
  register(api: OpenClawPluginApi) {
    api.registerChannel(new SlackPlugin(api.runtime));
    if (api.runtime) {
      api.runtime.setSlackRuntime(api.runtime);
    }
  }
};
```

### OpenClawPluginApi Interface

The plugin API provides:

```typescript
interface OpenClawPluginApi {
  runtime: OpenClawRuntime;
  registerChannel(channel: ChannelPlugin): void;
  registerTool(tool: Tool): void;
  registerHook(hook: Hook): void;
  getConfig<T>(key: string): T;
  setConfig(key: string, value: any): void;
  getLogger(): Logger;
}
```

## Channel Plugin Implementation

### Channel Interface

Extensions implementing messaging platforms must implement the ChannelPlugin interface:

```typescript
interface ChannelPlugin {
  readonly id: string;
  readonly name: string;
  start(): Promise<void>;
  stop(): Promise<void>;
  sendMessage(session: Session, message: Message): Promise<void>;
  onMessage(handler: MessageHandler): void;
  uploadMedia(session: Session, media: Media): Promise<string>;
  setTyping(session: Session, typing: boolean): Promise<void>;
}
```

### Message Normalization

Extensions normalize platform-specific messages into OpenClaw's unified format:

```typescript
interface NormalizedMessage {
  id: string;
  sessionId: string;
  channelId: string;
  sender: SenderIdentity;
  content: MessageContent;
  timestamp: Date;
  metadata: Record<string, any>;
}
```

## Authentication Mechanisms

### Platform-Specific Auth

Extensions implement various authentication methods:

#### OAuth2 Flows
- Slack: `oauth2/access_token` exchange
- Discord: OAuth2 bot authorization
- Google Chat: Service account / OAuth

#### Bot Tokens
- Telegram: Bot API token
- Discord: Bot token
- Slack: Bot user OAuth token

#### Session-Based
- WhatsApp: QR code session
- iMessage: Apple ID credentials

### Auth Extensions

Specialized auth extensions:

| Extension | Purpose |
|-----------|---------|
| `google-gemini-cli-auth` | Google/Gemini authentication |
| `minimax-portal-auth` | Minimix platform auth |
| `qwen-portal-auth` | Qwen/Alibaba auth |

## Memory Extensions

### memory-core

Core memory system providing:
- Session-based memory storage
- Context window management
- Conversation history
- Semantic search interface

### memory-lancedb

LanceDB backend for memory:
- Vector similarity search
- Persistent storage
- Efficient querying
- Embedding generation

## Utility Extensions

### diagnostics-otel

OpenTelemetry integration for observability:
- Trace propagation
- Metric collection
- Log aggregation
- Performance monitoring

### device-pair

Mobile device pairing for companion apps:
- Secure pairing protocol
- Token management
- Device metadata
- Connection lifecycle

### test-utils

Testing utilities for extension development:
- Mock implementations
- Test fixtures
- Assertion helpers

## Plugin Lifecycle Management

For detailed plugin lifecycle implementation, see [[05_Core_Runtime]].

### Installation

1. Validate plugin manifest
2. Download plugin package
3. Install dependencies
4. Run post-install scripts
5. Register with plugin registry

### Loading

1. Discover available plugins
2. Load plugin manifest
3. Validate configuration schema
4. Instantiate plugin
5. Call register() with API

### Runtime Management

- Plugin state tracking
- Resource allocation
- Health monitoring
- Graceful shutdown

### Updates

1. Check for new versions
2. Download updated package
3. Run migration scripts
4. Restart plugin

### Uninstallation

1. Stop plugin gracefully
2. Clean up resources
3. Remove configuration
4. Delete plugin files

## Hook System Integration

Extensions can register hooks to intercept various events:

```typescript
register(api: OpenClawPluginApi) {
  api.registerHook({
    name: 'before-message',
    phase: 'pre-process',
    handler: async (message) => {
      return message;
    }
  });
}
```

Available hook phases:
- `pre-process`: Before message processing
- `post-process`: After response generation
- `before-send`: Before sending to platform
- `after-receive`: After receiving from platform

For hook architecture, see [[01_Architecture]]. For hook runtime, see [[05_Core_Runtime]].

## Configuration Schema

Extensions define configuration schemas for validation:

```typescript
const configSchema = z.object({
  botToken: z.string().min(1),
  signingSecret: z.string().min(1),
  appToken: z.string().optional(),
  teamId: z.string().optional(),
  timeout: z.number().default(30000),
  retryAttempts: z.number().default(3),
});
```

## Extension Development Guidelines

### Best Practices

1. **Follow the plugin pattern**: Use consistent register/interface structure
2. **Validate configuration**: Use Zod schemas for config validation
3. **Handle errors gracefully**: Implement retry and fallback logic
4. **Log appropriately**: Use the provided logger for debugging
5. **Clean up resources**: Properly implement stop() for graceful shutdown

### Testing

Extensions should include:
- Unit tests for core logic
- Integration tests with mock Gateway
- E2E tests with real platform APIs (where possible)

## Version Management

Extensions declare version compatibility:

```json
{
  "engines": {
    "openclaw": ">=1.0.0 <2.0.0"
  }
}
```

The Gateway validates version compatibility before loading extensions.

## Related Sections

- [[06_UI_Layer]] - Channel message handling via Control UI
- [[05_Core_Runtime]] - Gateway server and extension loading
- [[01_Architecture]] - Plugin architecture
- [[04_Skills]] - Tool capabilities
