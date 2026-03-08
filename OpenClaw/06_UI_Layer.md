# OpenClaw UI Layer

## High-Level Summary

The OpenClaw UI layer provides the user interface for controlling and interacting with the Gateway. It consists of a web-based Control UI served by the Gateway (Vite + React-like architecture), terminal-based TUI components, and companion mobile apps for iOS, Android, and macOS. The web UI runs at `http://127.0.0.1:18789/` and provides channel management, session viewing, plugin configuration, and system diagnostics.

## Web Control UI

### Overview

The Control UI is a web application served by the Gateway's HTTP server. It provides a graphical interface for managing all aspects of OpenClaw.

### Technology Stack

- **Framework**: Vite (build tool)
- **UI Library**: React-like component system
- **Styling**: CSS with design system
- **State Management**: Client-side state

### Directory Structure

Location: `/workspace/ui/`

```
ui/
├── public/           # Static assets
├── src/             # React source code
├── index.html       # Entry HTML
├── package.json     # Dependencies
├── vite.config.ts   # Vite configuration
└── vitest.config.ts # Test configuration
```

### Vite Configuration

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:18789'
    }
  }
});
```

### Key UI Components

#### Dashboard
Main overview showing:
- Connected channels status
- Active sessions
- Recent messages
- System health

#### Channel Management
Interface for:
- Adding/removing channels
- Configuring channel settings
- Viewing channel health
- Testing connections

#### Session Viewer
Message browsing interface:
- Searchable message history
- Session details
- Participant information
- Message threading

#### Plugin Management
Plugin administration:
- Available plugins list
- Installation/uninstallation
- Configuration editor
- Status monitoring

#### Settings
System configuration:
- Security settings
- Notification preferences
- Display options
- API keys management

### HTTP Endpoints

The Control UI communicates with the Gateway via HTTP:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/channels` | List channels |
| `POST /api/channels/:id/enable` | Enable channel |
| `GET /api/sessions` | List sessions |
| `GET /api/sessions/:id/messages` | Session messages |
| `GET /api/plugins` | List plugins |
| `POST /api/plugins/:id/install` | Install plugin |
| `GET /api/config` | Get configuration |
| `POST /api/config` | Update configuration |

### Security

#### Control UI Authentication
- Token-based authentication
- Configurable token
- Session management

#### CORS Configuration
Content Security Policy for control UI.

### Mobile Responsiveness

The Control UI is responsive and works on:
- Desktop browsers
- Tablet browsers
- Mobile browsers (limited functionality)

## Terminal User Interface (TUI)

### Overview

OpenClaw includes terminal-based UI components for server operations.

### Progress Display

Location: `/workspace/src/terminal/progress-line.ts`

CLI progress indication:
- Spinner animations
- Progress bars
- Status messages

### Terminal Restore

Cleanup terminal state on exit:
- Restore cursor position
- Reset terminal modes
- Clear custom configurations

### Color Output

Terminal color support:
- ANSI color codes
- Theme-aware output
- Windows compatibility

## Companion Apps

### Overview

OpenClaw provides native companion apps for mobile and desktop platforms.

### macOS App

Location: `/workspace/apps/macos/`

Features:
- Native menu bar integration
- Voice input/output
- Screen sharing (via Peekaboo skill)
- System notifications
- Touch Bar support (if available)

### iOS App

Location: `/workspace/apps/ios/`

Features:
- Push notifications
- Voice input (Siri integration)
- Biometric authentication
- Background operation

### Android App

Location: `/workspace/apps/android/`

Features:
- Push notifications
- Voice input
- Material Design 3
- Background services

### Shared Kit

Location: `/workspace/apps/shared/OpenClawKit/`

Common code shared across platforms:
- Core business logic
- Shared types
- Platform-agnostic utilities

## Voice Interaction

### Voice Wake

OpenClaw supports voice wake activation:
- "Hey OpenClaw" detection
- Configurable wake words
- Background listening

### Voice Input

Speech-to-text processing:
- On-device processing (Sherpa ONNX)
- Cloud processing (Whisper API)

### Voice Output

Text-to-speech:
- On-device TTS (Sherpa ONNX TTS skill)
- Cloud TTS options

### Voice Call

Voice calling capability:
- `voice-call` extension
- `talk-voice` extension

## Canvas

### Overview

OpenClaw includes a live Canvas for visual workspace collaboration.

### Canvas Host

Location: `/workspace/src/canvas-host/`

Canvas server implementation:
- Real-time synchronization
- Drawing tools
- Image handling

### Canvas Capability

Location: `/workspace/src/gateway/canvas-capability.ts`

Agent-driven canvas tools:
- Drawing commands
- Image manipulation
- Collaborative editing

## CLI Interface

### Overview

The CLI provides command-line control of OpenClaw.

### Commands

| Command | Description |
|---------|-------------|
| `openclaw gateway` | Start Gateway server |
| `openclaw channels` | Channel management |
| `openclaw plugins` | Plugin management |
| `openclaw config` | Configuration |
| `openclaw onboard` | Onboarding wizard |
| `openclaw status` | System status |

### Onboarding

Location: `/workspace/src/wizard/`

Interactive setup wizard:
- Account creation
- Channel setup
- API key configuration

### Status Display

System status reporting:
- Running services
- Connected channels
- Resource usage

## Design System

### Styling

Design tokens:
- Colors
- Typography
- Spacing
- Shadows
- Animations

### Responsive Design

Breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Accessibility

- Keyboard navigation
- Screen reader support
- High contrast mode

## Diagnostics UI

### Health Monitoring

System health interface:
- CPU usage
- Memory usage
- Network status
- Error logs

### Debug Interface

Development-focused UI:
- Request inspection
- Response debugging
- Performance profiling

## Related Sections

- [[05_Core_Runtime]] - Gateway server
- [[03_Extensions]] - Channel management via extensions
- [[04_Skills]] - Tools available via UI
- [[01_Architecture]] - System architecture
