# OpenClaw Concept Map

A cross-reference index for finding concepts across all documentation sections.

---

## Architecture & Infrastructure

### System Structure

- **[[01_Architecture|Monorepo Structure]]** - pnpm workspaces-based project organization
- **[[01_Architecture|Technology Stack]]** - Node.js 22+, TypeScript, Swift/Kotlin, pnpm, Vite
- **[[05_Core_Runtime|Runtime Core]]** - Foundational services

### Networking & Gateway

- **[[01_Architecture|Gateway Layer]]** - Central WebSocket control plane
  - Alias: Gateway
  - See also: [[05_Core_Runtime]]

- **[[05_Core_Runtime|Gateway Server]]** - WebSocket server implementation
  - Alias: WebSocket Gateway
  - See also: [[01_Architecture]]

- **[[05_Core_Runtime|HTTP Server]]** - Control UI HTTP endpoints
- **[[05_Core_Runtime|WebSocket Runtime]]** - Connection state, message streaming
- **[[05_Core_Runtime|Server Methods (RPC)]]** - RPC methods for sessions, channels, agents

### Plugin & Extension System

- **[[01_Architecture|Plugin System]]** - Dynamic extension loading
  - See also: [[03_Extensions]], [[05_Core_Runtime]]

- **[[01_Architecture|Extension Architecture]]** - Plugin pattern for integrations
  - See also: [[03_Extensions]]

- **[[03_Extensions|Plugin Manifest]]** - openclaw.plugin.json format
- **[[03_Extensions|Extension Registration Pattern]]** - register() function pattern
- **[[03_Extensions|OpenClawPluginApi Interface]]** - Plugin API interface
- **[[03_Extensions|ChannelPlugin Interface]]** - Messaging platform interface
- **[[03_Extensions|Messaging Platform Integrations]]** - 40 extensions for WhatsApp, Telegram, Discord, etc.
- **[[05_Core_Runtime|Plugin Lifecycle]]** - Installation, loading, update phases
- **[[05_Core_Runtime|Plugin Discovery]]** - Scanning directories, validating compatibility

### Security & Configuration

- **[[01_Architecture|Security Architecture]]** - Token-based auth, OAuth, rate limiting
  - See also: [[05_Core_Runtime]]

- **[[01_Architecture|Configuration Management]]** - JSON-based config
  - See also: [[05_Core_Runtime]]

- **[[05_Core_Runtime|Configuration System]]** - Hot reload, env var interpolation
- **[[03_Extensions|Configuration Schema]]** - Zod-based validation

---

## Agent System

### Core Agent Concepts

- **[[02_Agents|Agent Definitions]]** - Agent metadata in .agents/
- **[[02_Agents|Agent Core]]** - Lifecycle management, state machine
- **[[02_Agents|Agent Workflows]]** - Workflow configurations
- **[[02_Agents|Agent Lifecycle]]** - Startup, processing, shutdown phases
- **[[02_Agents|Custom Agents]]** - Creating custom agents

### Agent Interaction

- **[[02_Agents|Gateway Agent Integration]]** - Prompt templates, event handling
- **[[02_Agents|Agent Prompt System]]** - System prompts, conversation history
- **[[02_Agents|Agent Events]]** - agent_started, agent_thinking, agent_tool_calls
- **[[02_Agents|Message Routing]]** - Agent selection rules
- **[[02_Agents|Multi-Agent Support]]** - Isolated sessions, cross-agent communication
- **[[02_Agents|Session Isolation]]** - Per-agent independent state

### Agent Tools & Hooks

- **[[02_Agents|Tool Invocation Flow]]** - 6-step agent tool process
  - See also: [[04_Skills]], [[07_Tools]]

- **[[02_Agents|Agent Hooks]]** - before-agent-start, after-agent-finish
  - See also: [[05_Core_Runtime]]

---

## Channel & Messaging

### Channel Layer

- **[[01_Architecture|Channel Layer]]** - Message routing across platforms
  - See also: [[05_Core_Runtime]]

- **[[05_Core_Runtime|Channel Registry]]** - Channel registration and lookup
- **[[05_Core_Runtime|Account Management]]** - Online/offline, presence tracking
- **[[05_Core_Runtime|Message Handling]]** - Typing indicators, acknowledgments

### Session Management

- **[[05_Core_Runtime|Session Management]]** - Session interface and storage
  - See also: [[02_Agents]]

### Message Processing

