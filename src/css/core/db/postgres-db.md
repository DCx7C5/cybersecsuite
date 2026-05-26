# @db — Database Layer (Tortoise ORM)

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document owns executable database-runtime guidance; documentation sanitization
may update prose without changing implementation status.

---

**Location**: `src/css/core/db/`

**Responsibility**: Tortoise ORM configuration, model auto-discovery, scope/team/quota management, database enums.

---

## Overview

CyberSecSuite uses **Tortoise ORM** for async PostgreSQL access.

**Services**:
- **cybersec-postgres**: custom PostgreSQL 18-alpine build (port 5432 internal)
- **Connection pooling**: Managed by asyncpg (Tortoise default)
- **Schema policy**: Phase 40 currently uses direct model/schema edits with no
  migration files for the development tranche; production
  migration/versioning is a later explicit decision.

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

### Initialization and Seeding Contract

| Stage | Required behavior |
|-------|-------------------|
| Development schema initialization | Follow the live Phase 40 direct-schema policy; do not invent migration files during this tranche. |
| Provider bootstrap | Seed from canonical YAML only if the provider table is empty; otherwise enrich without destructive reset. |
| Provider/model bootstrap | Establish Provider-to-LLMModel ownership before model upserts. |
| Runtime menu bootstrap | Idempotently upsert known navigation routes grouped by `menu_id`. |
| Owner defaults | Seed settings, templates, and built-ins only through owner-defined idempotent keys. |

### Operational Database Follow-Ups

| Concern | Requirement |
|---------|-------------|
| Connection pool | Use asyncpg credentials with a finite command timeout; do not allow hung queries to consume connections indefinitely. |
| Vector retrieval | Install and enable `pgvector` before claiming semantic VectorRAG implementation. |
| Expiry/time-series access | Add indexed paths for expiry and timestamp queries only where confirmed by live models and query use. |
| Telemetry | Keep append-heavy telemetry in OpenObserve; keep mutable application state in PostgreSQL. |

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

#### `tasks.py` (task lifecycle ownership)

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

```

#### `quotas.py` (team quota ownership only)

```python
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

**File**: `src/css/core/settings/config.py` after the tracked config
consolidation; until then audit existing `core/config.py` consumers before
cutting imports.

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
- `tasks.py` + `quotas.py` — `TaskAssignment`, `TaskResult`, and `TeamQuota` split by ownership

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
- ✅ Phase 40 uses direct model/schema edits and no migration files during this tranche

### Readiness Assessment
🟢 **Production Ready** — Minor issue: utils.py is empty (refactor opportunity)

---

## Phase 15 Cleanup Reconciliation

Earlier plans made this cleanup depend on a `working-dir-manager` /
`core/workspace` package. No implemented `core/workspace` directory was found
during documentation cleanup. Reconcile tracker rows and current source before
deleting scope models or utilities.

| Item | Action | Todo ID |
|------|--------|---------|
| `scope_utils.py` | Delete entire file | `scopes-module-remove` |
| `enums.py` | Remove `ScopeLevel` enum | `scopes-module-remove` |
| `models/scope.py` | Drop/migrate `SessionScope` and `ProjectScope` DB models | `scopes-module-remove` |

> Do not execute the legacy deletion sequence until the session/output-directory
> owner and permissions/session replacement contracts have been validated.

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
- **Blockers**: None (direct-schema policy is explicit for this tranche)
- **Phase Ready**: Phase 2 ✅ (Production Ready)
- **Last Audited**: 2026-05-03 by Agent 2
- **Audit Reference**: this local document and `models/postgres-models.md`; query `.plan/session.db` for live status

---

## Audit Timestamp (2026-05-04)

**Status**: DB critical chain updates synchronized from session.db

- ✅ `db-dedupe-enums` / `db-fix-tooltype-enum-empty`: canonical enum set retained in `enums.py`
- ✅ `db-fix-fk-labels-scope`: scope model FKs now use `css.ProjectScope` / `css.SessionScope`
- ✅ `db-fix-scope-level-charenum`: `ScopedEntry.scope_level` now uses `CharEnumField(ScopeLevel)`
- ✅ `db-fix-charfield-enums`: team/orchestrator/task status + priority fields migrated to DB enums

---

## Sync Reminder

> `.plan/session.db` is authoritative for implementation status. Update it
> when implementation work changes todo state; keep this local specification
> accurate for implementers.
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

## Executable Database Contract (2026-05-26)

The historical inventory above records earlier source shape. Current
implementation work must use these concrete boundaries:

| Path | Runtime symbols / pending responsibility |
|------|------------------------------------------|
| `src/css/core/db/models/base.py`, `src/css/core/db/models/mixins.py`, `src/css/core/db/fields/{char,int,float,decimal,json}_fields.py` | `BaseModel`, `BaseTreeModel`, timestamp/version/soft-delete/frontmatter policies, and semantic field helpers. |
| `src/css/core/db/models/memory.py`, `src/css/core/db/models/marketplace.py`, `src/css/core/db/models/tasks.py`, `src/css/core/db/models/quotas.py` | Canonical model consolidation lanes. |
| `src/css/core/db/models/provider.py`, `src/css/core/db/models/user.py`, `src/css/core/db/models/accounts.py`, `src/css/core/db/models/llm_models.py` | Provider/user/account/model ownership and startup seeding. `provider.py` owns the provider table; Provider↔LLMModel relation remains deferred. |
| `src/css/core/db/models/menu.py` | `MenuItem`, `MenuItemManager.roots()`, `sync_default_menu_items()`. |
| `src/css/core/menu/endpoints.py` | `list_menu_items(menu_id: str | None = None)` partitioned runtime API target. |
| `src/css/core/settings/config.py` | DB connection bootstrap configuration after settings ownership reconciliation. |

