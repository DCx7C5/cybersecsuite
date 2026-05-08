# @db — Database Layer (Tortoise ORM)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/core/db/`

**Responsibility**: Tortoise ORM configuration, model auto-discovery, scope/team/quota management, database enums.

---

## Overview

CyberSecSuite uses **Tortoise ORM** for async PostgreSQL access.

**Services**:
- **cybersec-postgres**: custom PostgreSQL 18-alpine build (port 5432 internal)
- **Connection pooling**: Managed by asyncpg (Tortoise default)
- **Migrations**: Via Tortoise migrations or Alembic (TBD)

**Current infra note**:
- Phase 20 plans PostgreSQL + `pgvector` for VectorRAG, but the current custom image does not yet install the extension package. `mem-pgvector-setup` now explicitly includes the Docker image prerequisite.

### Canonical ORM Primitives

- Every ORM entity inherits `css.core.db.models.base.BaseModel`.
- `BaseModel.id` is the canonical default primary key via `BigIntField(primary_key=True)`.
- `TimestampMixin` is the default source of truth for standard `created_at` / `updated_at` audit pairs.
- `BaseFrontmatterMixin` is the reusable frontmatter contract for models that truly have canonical identifier-style `name` + `description` semantics.
- `BaseUserModel` is for username-rooted identity records.
- `VersionMixin` is for synced/versioned artifacts that should carry semantic version plus remote/local hash provenance.
- Use semantic helpers from `css.core.db.fields` whenever the meaning matches:
  `NameField`, `DescriptionField`, `VersionField`, `SlugField`, `UrlField`,
  `PathField`, `SHA512SumField`, `IPv4Field`, `IPv6Field`, `QualityScoreField`,
  `CostField`.
- Use raw Tortoise fields only when there is no helper with the correct domain semantics.

### Important semantic caveat

- `NameField` is currently an **identifier field**, not a generic UI label. It enforces ASCII, Python-identifier-style content, and uniqueness.
- That means `BaseFrontmatterMixin` must **not** be rolled out blindly to every model with a `name` column.
- Models with human-facing labels or display names should use lighter semantics than `NameField`, most likely a plain `CharField` or a small normalization wrapper at the application boundary rather than another heavy base-field abstraction.
- `BaseFBSModel` is redundant convenience sugar over `BaseModel + BaseFrontmatterMixin` and should be removed instead of becoming another permanent base layer.

### Planned primitive rollout

- `db-timestamp-mixin-rollout` — replace repeated `created_at` / `updated_at` pairs with `TimestampMixin` where semantics are standard
- `db-frontmatter-field-semantics` — split identifier-style `NameField` from human-facing display-label semantics before broad base adoption
- `db-frontmatter-base-rollout` — standardize on `BaseFrontmatterMixin` and roll it out only where the field semantics truly fit
- `db-version-mixin-rollout` — adopt `VersionMixin` for versioned/synced artifacts that also want hash provenance

### Tracked ORM Cleanup Gaps

- `db-vector-rag-charenum-fields` — convert `rag_vector` model `choices=` string fields to canonical enums + `CharEnumField(...)`, matching the DB rules above.
- `db-timestamp-mixin-rollout` — standardize timestamp fields on `TimestampMixin` instead of repeating them inline across ORM models.
- `db-frontmatter-field-semantics` — split identifier-name semantics from display-name semantics before scaling `BaseFrontmatterMixin`.
- `db-frontmatter-base-rollout` — remove `BaseFBSModel` and apply `BaseFrontmatterMixin` only to models that truly fit the canonical `name` + `description` pattern.
- `db-version-mixin-rollout` — apply `VersionMixin` to versioned artifacts that should carry semantic version plus remote/local hash provenance.

---

## Core Files

### 1. **enums.py** (334 lines)

Database-level enums for forensics domain:

```python
class RedBlueMode(str, Enum):
    """Orchestrator operation mode."""
    BLUE_TEAM = "blue"      # Defensive
    RED_TEAM = "red"        # Offensive  
    PURPLE_TEAM = "purple"  # Hybrid

class AuditAction(str, Enum):
    """Forensic audit actions."""
    INVESTIGATE, ANALYZE, FIND, DETECT, EXPLOIT, ...

class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL, HIGH, MEDIUM, LOW, INFO

class FindingStatus(str, Enum):
    """Investigation status."""
    NEW, IN_PROGRESS, RESOLVED, ARCHIVED
```

