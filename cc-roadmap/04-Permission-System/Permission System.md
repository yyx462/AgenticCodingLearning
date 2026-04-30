# Permission System

> How Claude Code decides what tools can run without asking you, what needs approval, and how the UI presents those choices.

---

## Permission Flow

```
Tool requested by model
    │
    ▼
canUseTool() (src/hooks/useCanUseTool.ts)
    │
    ├─ Check PermissionMode
    │   ├── 'default'      → Ask for writes, auto-allow reads
    │   ├── 'plan'          → Read-only, no writes allowed
    │   ├── 'auto'          → Auto-allow most things (classifier decides)
    │   └── 'bypassPermissions' → Allow everything (sandboxed only)
    │
    ├─ Check permission rules (user-configured allow/deny patterns)
    │
    ├─ Check tool-specific permissions
    │   ├── BashTool: command pattern matching, sandbox check
    │   ├── FileEditTool: file path matching, staleness check
    │   ├── FileWriteTool: file path matching
    │   └── WebFetchTool: URL domain matching
    │
    └─ Decision
        ├── ALLOW → tool.call() executes immediately
        ├── DENY  → tool_result with error returned to model
        └── NEEDS_APPROVAL → PermissionRequest dialog shown
            │
            ▼
        PermissionRequest.tsx (src/components/permissions/)
            ├── User clicks "Allow" → tool.call() executes
            ├── User clicks "Deny" → error returned
            └── User clicks "Always allow" → rule saved to settings
```

---

## Key Files

### Permission Setup

| File | Purpose |
|---|---|
| `src/utils/permissions/permissionSetup.ts` | Initialize permission mode, parse CLI tool lists, check auto-mode gates |
| `src/utils/permissions/PermissionMode.ts` | Permission mode types and constants |
| `src/utils/permissions/PermissionUpdate.ts` | Apply permission changes (allow/deny rules) |
| `src/utils/permissions/filesystem.ts` | File permission rules, scratchpad directory |

### Permission UI

| File | Purpose |
|---|---|
| `src/components/permissions/PermissionRequest.tsx` | Main permission request component (decides which sub-component to show) |
| `src/components/permissions/PermissionDialog.tsx` | Dialog shell with Allow/Deny/Always Allow buttons |
| `src/components/permissions/BashPermissionRequest.tsx` | Bash command approval with command preview |
| `src/components/permissions/FileEditPermissionRequest.tsx` | File edit approval with diff preview |
| `src/components/permissions/FileWritePermissionRequest.tsx` | File write approval |
| `src/components/permissions/FilesystemPermissionRequest.tsx` | Directory access approval |
| `src/components/permissions/WebFetchPermissionRequest.tsx` | URL fetch approval |
| `src/components/permissions/AskUserQuestionPermissionRequest.tsx` | Question preview before showing to model |
| `src/components/permissions/SkillPermissionRequest.tsx` | Skill invocation approval |

### Permission Rules UI

| File | Purpose |
|---|---|
| `src/components/permissions/rules/AddPermissionRules.tsx` | Add new allow/deny rules |
| `src/components/permissions/rules/PermissionRuleList.tsx` | List all active rules |
| `src/components/permissions/rules/WorkspaceTab.tsx` | Workspace-scoped rules |

---

## Permission Modes

| Mode | Behavior | When used |
|---|---|---|
| `default` | Ask for writes, auto-allow reads | Normal interactive use |
| `plan` | Read-only mode, no tool execution | Planning phase |
| `auto` | Auto-approve most operations (classifier-based) | Trusted environments |
| `bypassPermissions` | Allow everything without asking | Docker/sandbox only |

---

## Cross-References

- Called by: [[Tool System#toolOrchestration.ts]] (every tool call goes through permission check)
- Uses: `src/state/AppStateStore.ts` ([[Conversation Loop and State#State Management]]) for permission context
- UI: [[UI Components#Permission Components]]
