# Claude Code Roadmap

> An Obsidian vault documenting the architecture of the Claude Code codebase.

## Start Here

- [[00-Architecture/The Closed Loop - Input to Output Flow|THE CLOSED LOOP]] — The highest-priority doc. Traces your input from keystroke to response, step by step, file by file.

## Deep Dives

Each major step in the Closed Loop has a dedicated technical deep dive:

- [[00-Architecture/Deep Dive - Input Processing Pipeline|Input Processing]] — How keystrokes become messages (Steps 1-4)
- [[00-Architecture/Deep Dive - Pre-flight Pipeline|Pre-flight Pipeline]] — Context management before API calls (Step 6a)
- [[00-Architecture/Deep Dive - API Streaming Layer|API Streaming]] — SSE streaming, retries, caching, model fallback (Step 6b)
- [[00-Architecture/Deep Dive - Tool Execution Pipeline|Tool Execution]] — Concurrency, permissions, result storage (Step 6c)

## Layers

1. [[01-Entry-and-Bootstrap/Entry and Bootstrap|Entry & Bootstrap]] — `main.tsx` → `setup()` → REPL ready
2. [[02-Conversation-Loop/Conversation Loop and State|Conversation Loop & State]] — The `query()` generator, AppState, tasks, context
3. [[03-Tool-System/Tool System|Tool System]] — Tool definitions, registry, execution, all 30+ tools
4. [[04-Permission-System/Permission System|Permission System]] — Permission modes, approval flow, rules
5. [[05-UI-Components/UI Components|UI Components]] — React/Ink component tree, message rendering
6. [[06-Services/Services and Utilities|Services & Utilities]] — API, compaction, MCP, analytics, hooks, 300+ util files

## Cross-Cutting

- [[09-Cross-References/Cross-File Reference Map|Cross-File Reference Map]] — Dependency graph, function call chains, data flow
