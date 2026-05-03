# @db — Database Layer (Tortoise ORM)

**Location**: `src/css/core/db/`

**Responsibility**: Tortoise ORM configuration, model auto-discovery, scope/team/quota management, database enums.

---

## Overview

CyberSecSuite uses **Tortoise ORM** for async PostgreSQL access.

**Services**:
- **cybersec-postgres**: PostgreSQL 15 (port 5432 internal)
- **Connection pooling**: Managed by asyncpg (Tortoise default)
- **Migrations**: Via Tortoise migrations or Alembic (TBD)

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
class ProjectScope(Model):
    """Project-level scope — persistent forensic workspace."""
    
    name: str
    description: str
    mode: RedBlueMode = RedBlueMode.BLUE_TEAM
    ioc_count: int = 0
    findings: list[Finding]  # Related findings
    
    class Meta:
        table = "project_scope"

class SessionScope(Model):
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
class Team(Model):
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
class OrchestratorInstance(Model):
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
                "css.modules.marketplace.models",
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

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-03