- **[[03_Extensions|Message Normalization]]** - Unified message format
- **[[03_Extensions|Authentication Mechanisms]]** - OAuth2, bot tokens, session auth

---

## Skills System

### Skills Architecture

- **[[01_Architecture|Skills Architecture]]** - 52 skill modules overview
  - See also: [[04_Skills]]

- **[[04_Skills|Skill Architecture]]** - SKILL.md + src/index.ts pattern
- **[[04_Skills|SKILL.md Format]]** - Description, Capabilities, Usage, Examples
- **[[04_Skills|Skills Directory Structure]]** - /workspace/skills/ with 52 modules
- **[[04_Skills|Skills List]]** - Categories: Productivity, Communication, Media, AI/ML, Developer
- **[[04_Skills|Skills by Category]]** - notion, slack, spotify, github, etc.

### Skills Implementation

- **[[04_Skills|Skill Implementation Patterns]]** - Simple vs Complex skills
- **[[04_Skills|Skill Entry Point Pattern]]** - index.ts with Skill object
- **[[04_Skills|Skill Invocation Flow]]** - 5-step agent-to-skill flow
  - See also: [[02_Agents]]

- **[[04_Skills|Skill Lifecycle]]** - Discovery, Registration, Execution
- **[[04_Skills|Skill Development]]** - 5-step creation process
- **[[04_Skills|Skill Access Control]]** - Permission system
- **[[04_Skills|Error Handling]]** - SkillError codes

### Skills Configuration

- **[[04_Skills|Skill Configuration]]** - JSON config, env vars
- **[[04_Skills|Tool Definition]]** - name, description, parameters
  - See also: [[07_Tools]]

- **[[04_Skills|Parameter Schema]]** - Zod-based validation

---

## Tools & Capabilities

### Tool System

- **[[07_Tools|Tool Architecture]]** - Native, skill-based, plugin tools
- **[[07_Tools|Tool Registry]]** - Central tool management
  - See also: [[02_Agents]]

- **[[07_Tools|Tool Categories]]** - communication, productivity, developer, media, ai
- **[[07_Tools|Tool Discovery]]** - 6-step discovery process
- **[[07_Tools|Tool Catalog]]** - Tool definitions, categories, search
- **[[07_Tools|Tool Development]]** - 5-step creation process

### Tool Types

- **[[07_Tools|Native Tools]]** - echo, timestamp, random, evaluate
- **[[07_Tools|Channel Tools]]** - channel.send, channel.list, channel.info
- **[[07_Tools|Session Tools]]** - session.list, session.history, session.create
- **[[07_Tools|Skill-Based Tools]]** - github, notion, spotify tools
  - See also: [[04_Skills]]

- **[[07_Tools|Plugin-Provided Tools]]** - Extensions registering tools
- **[[07_Tools|HTTP Tools]]** - http.request, http.get, http.post

### Tool Operations

- **[[07_Tools|Tool Configuration]]** - Per-agent tool settings
- **[[07_Tools|Tool Permissions]]** - Fine-grained access control
- **[[07_Tools|Tool Execution Context]]** - Session, agent, channel context
- **[[07_Tools|Tool Result Format]]** - success, data, error, metadata
- **[[07_Tools|Tool Usage in Agents]]** - Agent tool selection
- **[[07_Tools|Tool Chains]]** - Chaining multiple tools
- **[[07_Tools|Performance (Timeouts/Caching)]]** - Configurable timeouts, TTL
- **[[07_Tools|Monitoring]]** - Usage tracking, success/failure rates

---

## UI Layer

### Web Control UI

- **[[06_UI_Layer|Web Control UI]]** - Gateway UI at http://127.0.0.1:18789/
  - Alias: Control UI

- **[[06_UI_Layer|Key UI Components]]** - Dashboard, Channel Management, Session Viewer
- **[[06_UI_Layer|HTTP Endpoints]]** - REST API: /api/channels, /api/sessions
- **[[06_UI_Layer|Control UI Security]]** - Token-based auth, CORS
- **[[06_UI_Layer|Design System]]** - Design tokens, colors, typography
- **[[06_UI_Layer|Mobile Responsiveness]]** - Responsive design

### Mobile & Desktop Apps

- **[[06_UI_Layer|Companion Apps]]** - macOS, iOS, Android apps
- **[[06_UI_Layer|macOS App]]** - Menu bar, voice, screen sharing
- **[[06_UI_Layer|iOS App]]** - Push notifications, Siri, biometric auth
- **[[06_UI_Layer|Android App]]** - Material Design 3, background services
- **[[06_UI_Layer|Shared Kit]]** - OpenClawKit cross-platform code

