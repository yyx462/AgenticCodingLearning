# OpenClaw Agent System

## High-Level Summary

The OpenClaw agent system provides the intelligence layer that processes messages, invokes tools, and generates responses. The system is defined through configuration files in `.agents/` and workflow definitions in `.agent/workflows/`. Agents are integrated with the Gateway and can leverage skills, tools, and multi-agent routing capabilities.

## Core Components

### Agent Definitions (.agents/)

Location: `/workspace/.agents/`

The `.agents/` directory contains agent metadata and maintainer information:

- **maintainers.md** - Defines who maintains and is responsible for specific agents

### Agent Workflows (.agent/workflows/)

Location: `/workspace/.agent/workflows/`

The workflow configurations define how agents operate. The directory contains:

- **update_clawdbot.md** - Workflow configuration for the ClawDBot agent updates

### Agent Architecture in Source Code

The agent implementation is spread across the codebase with key locations:

#### Agent Core (src/agents/)

The core agent implementation resides in `/workspace/src/agents/` (part of the 48 subdirectories in src/). This provides:

- Agent lifecycle management
- State machine handling
- Tool invocation
- Response generation

#### Gateway Agent Integration (src/gateway/)

The Gateway integrates agents through several key files:

- **agent-prompt.ts** - Agent prompt templates and configuration
- **agent-event-assistant-text.ts** - Handling agent-generated text events
- **server.agent.*.test.ts** - Agent integration tests

## Agent Configuration

### Agent Prompt System

The agent prompt system (`src/gateway/agent-prompt.ts`) defines:

- System prompts that define agent behavior
- Dynamic prompt injection based on context
- Conversation history management

### Agent Events

Agents communicate through events that are processed by the Gateway:

```typescript
// Event types include:
- agent_started
- agent_thinking
- agent_tool_calls
- agent_response
- agent_finished
```

## Multi-Agent Support

OpenClaw supports multiple agents with isolated sessions:

### Session Isolation

From `/workspace/src/sessions/`:

- Each agent can have independent session state
- Sessions are keyed by session identifiers
- Cross-agent communication is explicit (not shared state)

### Routing

From `/workspace/src/routing/`:

- Message routing determines which agent handles a message
- Rules can be based on:
  - Channel origin
  - Message content (keywords, patterns)
  - User identity
  - Time-based rules

## Agent Tool Invocation

For detailed tool execution flow, see [[07_Tools]].

### Tool Registry

Tools are registered and discovered through the central Tool Registry. For details on the Tool Registry implementation, see [[07_Tools]].

## Agent Configuration Files

### Profile-Based Configuration

Agents can have multiple profiles defined in configuration:

```json
{
  "agents": {
    "main": {
      "model": "claude-3-opus",
      "systemPrompt": "You are a helpful coding assistant...",
      "tools": ["github", "filesystem", "terminal"]
    }
  }
}
```

### Model Overrides

From `/workspace/src/channels/model-overrides.ts`:

- Per-channel model selection
- Fallback model configuration
- Model-specific parameters

## Agent Behavior Customization

### System Prompts

System prompts define agent personality and capabilities:

- Core identity and role
- Available tools and when to use them
- Response style guidelines
- Context handling rules

### Conversation Context

Agents maintain conversation context through:

- Session history storage
- Memory integration
- Context window management
- Summary generation for long conversations

## Agent Lifecycle

### Startup

1. Gateway loads agent configurations
2. Agent prompt templates initialized
3. Tool registry populated
4. Session store loaded
5. Agent ready to receive messages

### Message Processing

1. Message received via channel
2. Session resolved (existing or new)
3. Context assembled (history + current message)
4. Agent processes with LLM
5. Tools invoked as needed
6. Response generated and sent

### Shutdown

1. Session state persisted
2. Open connections closed gracefully
3. Resources cleaned up

## Extension Points

### Custom Agents

To create a custom agent:

1. Define agent configuration in `.agents/`
2. Create workflow in `.agent/workflows/`
3. Configure tools and permissions
4. Register with Gateway

### Agent Hooks

Agents can be extended via hooks:

- `hooks.before-agent-start` - Pre-start initialization
- `hooks.after-agent-finish` - Post-completion cleanup
- Custom tool integration

## Best Practices

### Configuration Guidelines

From AGENTS.md:

- Keep files under ~500 LOC when feasible
- Add brief comments for tricky logic
- Use consistent naming conventions
- Test agent behavior with various message types

### Security Considerations

- Validate all tool invocation permissions
- Sanitize user input before processing
- Rate limit agent requests
- Log agent actions for audit

## Related Sections

- [[05_Core_Runtime]] - Gateway agent integration
- [[04_Skills]] - Tool capabilities available to agents
- [[03_Extensions]] - Platform integrations via extensions
- [[06_UI_Layer]] - Control UI for agent management
- [[07_Tools]] - Tool system details
