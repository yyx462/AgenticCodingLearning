# OpenClaw Skills System

## High-Level Summary

The OpenClaw skills system provides extensible tool capabilities that agents can invoke to perform specific tasks. Located in `/workspace/skills/`, there are 52 skills organized by category, covering productivity tools, communication platforms, media controllers, AI/ML services, and developer utilities. Each skill is a self-contained module that defines its capabilities and usage patterns through a standardized SKILL.md format.

## Skills Directory Structure

Location: `/workspace/skills/`

The skills directory contains 52 skill modules organized by category:

### Productivity Skills
| Skill | Purpose |
|-------|---------|
| 1password | 1Password password manager integration |
| apple-notes | Apple Notes access |
| apple-reminders | Apple Reminders management |
| bear-notes | Bear notes integration |
| canvas | Canvas LMS integration |
| notion | Notion workspace integration |
| obsidian | Obsidian vault integration |
| things-mac | Things.app task management |
| trello | Trello board management |

### Communication Skills
| Skill | Purpose |
|-------|---------|
| discord | Discord messaging |
| slack | Slack messaging |
| voice-call | Voice calling functionality |
| imsg | Apple iMessage |

### Media Skills
| Skill | Purpose |
|-------|---------|
| camsnap | Camera capture |
| openhue | Philips Hue lighting control |
| songsee | Song information lookup |
| sonoscli | Sonos speaker control |
| spotify-player | Spotify playback control |
| video-frames | Video frame extraction |

### AI/ML Skills
| Skill | Purpose |
|-------|---------|
| coding-agent | Code generation agent |
| gemini | Google Gemini model access |
| model-usage | Model usage tracking |
| openai-image-gen | DALL-E image generation |
| openai-whisper | Whisper speech-to-text |
| openai-whisper-api | Whisper API integration |
| sag | SAG AI agent |
| sherpa-onnx-tts | Offline TTS |

### Developer Skills
| Skill | Purpose |
|-------|---------|
| blogwatcher | Blog post monitoring |
| clawhub | ClawHub service |
| eightctl | 8x8 control |
| github | GitHub integration |
| gh-issues | GitHub issues management |
| gog | Go game assistant |
| himalaya | Email client |
| mcporter | Porter CLI |
| nano-banana-pro | Development tools |
| ordercli | Order management |
| session-logs | Session logging |
| skill-creator | Skill scaffolding |
| tmux | Tmux session management |
| wacli | WA web CLI |

### Apple Ecosystem Skills
| Skill | Purpose |
|-------|---------|
| blucli | BlueCLI control |
| bluebubbles | BlueBubbles iMessage |
| imsg | iMessage sending |
| wacli | WhatsApp web CLI |

### Utility Skills
| Skill | Purpose |
|-------|---------|
| gifgrep | GIF search |
| goplaces | Places/Location lookup |
| healthcheck | Health monitoring |
| peekaboo | Screen sharing |
| summarize | Content summarization |
| xurl | URL expansion |

## Skill Architecture

### Skill Structure Pattern

Each skill follows a consistent directory structure:

```
skills/<skill-name>/
├── SKILL.md          # Skill definition and capabilities
├── src/              # Implementation (optional)
├── package.json      # Dependencies (optional)
└── config/           # Configuration files (optional)
```

### SKILL.md Format

The SKILL.md file defines:

```markdown
# Skill Name

## Description
Brief description of what the skill does.

## Capabilities
- List of available capabilities
- Each capability with parameters

## Usage
How to invoke the skill.

## Examples
Example invocations.
```

## Skill Implementation Patterns

### Simple Skills (Documentation-Only)

Some skills are purely documentation-based, defined entirely in SKILL.md:

```
skills/discord/
└── SKILL.md    # Defines Discord integration capabilities
```

### Complex Skills (With Implementation)

Other skills include full implementation:

```
skills/github/
├── SKILL.md
├── src/
│   ├── index.ts
│   ├── client.ts
│   └── handlers/
├── package.json
└── config/
    └── default.json
```

