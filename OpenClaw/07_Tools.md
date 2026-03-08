# OpenClaw Tools and Capabilities

## High-Level Summary

OpenClaw's tool system provides agents with actionable capabilities to interact with external services, execute commands, and perform complex tasks. The system comprises native tools built into the Gateway, skill-based tools from the 52 available skills, and plugin-provided tools from extensions. Tools are registered with a central registry and exposed to agents through a standardized interface with parameter validation, error handling, and result formatting.

## Tool Architecture

### Tool Registry

Location: `/workspace/src/plugins/tools.ts`

The central tool registry manages all available tools:

```typescript
interface Tool {
  id: string;
  name: string;
  description: string;
  parameters: z.ZodSchema;
  handler: ToolHandler;
  permissions?: string[];
  category?: string;
}

interface ToolRegistry {
  tools: Map<string, Tool>;
  register(tool: Tool): void;
  get(id: string): Tool | undefined;
  list(): Tool[];
  listByCategory(category: string): Tool[];
}
```

### Tool Categories

Tools are organized into categories:

| Category | Description | Examples |
|----------|-------------|----------|
| communication | Messaging platforms | slack, discord, telegram |
| productivity | Productivity apps | notion, obsidian, trello |
| developer | Development tools | github, tmux, filesystem |
| media | Media control | spotify, sonos, video |
| ai | AI/ML services | gemini, openai, whisper |
| utility | General utilities | search, summarize, url |

### Tool Invocation Flow

1. Agent decides to use a tool
2. Tool invocation request constructed
3. Request sent to Gateway via WebSocket
4. Gateway validates tool and permissions
5. Tool handler executes
6. Results returned to agent
7. Agent incorporates results

## Native Tools

### Core Tools

Built-in tools available without extensions:

| Tool | Description |
|------|-------------|
| echo | Echo back input |
| timestamp | Current timestamp |
| random | Random number generation |
| evaluate | JavaScript evaluation |

### Channel Tools

Channel-specific tools:

```typescript
// Tools exposed per channel
- channel.send: Send message to channel
- channel.list: List available channels
- channel.info: Get channel details
- channel.health: Check channel status
```

### Session Tools

Session management tools:

```typescript
- session.list: List active sessions
- session.history: Get message history
- session.create: Create new session
- session.end: End session
```

## Skill-Based Tools

### Overview

Skills provide specialized tools for external services. Each skill exposes capabilities as tools.

For skill implementation details, see [[04_Skills]].

### Skill Tool Mapping

#### GitHub Skill

```typescript
// skills/github - Tool capabilities
- github.list_repos: List repositories
- github.get_issue: Get issue details
- github.create_issue: Create new issue
- github.list_prs: List pull requests
- github.create_pr: Create pull request
```

#### Notion Skill

```typescript
// skills/notion - Tool capabilities
- notion.search: Search pages
- notion.get_page: Get page content
- notion.create_page: Create new page
- notion.update_block: Update block
```

#### Spotify Skill

```typescript
// skills/spotify-player - Tool capabilities
- spotify.play: Start playback
- spotify.pause: Pause playback
- spotify.next: Next track
- spotify.previous: Previous track
- spotify.get_current_track: Now playing
- spotify.search: Search tracks
```

### Tool Parameter Schema

Tools define parameters using Zod:

```typescript
const createIssueParams = z.object({
  owner: z.string().describe('Repository owner'),
  repo: z.string().describe('Repository name'),
  title: z.string().describe('Issue title'),
  body: z.string().optional().describe('Issue body'),
  labels: z.array(z.string()).optional(),
  assignees: z.array(z.string()).optional(),
});

const tool = {
  name: 'github.create_issue',
  description: 'Create a GitHub issue',
  parameters: createIssueParams,
  handler: async (params) => {
    // Implementation
  }
};
```

## Plugin-Provided Tools

### Extension Tools

Extensions can provide custom tools:

```typescript
// In extension registration
register(api: OpenClawPluginApi) {
  api.registerTool({
    name: 'slack.post_message',
    description: 'Post a message to Slack',
    parameters: z.object({...}),
    handler: async (params) => {...}
  });
}
```

For extension tool registration, see [[03_Extensions]].

### HTTP Tools

Tools for making HTTP requests:

```typescript
// HTTP invocation tool
- http.request: Make HTTP request
- http.get: GET request
- http.post: POST request
```

## Tool Configuration

### Tool Settings

Tools can be configured per-agent:

```json
{
  "agents": {
    "main": {
      "tools": {
        "github": {
          "enabled": true,
          "permissions": ["repo", "read:user"]
        },
        "filesystem": {
          "enabled": true,
          "allowedPaths": ["/workspace"]
        }
      }
    }
  }
}
```

### Tool Permissions

Fine-grained permission control:

```typescript
interface ToolPermission {
  tool: string;
  actions: string[];
  constraints?: Record<string, any>;
}
```

## Tool Execution

### Execution Context

```typescript
interface ToolContext {
  session: Session;
  agent: Agent;
  channel: Channel;
  user: User;
  config: ToolConfig;
}
```

### Result Format

```typescript
interface ToolResult {
  success: boolean;
  data?: any;
  error?: {
    code: string;
    message: string;
  };
  metadata?: {
    duration: number;
    tokens?: number;
  };
}
```

### Error Handling

Standardized error codes:

| Code | Description |
|------|-------------|
| TOOL_NOT_FOUND | Tool doesn't exist |
| INVALID_PARAMS | Parameter validation failed |
| PERMISSION_DENIED | User lacks permission |
| RATE_LIMITED | Too many requests |
| EXECUTION_ERROR | Tool execution failed |
| TIMEOUT | Tool timed out |

## Tool Discovery

### Discovery Process

1. Load built-in tools
2. Scan and load skill tools
3. Scan and load extension tools
4. Register all with central registry
5. Validate tool schemas
6. Build tool index

### Tool Catalog

Location: `/workspace/src/gateway/server-tools-catalog.ts`

```typescript
interface ToolCatalog {
  tools: ToolDefinition[];
  categories: string[];
  search(query: string): Tool[];
}
```

## Tool Development

### Creating Custom Tools

1. Define tool interface
2. Implement handler
3. Register with tool registry
4. Add tests
5. Document capabilities

### Tool Template

```typescript
import { z } from 'zod';

const paramsSchema = z.object({
  // Define parameters
});

export const myTool: Tool = {
  name: 'my_custom_tool',
  description: 'Description of what the tool does',
  parameters: paramsSchema,

  async handler(params: z.infer<typeof paramsSchema>, context: ToolContext) {
    try {
      // Tool logic
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: { code: 'EXECUTION_ERROR', message: error.message }};
    }
  }
};
```

### Testing Tools

```typescript
describe('myTool', () => {
  it('should execute successfully', async () => {
    const result = await myTool.handler({ param: 'value' }, mockContext);
    expect(result.success).toBe(true);
  });

  it('should validate parameters', async () => {
    await expect(myTool.handler({}, mockContext)).rejects.toThrow();
  });
});
```

## Tool Usage in Agents

### Agent Tool Selection

Agents select tools based on:
- User intent detection
- Available tools list
- Tool descriptions
- Parameter requirements

For agent tool invocation details, see [[02_Agents]].

### Tool Result Processing

Agents process tool results:
1. Parse result data
2. Handle errors
3. Incorporate into response
4. Decide on follow-up actions

### Tool Chains

Complex operations can chain tools:

```typescript
// Example: Create issue and notify Slack
1. github.create_issue -> {issue_url}
2. slack.send_message -> {message: issue_url}
```

## Performance

### Tool Timeouts

Configurable timeouts per tool:

```json
{
  "tools": {
    "timeout": {
      "default": 30000,
      "http.request": 60000,
      "shell.exec": 10000
    }
  }
}
```

### Caching

Tool results can be cached:

```typescript
interface ToolOptions {
  cache?: {
    ttl: number;
    key: string;
  };
}
```

## Monitoring

### Tool Usage Tracking

Track:
- Invocation counts
- Success/failure rates
- Execution times
- Error patterns

### Logging

Tool invocations logged for debugging:

```typescript
logger.info('tool.invoke', {
  tool: toolName,
  session: sessionId,
  duration: executionTime,
  success: result.success
});
```

## Related Sections

- [[04_Skills]] - Skill capabilities
- [[02_Agents]] - Agent tool usage
- [[05_Core_Runtime]] - Gateway tool registry
- [[03_Extensions]] - Extension tools
