# @projects — Development / Runtime Project Management

**Tracking rule**: `.plan/session.db` is authoritative for todo state. This
document is the executable local specification for project management.

---

## Phase: 17 | Local Implementation Specification

The filesystem-layout architecture document requires later validation against
source before it is treated as an implementation contract.

---

## Purpose

`ProjectManager` - registered references to source directories. Projects are
not source folders with nested session output. Earlier `~/.css/projects/`
metadata proposals remain gated until a current runtime metadata/session-output
owner is explicitly confirmed.

- CRUD for registered projects
- Session linking: associate canonical session records with a project after the sessions owner exists
- Project-level settings overrides (via `@settings` scope=PROJECT)
- Session/output-directory integration after ownership is reconciled against current source
- REST API for frontend

---

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` (projects.py) | → consumes | `ProjectRecord` frozen `msgspec.Struct` value type |
| `css.core.db` | → consumes | `ProjectRecord` + `ProjectSessionRecord` ORM models |
| `@settings` | → integrates | Project-level setting overrides via `SettingsManager.get(..., scope=PROJECT)` |
| Session/output-directory owner | ← consumed by | Ownership unresolved: no implemented `core/workspace/` package was found during documentation cleanup; retain the integration requirement pending source reconciliation. |
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
A project is a DB record pointing at `project.source_dir`; the source code is
never copied. Sessions may reference `project.source_dir` as a permitted
source path, but session output ownership is separate and unresolved.

### No implicit project detection
CSS does NOT scan `$(pwd)` for a `.css/` folder. A project must be explicitly registered with `ProjectManager.create()`. Then sessions can be linked to it. A session without a `project_id` is a standalone session (e.g., a quick threat hunt).

### Filesystem sync gate
The previously proposed metadata-directory synchronization is not an
executable contract until its owner and storage root are approved. CRUD and
session linkage must not create `~/.css` or a new `core/workspace` package by
assumption.

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
  session_id TEXT,               -- matches the canonical sessions owner once implemented
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

    # Filesystem metadata sync is added only after its owner/storage root is confirmed.
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

## Filesystem Layout Gate

The historical `~/.css/projects/` metadata layout is not approved as a live
runtime target. Reconcile it with `.plan/` governance, the future sessions
owner, and settings persistence before implementing filesystem synchronization.

---

## Implementation Todos (Phase 17)

| Todo ID | Description | Status |
|---------|-------------|--------|
| `projects-db-model` | ProjectRecord + ProjectSessionRecord Tortoise ORM | pending |
| `projects-db-migration` | DB migration | pending |
| `projects-record-struct` | ProjectRecord frozen `msgspec.Struct` in `core/types` | pending |
| `projects-manager-crud` | CRUD + find_by_path | pending |
| `projects-manager-sessions` | Session linking methods | pending |
| `projects-manager-fs-sync` | Filesystem metadata sync | pending |
| `projects-rest-routes` | REST endpoints /api/projects/* | pending |
| `projects-workingdir-integration` | Legacy-named todo: integrate the confirmed session/output-directory owner after source reconciliation. | pending |
| `projects-event-emission` | Project lifecycle events (BLOCKED: Phase 14) | pending |

## Executable Phase 17 Contract (2026-05-26)

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/modules/projects/models.py` | Existing `Project`, `ProjectFile`; inspect before adding tracker-planned records. |
| `src/css/modules/projects/manager.py` | Planned `ProjectManager` CRUD/session-link operations. |
| `src/css/modules/projects/routes.py` | Planned `/api/projects/*` handlers. |
| `src/css/core/types/projects.py` | Planned immutable project response/value structs if retained after existing model inspection. |
| `src/css/modules/sessions/` | Planned canonical session association owner; currently a stub contract only. |

1. Reconcile existing `Project`/`ProjectFile` with the tracker-planned
   project/session records before introducing duplicate persistence.
2. Implement DB CRUD and session linking first; expose REST operations over
   those records and emit events after Phase 14 event ownership is available.
3. Keep `projects-workingdir-integration` gated until the session-output owner
   is explicitly selected; do not implement the legacy path named in the id.
4. Validate ORM/API CRUD, source-path uniqueness/access control, session
   association, event behavior, and absence of unapproved filesystem or
   `core/workspace` creation.