### Skill Entry Point Pattern

```typescript
import { Skill, SkillContext } from '@openclaw/skill-sdk';

export const discordSkill: Skill = {
  id: 'discord',
  name: 'Discord',
  description: 'Discord messaging integration',

  async invoke(ctx: SkillContext, params: DiscordParams): Promise<SkillResult> {
    // Implementation
  },

  getCapabilities() {
    return [
      { name: 'sendMessage', description: 'Send a Discord message' },
      { name: 'getChannel', description: 'Get channel information' },
    ];
  }
};
```

## Skill Invocation

### From Agent

Agents invoke skills through the tool system. For detailed tool invocation flow, see [[07_Tools]].

### Tool Definition

Skills expose capabilities as tools:

```typescript
interface Tool {
  name: string;
  description: string;
  parameters: z.ZodSchema;
  handler: ToolHandler;
}
```

### Parameter Schema

Skills define parameter schemas using Zod:

```typescript
const sendMessageParams = z.object({
  channel: z.string().describe('Channel ID or name'),
  content: z.string().describe('Message content'),
  thread: z.string().optional().describe('Thread ID'),
  reply: z.string().optional().describe('Message to reply to'),
});
```

## Skill Configuration

### Configuration Files

Skills may include configuration:

```json
// skills/github/config/default.json
{
  "github": {
    "apiUrl": "https://api.github.com",
    "defaultOwner": null,
    "defaultRepo": null
  }
}
```

### Environment Variables

Sensitive credentials use environment variables:

```bash
GITHUB_TOKEN=ghp_xxxxx
NOTION_API_KEY=secret_xxxxx
SPOTIFY_CLIENT_ID=xxxxx
```

### Configuration Schema

Skills define configuration schemas:

```typescript
const configSchema = z.object({
  apiKey: z.string().optional(),
  apiUrl: z.string().default('https://api.example.com'),
  timeout: z.number().default(30000),
});
```

## Skill Lifecycle

### Discovery

Skills are discovered through:
1. Directory scanning of `/workspace/skills/`
2. Reading SKILL.md for capability definitions
3. Loading implementation if present

### Registration

Skills register with the skill registry:

```typescript
const registry = {
  skills: new Map<string, Skill>(),

  register(skill: Skill) {
    this.skills.set(skill.id, skill);
  },

  get(id: string): Skill | undefined {
    return this.skills.get(id);
  }
};
```

### Execution

Skill execution flow:
1. Validate parameters against schema
2. Check authentication/authorization
3. Execute skill logic
4. Handle errors
5. Return results

## Skill Development

### Creating a New Skill

1. Create directory in `/workspace/skills/<skill-name>/`
2. Add SKILL.md with capability definitions
3. Implement in src/index.ts (if needed)
4. Add tests
5. Register in skill registry

### Testing Skills

Skills should include:
- Unit tests for logic
- Integration tests with real APIs
- Mock fixtures for common scenarios

## Skill Access Control

### Permission System

Skills can declare required permissions:

```typescript
const skill: Skill = {
  id: 'github',
  permissions: ['repo', 'read:user'],

  async invoke(ctx, params) {
    // Check permissions before execution
  }
};
```

### Channel Restrictions

Skills can be restricted to specific channels:

```json
{
  "skills": {
    "github": {
      "allowedChannels": ["dev-team", "code-review"]
    }
  }
}
```

## Error Handling

Skills implement error handling:

```typescript
async invoke(ctx, params) {
  try {
    // Execute skill logic
  } catch (error) {
    if (error instanceof AuthError) {
      throw new SkillError('Authentication required', 'AUTH_REQUIRED');
    }
    if (error instanceof RateLimitError) {
      throw new SkillError('Rate limited, retry later', 'RATE_LIMITED');
    }
    throw error;
  }
}
```

## Related Sections

- [[07_Tools]] - Tool system and Tool Registry
- [[02_Agents]] - Agent tool invocation
- [[03_Extensions]] - Platform integrations
- [[05_Core_Runtime]] - Gateway tool routing
