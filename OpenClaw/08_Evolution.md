# OpenClaw Evolution and Community

## High-Level Summary

OpenClaw has evolved from a single-channel chatbot gateway into a comprehensive multi-platform AI assistant system. The project follows semantic versioning, maintains detailed changelogs, and operates with a community-driven development model. The vision emphasizes local, fast, and always-on personal AI assistance with full user data ownership. Development is guided by detailed AGENTS.md conventions, and contributions follow established patterns.

## Project History

### Origins

OpenClaw began as a personal project to connect AI coding assistants to messaging platforms. The initial focus was on creating a simple gateway that could:

- Connect to WhatsApp and Telegram
- Forward messages to an AI agent
- Return responses to the user

### Evolution Timeline

| Version | Major Features |
|---------|----------------|
| 0.1.0 | Basic WhatsApp/Telegram gateway |
| 0.5.0 | Multi-channel support |
| 1.0.0 | Plugin system, skill framework |
| 2.0.0 | Gateway, Control UI |
| 3.0.0 | Mobile apps, voice support |
| Current | Multi-agent, Canvas, 20+ channels |

### Key Milestones

1. **Plugin Architecture**: Introduction of the extension system allowing easy addition of new platforms
2. **Skills Framework**: Launch of 52+ skills providing tool capabilities to agents
3. **WebSocket Gateway**: Transition from HTTP polling to WebSocket for real-time communication
4. **Control UI**: Web-based administration interface
5. **Mobile Companion Apps**: iOS and Android apps for on-the-go access
6. **Voice Interaction**: Wake word detection and voice I/O
7. **Canvas**: Real-time visual workspace collaboration
8. **Multi-Agent Support**: Isolated sessions for multiple AI agents

## Vision and Principles

### Core Vision

OpenClaw aims to be a **personal AI assistant that runs on your own devices**. Key principles:

- **Local**: All data stays on user devices
- **Fast**: Minimal latency for responsive interactions
- **Always-on**: 24/7 availability on personal hardware
- **Private**: No data sent to third parties without consent
- **User-controlled**: Full control over configuration and behavior

### Design Principles

1. **Simplicity**: Easy to set up and maintain
2. **Extensibility**: Plugin and skill systems for expansion
3. **Privacy**: Local-first data handling
4. **Performance**: Optimized for speed and efficiency
5. **Reliability**: Production-ready stability

### Target Users

- Developers who want AI assistance in their workflow
- Power users wanting personalized AI integration
- Privacy-conscious users preferring local AI
- Teams wanting self-hosted AI assistants

## Community Model

### Maintainers

Location: `/workspace/.agents/maintainers.md`

The project has designated maintainers for:
- Core Gateway development
- Extension maintenance
- Skills development
- Documentation
- Community support

### Contribution Areas

| Area | Description |
|------|-------------|
| Core | Gateway, runtime, core features |
| Extensions | Platform integrations |
| Skills | Tool capabilities |
| UI | Web UI, mobile apps |
| Docs | Documentation |
| Community | Support, feedback |

### Development Workflow

1. **Issue Reporting**: Use GitHub Issues
2. **Discussion**: GitHub Discussions for questions
3. **Pull Requests**: Fork, branch, PR workflow
4. **Code Review**: Maintainer review process
5. **Release**: Semantic versioning with changelog |

## AGENTS.md Conventions

Location: `/workspace/AGENTS.md`

The project maintains comprehensive AI agent guidance covering:

### Project-Specific Rules

- Vocabulary: "makeup" = "mac app"
- Never edit `node_modules`
- Signal deployment: use `fly ssh console`
- Gateway on macOS: start/stop via app, not tmux
- Never send streaming replies to external messaging
- Voice wake: use template `openclaw-mac agent --message "${text}"`

### Code Style

- Keep files under ~500 LOC when feasible
- Add brief comments for tricky logic
- Use `@Observable`/`@Bindable` over `ObservableObject` in SwiftUI

### Testing Requirements

- Multiple Vitest configurations: unit, e2e, channels, extensions, gateway, live, scoped

### Release Procedures

- Version locations: package.json, Android, iOS, macOS, docs
- Release guardrails: always ask permission before publishing
- Changelog procedures documented

## Documentation

### Documentation Structure

Location: `/workspace/docs/`

The documentation is built with Mintlify and organized into:

| Section | Topics |
|---------|--------|
| Getting Started | Installation, quick start |
| Concepts | Architecture, channels, agents |
| Channels | Platform-specific setup |
| Tools | Skill and tool references |
| Reference | API, CLI, configuration |
| Security | Auth, secrets, best practices |
| Debug | Troubleshooting, diagnostics |

### Internationalization

Multiple language documentation:
- English (default)
- Japanese (ja-JP)
- Chinese (zh-CN)

## Technology Evolution

### Language Mix

- **Primary**: TypeScript (Gateway, web UI)
- **Swift**: macOS, iOS apps
- **Kotlin**: Android app
- **Shell**: Scripts and tooling

### Build System

- **Package Manager**: pnpm workspaces
- **Build Tool**: Vite (web), Turbo concepts
- **Testing**: Vitest
- **Container**: Docker, docker-compose

### Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| WebSocket Gateway | Real-time, bidirectional communication |
| Plugin System | Extensible platform integration |
| Skills Framework | Modular tool capabilities |
| Session Isolation | Multi-agent support |
| Local-first | Privacy and data ownership |

## Version Management

### Semantic Versioning

- **Major**: Breaking changes
- **Minor**: New features
- **Patch**: Bug fixes

### Release Channels

- **Stable**: Production-ready releases
- **Beta**: Pre-release testing
- **Nightly**: Latest development (not for production)

### Changelog

Location: `/workspace/CHANGELOG.md`

Maintained with:
- Version releases
- Feature additions
- Bug fixes
- Breaking changes
- Deprecations

## Open Source Ecosystem

### Dependencies

Key dependencies:
- Node.js 22+
- WebSocket libraries
- LLM provider SDKs
- Platform APIs

### Patches

Location: `/workspace/patches/`

Dependency patches for:
- Bug workarounds
- Version adjustments
- Custom modifications

## Community Resources

### Communication

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Q&A and community discussion

### Contributing

From CONTRIBUTING.md:

1. Fork the repository
2. Create a feature branch
3. Follow code style
4. Add tests
5. Submit PR
6. Address review feedback

## Security

### Security Model

From SECURITY.md:

- Private AI assistant model
- Local data storage
- No telemetry or data collection
- User controls all credentials
- Secure secret management

### Vulnerability Handling

- Responsible disclosure
- Security advisories
- CVE coordination

## Future Directions

### Planned Features

- Additional platform integrations
- Enhanced voice capabilities
- Improved multi-agent workflows
- Advanced Canvas features

### Community-Driven

The project welcomes:
- New extension submissions
- Skill contributions
- Documentation improvements
- Bug reports and fixes

## Related Sections

- [[01_Architecture]] - Technical architecture
- [[03_Extensions]] - Platform integrations
- [[04_Skills]] - Tool capabilities
- [[05_Core_Runtime]] - Gateway implementation