### Specialized UIs

- **[[06_UI_Layer|Terminal UI]]** - Progress display, color output
- **[[06_UI_Layer|Voice Interaction]]** - Speech-to-text, text-to-speech
- **[[06_UI_Layer|Canvas]]** - Live visual workspace collaboration
- **[[06_UI_Layer|Diagnostics UI]]** - Health monitoring, error logs
- **[[06_UI_Layer|CLI Interface]]** - Commands: gateway, channels, plugins
  - See also: [[05_Core_Runtime]]

---

## Core Runtime Services

### Runtime Environment

- **[[05_Core_Runtime|Core Runtime Files]]** - entry.ts, runtime.ts
- **[[05_Core_Runtime|Runtime Environment]]** - RuntimeEnv type with log, error, exit
- **[[05_Core_Runtime|Event System]]** - client.connect, message.received, agent.started
- **[[05_Core_Runtime|Cron System]]** - Scheduled maintenance

### Memory & Providers

- **[[05_Core_Runtime|Memory System]]** - Session-based memory, context window
  - See also: [[03_Extensions]]

- **[[03_Extensions|Memory Extensions]]** - memory-core, memory-lancedb
- **[[05_Core_Runtime|LLM Providers]]** - OpenAI, Anthropic, Gemini, Ollama

### CLI & Hooks

- **[[05_Core_Runtime|CLI System]]** - openclaw gateway, channels, plugins commands
  - See also: [[06_UI_Layer]]

- **[[01_Architecture|Hook System]]** - Plugin intercept system
  - See also: [[03_Extensions]], [[05_Core_Runtime]]

- **[[03_Extensions|Hook System Integration]]** - Message phase hooks

---

## Evolution & Community

### Project Overview

- **[[08_Evolution|Project History]]** - Single-channel to multi-platform evolution
- **[[08_Evolution|Evolution Timeline]]** - Versions 0.1.0 to 3.0.0
- **[[08_Evolution|Key Milestones]]** - 8 major milestones
- **[[08_Evolution|Core Vision]]** - Personal AI, local, private
- **[[08_Evolution|Design Principles]]** - Simplicity, extensibility, privacy
- **[[08_Evolution|Target Users]]** - Developers, power users, privacy-conscious

### Community & Development

- **[[08_Evolution|Community Model]]** - Designated maintainers
- **[[08_Evolution|Contribution Areas]]** - Core, Extensions, Skills, UI, Docs
- **[[08_Evolution|Development Workflow]]** - Issue reporting, PR workflow
- **[[08_Evolution|AGENTS.md Conventions]]** - Project-specific rules
- **[[08_Evolution|Community Resources]]** - GitHub Issues, Discussions

### Documentation & Releases

- **[[08_Evolution|Documentation Structure]]** - Mintlify-based docs
- **[[08_Evolution|Internationalization]]** - English, Japanese, Chinese
- **[[08_Evolution|Technology Evolution]]** - TypeScript, Swift, Kotlin, pnpm, Vite
- **[[08_Evolution|Key Architectural Decisions]]** - WebSocket Gateway, plugin system
- **[[08_Evolution|Version Management]]** - Semantic versioning
- **[[08_Evolution|Release Channels]]** - Stable, Beta, Nightly
- **[[08_Evolution|Changelog]]** - CHANGELOG.md format

### Security & Future

- **[[08_Evolution|Security Model]]** - Private AI, local storage
- **[[08_Evolution|Vulnerability Handling]]** - Responsible disclosure
- **[[08_Evolution|Future Directions]]** - Additional platforms, voice, multi-agent
- **[[08_Evolution|Open Source Ecosystem]]** - Node.js 22+, WebSocket libs
- **[[08_Evolution|Patches]]** - Custom patches in /workspace/patches/

---

## Quick Lookups

### Want to understand...

- **How Gateway works** → [[01_Architecture]] or [[05_Core_Runtime]]
- **How agents work** → [[02_Agents]]
- **How to add a new platform** → [[03_Extensions]]
- **How skills work** → [[04_Skills]]
- **How tools are registered** → [[07_Tools]]
- **How the UI is built** → [[06_UI_Layer]]
- **How the project evolved** → [[08_Evolution]]

---

*This concept map is part of the OpenClaw documentation. See [[Index]] for the main index.*