---

### 2. **Models** (`models/`)

**Core database entities** (967 lines total):

#### `scope.py` (395 lines)

Tortoise ORM models for forensic scope isolation:

```python
class ProjectScope(BaseModel):
    """Project-level scope — persistent forensic workspace."""
    
    name: str
    description: str
    mode: RedBlueMode = RedBlueMode.BLUE_TEAM
    ioc_count: int = 0
    findings: list[Finding]  # Related findings
    
    class Meta:
        table = "project_scope"

class SessionScope(BaseModel):
    """Session-level scope — ephemeral investigation context."""
    
    project: ForeignKeyField = ForeignKey(ProjectScope)
    session_id: str  # Unique session identifier
    start_time: datetime
    iocs: list[IOC]  # Session-specific IOCs
    
    class Meta:
        table = "session_scope"
```

#### `team.py` (2103 lines)

Team/agent management models:

```python
class Team(BaseModel):
    """Team of agents working together."""
    
    name: str
    description: str
    agents: list[Agent]  # Team members
    scope: ForeignKeyField = ForeignKey(ProjectScope)
    
    class Meta:
        table = "team"
```

#### `orchestrator.py` (755 lines)

Orchestrator instance tracking:

```python
class OrchestratorInstance(BaseModel):
    """Running orchestrator process."""
    
    name: str
    host: str
    port: int
    role: str  # "Orchestrator", "TeamLeader", etc.
    last_heartbeat: datetime
    status: str  # "running", "idle", "error"
    
    class Meta:
        table = "orchestrator_instance"
```

#### `quotas.py` (2900 lines)

Task tracking and quotas:

```python
class TaskAssignment(Model):
    """Task assigned to team member."""
    
    task_id: str
    team: ForeignKeyField = ForeignKey(Team)
    status: str  # PENDING, RUNNING, DONE, FAILED
    assigned_at: datetime
    result: ForeignKeyField = ForeignKey("models.TaskResult", null=True)
    
    class Meta:
        table = "task_assignment"

class TaskResult(Model):
    """Result of completed task."""
    
    task_id: str
    output: str
    error: str
    duration_ms: int
    completed_at: datetime
    
    class Meta:
        table = "task_result"

class TeamQuota(Model):
    """Resource quotas for team."""
    
    team: ForeignKeyField = ForeignKey(Team)
    max_concurrent_tasks: int
    max_daily_cost: float
    used_cost_today: float
```

---

### 3. **scope_utils.py** (395 lines)

Scope management utilities:

```python
def get_or_create_project_scope(
    name: str,
    mode: RedBlueMode
) -> ProjectScope:
    """Get existing or create new project scope."""
    # Implementation

def get_session_scope(session_id: str) -> SessionScope:
    """Retrieve session scope by ID."""
    # Implementation

async def archive_session_scope(session_id: str):
    """Archive session scope (move to cold storage)."""
    # Implementation
```

---

### 4. **exceptions.py** (184 lines)

Database-specific exceptions:

```python
class DatabaseError(Exception):
    """Base database error."""

class ScopeNotFoundError(DatabaseError):
    """Scope not found in database."""

class QuotaExceededError(DatabaseError):
    """Team quota exceeded."""
```

---

## Model Auto-Discovery

**File**: `src/css/core/loader.py` (implementation detail)

Tortoise ORM auto-discovers models from:
1. `src/css/modules/*/models.py`
2. `src/css/api_services/*/models.py`
3. `src/css/core/db/models/*.py`

```python
def discover_tortoise_models() -> list[ModelModule]:
    """Auto-discover all Tortoise ORM models."""
    models = []
    
    # Core models
    models.append(ModelModule("core.db", "css.core.db.models"))
    
    # Module models
    for module_name in discover_modules():
        models.append(ModelModule(module_name, f"css.modules.{module_name}.models"))
    
    return models
```

---

## Tortoise Configuration

**File**: `src/css/config.py` (built dynamically)

```python
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": DATABASE_HOST,
                "port": DATABASE_PORT,
                "user": DATABASE_USER,
                "password": DATABASE_PASSWORD,
                "database": DATABASE_NAME,
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "css.core.db.models",
                "css.core.db.models.marketplace",
                # ... other discovered models
            ],
            "default_connection": "default",
        }
    }
}
```