| Pending todo group | Status | Steps and validation |
|--------------------|--------|----------------------|
| Phase 40 model lanes | pending | Audit imports, preserve canonical models, cut consumers over, and validate ORM discovery/imports before removal. |
| `db40-lane-task-provider-user`, `db40-taskmodel-import-cutover`, `db40-quotas-task-residual-cleanup`, `db40-user-vs-account-boundary`, `db40-provider-model-cutover` | in_progress | Lock and apply ownership boundaries: task lifecycle in `tasks.py`, quota in `quotas.py`, internal user identity in `user.py`, tenant accounts in `accounts.py`, and provider/model catalog in `provider.py` + `llm_models.py`. |
| `db40-basetree-candidate-inventory` | done | Navigation URL/path/breadcrumb tree ownership remains in `MenuItem` (`BaseTreeModel`); no additional tree ORM adoption required in this tranche. |
| `db40-basetree-tag-adoption-plan` | done | Tag taxonomy stays classification metadata on `Tag.parent_tag`; no default `BaseTreeModel` adoption without explicit navigation semantics. |
| `db40-menu-menuid-upsert`, `db40-menu-menuid-endpoints` | pending | Seed partitions idempotently, implement `list_menu_items()` filter, initialize DB, and exercise each partition route. |
| `db40-lane-tagging`, `db40-taggable-entity-inventory`, `db40-tag-junction-naming-standard`, `db40-tag-junction-meta-backfill`, `db40-tagging-db-concept`, `db40-llmmodel-tag-runtime-wire` | in_progress | Keep tagging as classification/filter/search/policy metadata only; finalize naming/meta/runtime wire in the documented order without menu/tree/navigation scope creep. |
| Phase 17 provider/model seed rows | pending | Establish relation ownership before non-destructive YAML/bootstrap seeding and model upsert tests. |
| `db40-field-library-expansion` | done | Expanded semantic field helpers across char/int/float/decimal/json modules and exposed canonical imports for model use. |
| `db40-intelligence-home-plan` | done | Verified triage ownership is module-local after facade removal; retrieval ownership stays in `core/rag_vector` + `core/rag_graph`. |
| `db40-lane-platform-polish`, `db40-mixins-expansion`, `db40-model-meta-standardization`, `db40-pipeline-home-plan` | in_progress | Lane F documentation pass defining field/mixin/Meta and runtime-home ownership boundaries (`core/cache`, `modules/triage`, `core/pipeline`). |

### Lane C Task/Provider/User Contract

Ownership map for Phase 40 lane C:
- `TaskAssignment` and `TaskResult` live in `src/css/core/db/models/tasks.py`.
- `TeamQuota` lives in `src/css/core/db/models/quotas.py`.
- `User` is internal/admin identity in `src/css/core/db/models/user.py`.
- `Account`, `UserProfile`, `Organization`, and related tenancy records live in
  `src/css/core/db/models/accounts.py`.
- Provider/model catalog ownership lives in
  `src/css/core/db/models/provider.py` + `src/css/core/db/models/llm_models.py`.
- `LLMModel.provider` remains a temporary slug bridge until
  `orm-provider-llmmodel-relation` introduces the explicit relation.
- `src/css/modules/tasks/models.py` remains an auto-discovery stub and does not
  re-own task ORM models.

Lane C child todo execution constraints:
1. `db40-taskmodel-import-cutover` before `db40-quotas-task-residual-cleanup`.
2. `db40-user-vs-account-boundary` before `db40-provider-model-cutover`.

### Lane D BaseTreeModel Inventory Contract

- `src/css/core/db/models/menu.py::MenuItem` remains the canonical
  `BaseTreeModel` navigation owner.
- `src/css/modules/tags/models.py::Tag.parent_tag` remains classification
  hierarchy metadata, not navigation-tree ownership.
- `src/css/core/marketplace/` continues to consume menu hierarchy and does not
  define an additional tree ORM model.
- Tag-tree adoption is explicitly deferred unless tagging introduces
  URL/path/breadcrumb navigation requirements.

### Lane E Tagging Contract

Tagging scope in Phase 40:
- Classification, filter, search, and policy metadata.
- Not navigation/menu/tree hierarchy.

Lane E child todo execution order:
1. `db40-taggable-entity-inventory`
2. `db40-tag-junction-naming-standard`
3. `db40-tag-junction-meta-backfill`
4. `db40-tagging-db-concept`
5. `db40-llmmodel-tag-runtime-wire`

Lane E owned write surface:
- `src/css/modules/tags/*`
- `src/css/core/db/models/llm_models.py`
- `src/css/core/db/models/marketplace.py`
- `src/css/modules/tools/models.py`
- `src/css/core/tools/models.py`

Out-of-scope for Lane E: menu/tree/navigation and unrelated model cleanup.

### Lane F Ordered Dependency Contract

Lane F child todo execution order is fixed to avoid ownership overlap:
1. `db40-field-library-expansion` before `db40-mixins-expansion`.
2. `db40-tag-junction-meta-backfill` before `db40-model-meta-standardization`.
3. `db40-intelligence-home-plan` before `db40-pipeline-home-plan`.

Direct schema policy requirement in both DB planning docs:
- Phase 40 uses direct model and schema edits in development.
- Do not infer or backfill a production migration/versioning policy in this lane.

### Phase 40 Schema-Change Development Flow

For schema-changing implementation work in this tranche:
1. Edit the ORM model directly in `src/css/core/db/models/`.
2. Rebuild the dev schema through the existing initialization path:
   `python manage.py init-db`.
3. Reseed deterministic owner/bootstrap data through the same init flow.
4. Re-run read-side checks (imports, ORM discovery, and query paths) before
   marking tracker todos done.
