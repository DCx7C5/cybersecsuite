# @projects — Development / Runtime Project Management

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## Phase: 17 | Full plan in `.plan/plan.md` § Phase 17 + `.plan/architecture/filesystem-layout.md`

---

## Purpose

`ProjectManager` — registered references to source directories. Projects are **not** folders with `.css/` subfolders. They are DB entries + `~/.css/projects/<id>/metadata.json` pointing at an external source directory.

- CRUD for registered projects
- Session linking: associate sessions (from `~/.css/sessions/`) with a project
- Project-level settings overrides (via `@settings` scope=PROJECT)
- Auto-integration with `WorkingDirManager` (Phase 15)
- REST API for frontend

---

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` (projects.py) | → consumes | `ProjectRecord` dataclass |
| `css.core.db` | → consumes | `ProjectRecord` + `ProjectSessionRecord` ORM models |
| `@settings` | → integrates | Project-level setting overrides via `SettingsManager.get(..., scope=PROJECT)` |
| `@working_dir` | ← consumed by | `WorkingDirManager.create(project_id=X)` auto-links session |
| `@events` (Phase 14) | → emits | `project.created`, `project.removed`, `project.session_linked` |
| Frontend | ← consumed by | REST endpoints `/api/projects/*` |

---

## File Layout

```
src/css/modules/projects/
├── __init__.py
├── projects.md            ← this file
└── manager.py             ← ProjectManager class
    routes.py              ← REST endpoints (/api/projects/*)
```

---

## Key Design Decisions

### Projects are references, not containers
A project = a DB record + `~/.css/projects/<id>/metadata.json`. The source code lives at `project.source_dir` and is never copied. Sessions reference `project.source_dir` as a read-only path.

### No implicit project detection
CSS does NOT scan `$(pwd)` for a `.css/` folder. A project must be explicitly registered with `ProjectManager.create()`. Then sessions can be linked to it. A session without a `project_id` is a standalone session (e.g., a quick threat hunt).

### Filesystem sync
On `create()`: writes `~/.css/projects/<id>/metadata.json`
On `remove()`: deletes `~/.css/projects/<id>/` — does NOT touch sessions or source code
On startup: `sync_filesystem()` repairs FS ↔ DB drift

---

## DB Schema (managed by T17.8)

```sql
projects(
  id UUID PK,
  name TEXT NOT NULL,
  source_dir TEXT NOT NULL,      -- absolute path, unique when active=TRUE
  description TEXT,
  tags TEXT[],
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

project_sessions(
  project_id UUID FK → projects.id ON DELETE CASCADE,
  session_id TEXT,               -- matches ~/.css/sessions/session-<sid>/
  linked_at TIMESTAMPTZ,
  PRIMARY KEY (project_id, session_id)
)
```

---

## ProjectManager API

```python
class ProjectManager:
    # CRUD
    async def create(name, source_dir, description=None, tags=None) → ProjectRecord
    async def get(project_id) → ProjectRecord | None
    async def list(active_only=True) → list[ProjectRecord]
    async def update(project_id, **kwargs) → ProjectRecord
    async def remove(project_id) → None          # DB only; sessions/source untouched

    # Lookup
    async def find_by_path(source_dir) → ProjectRecord | None

    # Session linking
    async def add_session(project_id, session_id) → None
    async def remove_session(project_id, session_id) → None
    async def get_sessions(project_id) → list[str]
    async def get_project_for_session(session_id) → ProjectRecord | None

    # Filesystem sync
    def _write_metadata(project) → None          # → ~/.css/projects/<id>/metadata.json
    def _delete_metadata(project_id) → None
    async def sync_filesystem() → None
```

---

## REST API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects/` | List all projects |
| POST | `/api/projects/` | Create project (validates source_dir) |
| GET | `/api/projects/{id}/` | Get project details |
| PUT | `/api/projects/{id}/` | Update project |
| DELETE | `/api/projects/{id}/` | Remove (not sessions/source) |
| GET | `/api/projects/{id}/sessions/` | List linked sessions |
| POST | `/api/projects/{id}/sessions/{sid}/` | Link session |
| DELETE | `/api/projects/{id}/sessions/{sid}/` | Unlink session |
| GET | `/api/projects/search/?path=<dir>` | Find project by source_dir |

---

## Filesystem Layout (see `.plan/architecture/filesystem-layout.md`)

```
~/.css/projects/
└── <project-id>/
    ├── metadata.json    {id, name, source_dir, description, tags, created_at}
    └── config.yaml      project-level settings overrides (managed by SettingsManager)
```

---

## Implementation Todos (Phase 17)

| Todo ID | Description | Status |
|---------|-------------|--------|
| `projects-db-model` | ProjectRecord + ProjectSessionRecord Tortoise ORM | pending |
| `projects-db-migration` | DB migration | pending |
| `projects-record-struct` | ProjectRecord dataclass in core/types | pending |
| `projects-manager-crud` | CRUD + find_by_path | pending |
| `projects-manager-sessions` | Session linking methods | pending |
| `projects-manager-fs-sync` | Filesystem metadata sync | pending |
| `projects-rest-routes` | REST endpoints /api/projects/* | pending |
| `projects-workingdir-integration` | WorkingDirManager auto-link (BLOCKED: Phase 15) | pending |
| `projects-event-emission` | Project lifecycle events (BLOCKED: Phase 14) | pending |