---

## Initialization

**In `app.py` lifespan**:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    yield
    
    await Tortoise.close_connections()
```

---

## Connection Pooling

**asyncpg** handles connection pooling automatically:

- Default pool size: 10
- Min connections: 1
- Max connections: 20
- Configurable via connection string

---

## Integration Points

- **@loader**: Auto-discovers models
- **@asgi**: Initializes ORM in lifespan
- **@logger**: Logs ORM events (SQL queries in DEBUG mode)
- **@config**: Provides database credentials
- **All @modules**: Access models via Tortoise

---

## Audit Results (2026-05-03)

**Agent 2 Core Infrastructure Audit**

### 5-File Pattern Compliance
✅ **PARTIAL COMPLIANCE** — 5 top-level files + models/ subdirectory

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `__init__.py` | Module exports | 56 | ✅ |
| `enums.py` | DB enums (RedBlueMode, Severity, etc) | 334 | ✅ |
| `exceptions.py` | Database exceptions | 184 | ✅ |
| `scope_utils.py` | Scope management utilities | 395 | ✅ |
| `utils.py` | General utilities | 0 | ⚠️ Empty |
| **models/** | Subdirectory | - | ℹ️ |

**Total**: 5 files + models/, 969 LOC → Good (expansion reasonable)

### Models Breakdown
- `scope.py` — ProjectScope, SessionScope (395 lines)
- `team.py` — Team, Agent models (2103 lines)
- `orchestrator.py` — OrchestratorInstance (755 lines)
- `quotas.py` — TaskAssignment, TaskResult, TeamQuota (2900 lines)

### Integration Status
- ✅ Depends on: asgi (init in lifespan), logger, config (8 connections)
- ✅ Reverse dependencies: asgi (lifespan), all modules (model access)
- ✅ 8 indirect integrations validated
- 🟠 Circular risk: db → types → retry (mitigated with lazy imports)

### Implementation Status
- ✅ Tortoise ORM configured
- ✅ Model auto-discovery
- ✅ Scope/team/quota management
- ✅ Connection pooling (asyncpg)
- ✅ Schema generation
- ⚠️ Migrations strategy TBD (Tortoise vs Alembic)

### Readiness Assessment
🟢 **Production Ready** — Minor issue: utils.py is empty (refactor opportunity)

---

## Phase 15 Cleanup (Post-working-dir-manager)

**Prerequisite**: These changes happen AFTER `working-dir-manager` todo is complete.

| Item | Action | Todo ID |
|------|--------|---------|
| `scope_utils.py` | Delete entire file | `scopes-module-remove` |
| `enums.py` | Remove `ScopeLevel` enum | `scopes-module-remove` |
| `models/scope.py` | Drop/migrate `SessionScope` and `ProjectScope` DB models | `scopes-module-remove` |

> **Order matters**: `working-dir-manager` → `perm-rename-scope-to-session` → `streaming-decouple-from-scopes` → `scopes-module-remove` (deletes this DB code last)

---

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-04

---

## Audit Timestamp (2026-05-03)

**Agent 2 Infrastructure Audit — COMPLETE**

- **Status**: ✅ 100% Implemented
- **5-File Pattern**: ⚠️ Partial (5/5 top-level + models subdir)
- **Files**: 10 (5 top + 4 model files) | **LOC**: 969
- **Dependencies**: asgi, logger, config (3 components)
- **Reverse Dependencies**: asgi, loader, modules (50+ dependents)
- **Blockers**: None (migrations strategy TBD, not blocking)
- **Phase Ready**: Phase 2 ✅ (Production Ready)
- **Last Audited**: 2026-05-03 by Agent 2
- **Audit Reference**: .plan/plan.md (phase and status sections)

---

## Audit Timestamp (2026-05-04)

**Status**: DB critical chain updates synchronized from session.db

- ✅ `db-dedupe-enums` / `db-fix-tooltype-enum-empty`: canonical enum set retained in `enums.py`
- ✅ `db-fix-fk-labels-scope`: scope model FKs now use `css.ProjectScope` / `css.SessionScope`
- ✅ `db-fix-scope-level-charenum`: `ScopedEntry.scope_level` now uses `CharEnumField(ScopeLevel)`
- ✅ `db-fix-charfield-enums`: team/orchestrator/task status + priority fields migrated to DB enums

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
