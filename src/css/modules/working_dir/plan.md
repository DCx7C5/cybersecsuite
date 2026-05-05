# modules/working_dir — Plan

**Status**: Phase 15 — NOT YET IMPLEMENTED (stub only)
**Phase**: 15 (addendum)
**Source of truth**: `/home/daen/Projects/cybersecsuite/.plan/plan.md` Phase 15 Addendum section

---

## Vocabulary (read this first)

| Term | What it means | Where it lives |
|------|--------------|----------------|
| **Project** | A registered engagement/target — e.g. "corp-pentest Q1 2026". Points to a source dir (read-only). | `modules/projects/` (Phase 17). `~/.css/projects/<id>/metadata.json` |
| **Session** | One agent execution context. Has its own scratch space on disk. May optionally belong to a project. | `modules/sessions/` (Phase 19). `~/.css/sessions/<id>/` |
| **session_dir** | The agent's writable scratch space: findings, artifacts, notes. | `~/.css/sessions/{session_id}/` |
| **project.source_dir** | The read-only target directory (codebase, network config, etc). Never copied. | wherever the user's project lives |
| **project_id** | Optional FK linking a session to a project for organisation. NOT the same as session_dir. | `SessionContext.project_id: str \| None` |

**Critical distinction**: a session can exist without any project (standalone threat hunt). A project can have zero active sessions. They are **siblings**, not parent/child.

```
~/.css/
├── projects/
│   └── <project_id>/
│       └── metadata.json       ← project record (source_dir, name, tags)
└── sessions/
    └── <session_id>/           ← session_dir (writable scratch)
        ├── plan.md
        ├── findings/
        ├── artifacts/
        └── agents/
            └── <agent_id>/
```

---

## What This Module Does

Owns the lifecycle of a session's working directory on disk. The ONLY place that:
- Creates the session directory structure
- Knows which subdirectory layout belongs to which mode
- Creates the automatic least-privilege PathGrant for the session
- Provides the agent's sub-directory
- Cleans up after session ends

Nothing else creates directories. Not agents, not tools, not permissions.

---

## SessionContext (dependency — lives in css/core/session.py)

```python
class SessionContext(msgspec.Struct, frozen=True):
    session_id: str
    agent_id: str
    session_dir: Path          # absolute path to ~/.css/sessions/{session_id}/
    project_id: str | None = None   # optional FK → projects module (Phase 17)
    target: str | None = None       # human label: IP, domain, repo name
    parent_session_id: str | None = None
    git_enabled: bool = True        # Phase 24: auto-commit per turn
```

`WorkingDirManager.create()` returns a `SessionContext`. Everything else receives it.

---

## Three Session Modes

### `planner`
Use when: starting a full pentest engagement, red team op, structured investigation.
Creates:
```
~/.css/sessions/{session_id}/
├── plan.md              ← starter template: session_id, target, created_at, ## Objectives
├── findings/
├── artifacts/
├── tools/
└── agents/{agent_id}/
    ├── scratch/
    └── output/
```

### `search`
Use when: hunting a specific threat, quick lookup, sub-agent for a specific task.
Creates:
```
~/.css/sessions/{session_id}/
├── findings/
└── artifacts/
```
No plan.md. Minimal footprint.

### `minimal`
Use when: unknown purpose, just need the root dir.
Creates: `~/.css/sessions/{session_id}/` only.

---

## WorkingDirManager API

```python
from css.modules.working_dir import WorkingDirManager

wdm = WorkingDirManager()

# Start a session
ctx = await wdm.create(
    session_id="abc-123",
    agent_id="agent-1",
    target="192.168.1.0/24",
    mode="planner",          # or "search" or "minimal"
    project_id="corp-q1",   # optional — links to a registered project
)
# ctx.session_dir = Path("~/.css/sessions/abc-123")
# PathGrant auto-registered: agent-1 → ~/.css/sessions/abc-123/** → READ+WRITE

# Get agent-specific subdir
agent_dir = await wdm.agent_subdir(ctx)
# Path("~/.css/sessions/abc-123/agents/agent-1/")

# Clean up (keeps findings by default)
await wdm.cleanup("abc-123", keep_findings=True)
# findings/ moved to /workspace/archive/abc-123/, then session dir removed
```

---

## Least Privilege Contract

`WorkingDirManager.create()` registers exactly ONE PathGrant automatically:
```
agent_id → ~/.css/sessions/{session_id}/** → READ + WRITE
```

**Nothing else is accessible without an explicit additional grant from the orchestrator.**

Example: if agent needs to read `/etc/hosts`, orchestrator must call:
```python
await grant_manager.grant_path(
    agent_id=agent_id,
    path_pattern="/etc/hosts",
    ops={PathOp.READ},
    session_id=session_id,
)
```

---

## File Layout (Phase 15 target)

```
modules/working_dir/
├── __init__.py       # exports: WorkingDirManager
├── manager.py        # WorkingDirManager class (all methods async)
└── plan.md           # THIS FILE
```

---

## Todos (session.db — Phase 15 addendum)

| ID | What | Status |
|----|------|--------|
| `session-context-create` | SessionContext struct in css/core/session.py | pending |
| `working-dir-manager` | WorkingDirManager.create() + PathGrant registration | pending |
| `working-dir-planner-layout` | _setup_planner_layout() with plan.md template | pending |
| `working-dir-search-layout` | _setup_search_layout() findings+artifacts only | pending |
| `working-dir-agent-subdir` | agent_subdir() per-agent scratch+output dirs | pending |
| `working-dir-cleanup` | cleanup() with optional findings archive | pending |

Start with `session-context-create` (no deps). Then `working-dir-manager` (deps: session-context-create + perm-grant-manager).
