# UI Components

> The React/Ink component tree that renders Claude Code in your terminal.

---

## Component Tree

```
App.tsx
├── ThemeProvider
├── KeybindingProvider
├── REPL.tsx (src/screens/REPL.tsx)
│   ├── VirtualMessageList.tsx      ← Scrollable message list
│   │   ├── MessageRow.tsx          ← Single row wrapper
│   │   │   └── Message.tsx         ← Routes to specific message type
│   │   │       ├── AssistantTextMessage.tsx
│   │   │       ├── AssistantThinkingMessage.tsx
│   │   │       ├── UserToolResultMessage.tsx
│   │   │       │   ├── UserToolCanceledMessage.tsx
│   │   │       │   ├── UserToolRejectMessage.tsx
│   │   │       │   └── UserToolErrorMessage.tsx
│   │   │       ├── SystemTextMessage.tsx
│   │   │       ├── UserCommandMessage.tsx
│   │   │       └── AttachmentMessage.tsx
│   │   └── MessageSelector.tsx     ← Select messages for export
│   │
│   ├── PromptInput/                ← The input bar
│   │   ├── PromptInput.tsx         ← Main input component
│   │   ├── inputModes.ts           ← Input mode logic (vim, emacs)
│   │   └── PromptInputQueuedCommands.tsx
│   │
│   ├── PermissionRequest.tsx       ← Tool approval dialogs
│   │   ├── BashPermissionRequest.tsx
│   │   ├── FileEditPermissionRequest.tsx
│   │   ├── FileWritePermissionRequest.tsx
│   │   └── ...
│   │
│   ├── Spinner.tsx                 ← Loading/activity indicator
│   ├── LogoV2/                     ← Welcome screen, activity feed
│   ├── Settings/                   ← Settings dialogs
│   ├── FeedbackSurvey/             ← Feedback prompts
│   └── DevBar.tsx                  ← Developer debug bar
│
└── Dialog launchers (src/dialogLaunchers.tsx)
    ├── launchResumeChooser()
    ├── launchSnapshotUpdateDialog()
    └── ...
```

---

## Key Component Areas

### Message Rendering (`src/components/messages/`)

Each message type has a dedicated component. `Message.tsx` acts as a router — it inspects `message.type` and renders the correct sub-component.

| Component | Renders | When |
|---|---|---|
| `AssistantTextMessage` | Markdown, code blocks, links | Model's text response |
| `AssistantThinkingMessage` | Collapsible thinking block | Model's thinking (when visible) |
| `UserToolResultMessage` | Tool output, file diffs | Tool execution result |
| `SystemTextMessage` | Status/info messages | System notifications |
| `UserCommandMessage` | Slash command echo | User ran `/command` |
| `AttachmentMessage` | File changes, memory, skills | Injected context |
| `ShutdownMessage` | Session end | Graceful shutdown |

### Design System (`src/components/design-system/`)

Custom themed primitives that wrap Ink's base components:

| Component | Purpose |
|---|---|
| `ThemedBox.tsx` | Box with theme-aware colors |
| `ThemedText.tsx` | Text with theme-aware colors |
| `ThemeProvider.tsx` | Provides theme context |
| `Dialog.tsx` | Modal dialog |
| `FuzzyPicker.tsx` | Fuzzy search picker |
| `ListItem.tsx` | List item component |
| `ProgressBar.tsx` | Progress bar |
| `StatusIcon.tsx` | Status indicator |
| `Ratchet.tsx` | Stepper component |

### Diff Components (`src/components/diff/`)

| Component | Purpose |
|---|---|
| `DiffDialog.tsx` | Full diff view dialog |
| `DiffFileList.tsx` | List of changed files |
| `DiffDetailView.tsx` | Side-by-side or unified diff |

### Highlighted Code (`src/components/HighlightedCode/`)

- Syntax highlighting for code blocks in messages
- Falls back to plain text for unsupported languages

---

## Cross-References

- Data from: [[Conversation Loop and State#State Management]] (AppState drives rendering)
- Permission UI: [[Permission System]]
- Input handling: [[The Closed Loop - Input to Output Flow]] (Step 1-2)
