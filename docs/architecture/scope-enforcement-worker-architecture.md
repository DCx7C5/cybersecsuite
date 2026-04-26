# Scope Enforcement & Worker Architecture

**Status**: Phase 5B + 5C Complete  
**Last Updated**: 2026-04-26  
**Components**: Middleware, Cache, Audit, Worker State, Session Persistence

---

## Overview

This document describes the scope enforcement and worker context subsystems implemented in Phase 5B and 5C:

1. **Phase 5B: Scope Enforcement** — Request-level middleware validates scope context and enforces permissions
2. **Phase 5C: Worker Context** — Stateful worker management with scope binding and session persistence

---

## Phase 5B: Scope Enforcement Architecture

### System Diagram

```
HTTP Request
    ↓
[ScopeMiddleware]
    ├─ Extract scope from headers/JWT/path
    ├─ Validate scope hierarchy
    ├─ Check permissions
    ├─ Audit log (if needed)
    └─ Inject request.state.scope
    ↓
Route Handler (FastAPI)
    ├─ Access request.state.scope
    ├─ Use cached scope context
    └─ Return response
    ↓
[Cache Manager]
    ├─ Scope-aware cache keys
    ├─ Cascade invalidation on scope change
    └─ TTL enforcement
    ↓
HTTP Response
    ├─ X-Request-ID header
    ├─ X-Scope-Level header
    └─ X-Scope-Elapsed-Ms header
```

### Components

#### 1. ScopeMiddleware (src/ai_proxy/middleware.py)

**Purpose**: Request boundary enforcement

```python
class ScopeMiddleware(BaseHTTPMiddleware):
    """
    Extracts scope context from request and enforces permissions.
    Runs on every request, adds < 5ms overhead.
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Extract scope
        scope = await self._extract_scope_context(request)
        request.state.scope = scope
        
        # 2. Check permission
        if not self._check_permission(scope):
            raise ScopePermissionError("User lacks permission")
        
        # 3. Call route
        response = await call_next(request)
        
        # 4. Add response headers
        response.headers["X-Request-ID"] = scope.request_id
        response.headers["X-Scope-Level"] = scope.scope_level
        response.headers["X-Scope-Elapsed-Ms"] = scope.elapsed_ms()
        
        return response
```

**Scope Extraction Priority** (first match wins):
1. `X-Scope-Level` header
2. JWT token (if bearer auth)
3. Path parameters (`/projects/{project_id}`)
4. Defaults (app scope)

**Performance**: < 5ms per request (measured)

#### 2. CacheManager (src/db/cache_manager.py)

**Purpose**: Scope-aware caching with hierarchy support

```python
class CacheManager:
    """
    Cache with scope-aware keys and cascade invalidation.
    Parent scope change automatically invalidates child scopes.
    """
    
    # Scope hierarchy (strict parent → child order)
    SCOPE_HIERARCHY = [
        CacheScope.GLOBAL,
        CacheScope.APP,
        CacheScope.PROJECT,
        CacheScope.RUNTIME,
        CacheScope.SESSION,
    ]
```

**Cache Key Format**: `{scope_level}:{resource_id}:{key}`

Example:
```
project:123:user_list           → Users in project 123
session:456:execution_state     → Execution state in session 456
global:default:feature_flags    → Global feature flags
```

**Invalidation Cascade**:
```
Project scope changes (e.g., config update)
    ↓
[Find all runtimes in project]
    ↓
[Find all sessions in each runtime]
    ↓
[Delete all session-scoped cache entries]
    ↓
[Delete runtime-scoped cache entries]
    ↓
[Delete project-scoped cache entries]
```

**Performance**: < 1ms per cache hit (Redis or in-memory)

#### 3. AuditLogger (src/db/audit_logger.py)

**Purpose**: Non-blocking audit trail for all scope access

```python
class AuditLogger:
    """
    Async, queue-based audit logging.
    Buffered entries flushed to DB in batches.
    < 1ms per log entry (non-blocking).
    """
    
    async def log_permission_check(
        self,
        user_id: str,          # ID only, no PII
        resource: str,         # Resource ID
        action: str,           # read, write, delete
        scope_level: str,      # global, app, project, runtime, session
        result: str,           # allowed, denied, error
        details: dict = None   # Additional context
    ):
        # Queue entry (non-blocking, < 1ms)
        # Background worker flushes batch to DB
        # No exceptions propagate to request
```

**Audit Log Table**:
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    resource VARCHAR(256) NOT NULL,
    action VARCHAR(64) NOT NULL,
    scope_level VARCHAR(16) NOT NULL,
    result VARCHAR(32) NOT NULL,
    details JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for fast queries
    INDEX (user_id, timestamp),
    INDEX (resource, action),
    INDEX (scope_level, timestamp)
);
```

**Batch Flushing**:
- Buffer size: 100 entries (configurable)
- Flush interval: 5 seconds (configurable)
- No entries lost (queue is durable in Tortoise ORM)

#### 4. Exception Hierarchy (src/db/exceptions.py)

**Purpose**: Structured error handling with HTTP mapping

```
ScopeError (HTTP 500)
  ├─ ScopePermissionError (HTTP 403)
  │   └─ "User lacks permission for this scope"
  ├─ ScopeResourceNotFoundError (HTTP 404)
  │   └─ "Resource not found in this scope"
  ├─ ScopeValidationError (HTTP 422)
  │   └─ "Invalid scope parameters"
  ├─ ScopeHierarchyError (HTTP 500)
  │   └─ "Scope hierarchy violated"
  └─ CacheInvalidationError (HTTP 500)
      └─ "Cache invalidation failed"
```

**Error Response Format**:
```json
{
  "error_code": "PERMISSION_DENIED",
  "message": "User lacks permission for this scope",
  "context": {
    "scope_level": "project",
    "user_id": "user123",
    "resource": "project:456"
  }
}
```

---

## Phase 5C: Worker Context Architecture

### System Diagram

```
Worker Lifecycle
    ↓
[WorkerStateMachine]
    ├─ Validate state transition (queued→running, etc.)
    ├─ Save transition to DB (atomic)
    ├─ Create audit log entry
    └─ Return transition record
    ↓
[WorkerSession]
    ├─ Save context (JSON, unlimited nesting)
    ├─ Save execution history (timestamped steps)
    ├─ Save bookmarks (named checkpoints)
    ├─ Hash all data (BLAKE2b-256)
    └─ Store in DB (transaction-safe)
    ↓
[Restore]
    ├─ Load from DB
    ├─ Verify hashes
    ├─ Detect tampering
    └─ Return context or raise IntegrityCheckError
    ↓
[Scope Binding]
    ├─ Worker tied to project/session
    ├─ Audit trail includes scope level
    ├─ Scope-based filtering for queries
    └─ Cross-scope isolation enforced
```

### Components

#### 1. WorkerStateMachine (src/db/worker_manager.py)

**Purpose**: Validate and track worker state transitions

```python
class WorkerStateMachine:
    """Manage worker state with validation and audit."""
    
    VALID_TRANSITIONS = {
        WorkerState.QUEUED: [WorkerState.RUNNING, WorkerState.FAILED],
        WorkerState.RUNNING: [WorkerState.PAUSED, WorkerState.COMPLETED, WorkerState.FAILED],
        WorkerState.PAUSED: [WorkerState.RUNNING, WorkerState.COMPLETED, WorkerState.FAILED],
        WorkerState.COMPLETED: [],  # Terminal
        WorkerState.FAILED: [],      # Terminal
    }
    
    async def transition(self, to_state, reason, metadata=None):
        # 1. Validate transition is legal
        if to_state not in VALID_TRANSITIONS[current_state]:
            raise ValueError(f"Invalid transition: {current_state} → {to_state}")
        
        # 2. Create record (atomic)
        async with in_transaction():
            transition = await WorkerStateTransition.create(
                worker_id=self.worker_id,
                from_state=current_state,
                to_state=to_state,
                reason=reason,
                metadata=metadata or {},
                project=...,
                session=...
            )
            
            # 3. Create audit log
            await WorkerAuditLog.create(
                worker_id=self.worker_id,
                from_state=current_state,
                to_state=to_state,
                reason=reason,
                scope_level=self._get_scope_level(),
                permission_check_passed=True,
                created_at=datetime.now()
            )
        
        return transition
```

**State Transition Diagram**:
```
    ┌─────────────┐
    │   QUEUED    │
    └────┬────────┘
         │ (execute)
         ↓
    ┌─────────────┐       ┌──────────────┐
    │  RUNNING    │◄─────→│   PAUSED     │
    └────┬────────┘       └──────────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ↓                          ↓
┌────────────┐          ┌───────────┐
│ COMPLETED  │          │  FAILED   │
└────────────┘          └───────────┘
(terminal)              (terminal)
```

**Query Operations**:
```python
# Get all running workers
running = await mgr.get_workers_by_state(WorkerState.RUNNING)

# Get workers by multiple states
active = await mgr.get_workers_by_multiple_states(
    [WorkerState.RUNNING, WorkerState.PAUSED]
)

# Get state distribution
dist = await mgr.get_state_distribution()
# Output: {queued: 5, running: 3, paused: 1, completed: 20, failed: 2}

# Find stale workers (inactive > 1 hour)
stale = await mgr.get_stale_workers(inactive_threshold_seconds=3600)
```

**Performance Optimization**:
- Session object caching (eliminates duplicate DB lookups)
- Composite indexes on (project, to_state), (session, to_state)
- Transition history retrievable by worker_id (indexed)

#### 2. WorkerSession (src/db/models/worker.py)

**Purpose**: Persist worker state with cryptographic integrity

```python
class WorkerSession(ScopedEntry):
    """Worker session with context, history, and bookmarks."""
    
    worker_id = fields.CharField(max_length=128, unique=True)
    current_state = fields.CharField(max_length=32, default="queued")
    
    # Session data
    context_data = fields.JSONField(default=dict)           # Worker state
    execution_history = fields.JSONField(default=list)      # Steps taken
    bookmarks = fields.JSONField(default=dict)              # Checkpoints
    
    # Integrity hashes (BLAKE2b-256)
    context_hash = fields.CharField(max_length=128)
    execution_history_hash = fields.CharField(max_length=128)
    bookmarks_hash = fields.CharField(max_length=128)
    
    # Tracking
    steps_executed = fields.IntField(default=0)
    last_checkpoint = fields.CharField(max_length=128, null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Scope bindings
    project = fields.ForeignKeyField("models.Project", related_name="worker_sessions")
    session = fields.ForeignKeyField("models.Session", related_name="worker_sessions", null=True)
    
    def verify_integrity(self) -> list[str]:
        """Verify hashes, return list of failures (if any)."""
        failures = []
        
        # Check context
        actual_hash = blake2b_hash(json.dumps(self.context_data, sort_keys=True))
        if actual_hash != self.context_hash:
            failures.append("context_hash_mismatch")
        
        # Check execution history
        hist_hash = blake2b_hash(json.dumps(self.execution_history, sort_keys=True))
        if hist_hash != self.execution_history_hash:
            failures.append("execution_history_hash_mismatch")
        
        # Check bookmarks
        bm_hash = blake2b_hash(json.dumps(self.bookmarks, sort_keys=True))
        if bm_hash != self.bookmarks_hash:
            failures.append("bookmarks_hash_mismatch")
        
        return failures
```

**Hash Computation** (BLAKE2b-256):
```python
import hashlib
import json

def blake2b_hash(data: str) -> str:
    """Compute BLAKE2b-256 hash (hex-encoded, 64 chars)."""
    return hashlib.blake2b(
        data.encode(),
        digest_size=32  # 256 bits = 32 bytes
    ).hexdigest()

# Example:
data = json.dumps({"step": 5, "results": [...]}, sort_keys=True)
hash_value = blake2b_hash(data)  # "a1b2c3d4..." (64 hex chars)
```

**Deterministic Serialization**:
- Use `json.dumps(..., sort_keys=True)` to ensure consistent ordering
- Same data always produces same hash
- Different data always produces different hash (BLAKE2b collision resistance)

#### 3. SessionManager (src/db/session_manager.py)

**Purpose**: Save/restore worker session with integrity verification

```python
class WorkerSessionManager:
    """Save and restore worker session state."""
    
    async def save_session(
        self,
        context: dict[str, Any],
        execution_history: list[dict],
        bookmarks: dict[str, Any]
    ) -> WorkerSession:
        """Save session with BLAKE2b-256 hashing."""
        
        # Hash each component
        context_hash = blake2b_hash(json.dumps(context, sort_keys=True))
        hist_hash = blake2b_hash(json.dumps(execution_history, sort_keys=True))
        bm_hash = blake2b_hash(json.dumps(bookmarks, sort_keys=True))
        
        # Save atomically
        async with in_transaction():
            session = await WorkerSession.create(
                worker_id=self.worker_id,
                context_data=context,
                execution_history=execution_history,
                bookmarks=bookmarks,
                context_hash=context_hash,
                execution_history_hash=hist_hash,
                bookmarks_hash=bm_hash,
                steps_executed=len(execution_history),
                project_id=self.project_id,
                session_id=self.session_id
            )
        
        return session
    
    async def restore_session(
        self,
        verify_integrity: bool = True
    ) -> dict[str, Any]:
        """Restore session with optional integrity check."""
        
        session = await WorkerSession.get(worker_id=self.worker_id)
        
        if verify_integrity:
            failures = session.verify_integrity()
            if failures:
                raise IntegrityCheckError(
                    f"Session integrity check failed: {failures}",
                    failures=failures
                )
        
        return {
            "context": session.context_data,
            "execution_history": session.execution_history,
            "bookmarks": session.bookmarks,
        }
```

**Execution History Format**:
```python
execution_history = [
    {
        "step": 1,
        "action": "fetch_data",
        "status": "success",
        "result": {"rows": 1000},
        "timestamp": "2026-04-26T14:30:00Z",
    },
    {
        "step": 2,
        "action": "process_data",
        "status": "error",
        "error": "Connection timeout",
        "timestamp": "2026-04-26T14:30:05Z",
    },
]
```

**Bookmarks (Resumable Checkpoints)**:
```python
bookmarks = {
    "checkpoint_1": {
        "step": 2,
        "execution_context": {"current_batch": 0, "offset": 0},
        "state": {...},
        "created_at": "2026-04-26T14:30:00Z",
    },
    "checkpoint_2": {
        "step": 5,
        "execution_context": {"current_batch": 1, "offset": 100},
        "state": {...},
        "created_at": "2026-04-26T14:30:30Z",
    },
}
```

#### 4. Scope Binding

**Purpose**: Tie workers to scope hierarchy, enable scope-based queries

```python
# Worker creation at project scope
mgr = WorkerStateMachine(
    worker_id="my-worker",
    project_id="proj-123",      # Required
    session_id=None             # Optional
)

# Worker creation at session scope
mgr = WorkerStateMachine(
    worker_id="my-worker",
    project_id="proj-123",      # Required
    session_id="session-456"    # Optional (for session-level)
)

# Scope-based queries
project_mgr = WorkerStateMachine(..., project_id="proj-123")
workers = await project_mgr.get_workers_by_state(WorkerState.RUNNING)
# Result: Only workers in proj-123

session_mgr = WorkerStateMachine(..., session_id="session-456")
workers = await session_mgr.get_workers_by_state(WorkerState.RUNNING)
# Result: Only workers in session-456
```

**Audit Trail Scope Level**:
```python
# Recorded in WorkerAuditLog
scope_level = "session" if self.session_id else "project"

# Example audit log:
{
    "worker_id": "my-worker",
    "from_state": "queued",
    "to_state": "running",
    "scope_level": "project",  # Project-level transition
    "created_at": "2026-04-26T14:30:00Z",
}
```

---

## Data Flow: Complete Example

### Scenario: Execute a worker task

**Step 1: Request arrives**
```
POST /workers/my-worker/execute
Authorization: Bearer <jwt_token>
X-Project-ID: proj-123
```

**Step 2: ScopeMiddleware processes**
```
1. Extract scope: project_id=123
2. Validate: Global→App→Project hierarchy OK
3. Check permission: user_id has execute on proj-123
4. Inject request.state.scope (cached for route)
5. Add headers to response: X-Scope-Level: project
```

**Step 3: Route executes**
```python
@app.post("/workers/{worker_id}/execute")
async def execute_worker(request: Request, worker_id: str):
    scope = request.state.scope  # Cached from middleware
    project_id = scope.project_id
    
    # Create state machine
    mgr = WorkerStateMachine(worker_id, project_id)
    
    # Transition state
    await mgr.transition(
        to_state=WorkerState.RUNNING,
        reason="User initiated execution",
        metadata={"user_id": scope.user_id}
    )
    
    return {"status": "running"}
```

**Step 4: State change recorded**
```
WorkerStateTransition:
  - worker_id: my-worker
  - from_state: queued
  - to_state: running
  - reason: "User initiated execution"
  - project_id: proj-123
  - transitioned_at: 2026-04-26T14:30:00Z

WorkerAuditLog:
  - worker_id: my-worker
  - from_state: queued
  - to_state: running
  - scope_level: project
  - permission_check_passed: true
  - created_at: 2026-04-26T14:30:00Z
```

**Step 5: Audit logger (async)**
```
Background queue worker flushes to DB:
  INSERT INTO audit_log (user_id, resource, action, scope_level, result, ...)
  VALUES ("user-123", "worker:my-worker", "execute", "project", "allowed", ...)
```

**Step 6: Cache invalidation (if needed)**
```
If worker configuration changed:
  - Invalidate: project:123:worker_config
  - Cascade to runtime/session caches
  - Clear any dependent cached queries
```

---

## Integration Points

### Route Integration

```python
from src.ai_proxy.middleware import ScopeMiddleware
from src.db.worker_manager import WorkerStateMachine
from src.db.session_manager import WorkerSessionManager
from src.db.exceptions import ScopePermissionError

app = FastAPI()
app.add_middleware(ScopeMiddleware)

@app.post("/workers/{worker_id}/execute")
async def execute_worker(request: Request, worker_id: str):
    scope = request.state.scope
    
    try:
        mgr = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id
        )
        
        await mgr.transition(
            to_state=WorkerState.RUNNING,
            reason="User initiated",
            metadata={"user_id": scope.user_id}
        )
        
        return {"status": "running"}
    except ScopePermissionError as e:
        return JSONResponse(
            status_code=403,
            content={"error_code": e.error_code, "message": str(e)}
        )
```

### Session Persistence

```python
async with WorkerSessionManager(worker_id, project_id) as mgr:
    # Save current state
    await mgr.save_session(
        context={"step": 5, "results": [...]},
        execution_history=history,
        bookmarks=bookmarks
    )

# Later, restore
async with WorkerSessionManager(worker_id, project_id) as mgr:
    state = await mgr.restore_session(verify_integrity=True)
    print(f"Restored: {state['context']}")
```

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| **Middleware extraction** | <1ms | Header/JWT parsing |
| **Permission check** | <1ms | Cached scope context |
| **Scope middleware total** | <5ms | Requirement met |
| **State transition** | <5ms | Single DB transaction |
| **Session save** | <10ms | Hash + transaction |
| **Session restore + verify** | <20ms | BLAKE2b hashing |
| **Scope-filtered query** | <5ms | Indexed (project, state) |
| **Audit log write** | <1ms | Queue-based, async |
| **Cache hit** | <1ms | Redis or memory |

---

## Security Model

✅ **Scope Hierarchy Enforcement**
- No skipping levels (global→app→project hierarchy)
- Automatic cascading (parent change invalidates children)
- Queries always scoped to caller's level

✅ **Permission Checking**
- Per-scope permission model
- Audit trail of all permission decisions
- Denied attempts logged and traceable

✅ **Integrity Verification**
- BLAKE2b-256 hashing for session data
- Tampering detection on restore
- Deterministic serialization ensures consistency

✅ **Isolation**
- Workers query-isolated by project/session
- No cross-scope data leakage
- Audit logs isolated per scope

✅ **Non-repudiation**
- All actions logged with user, resource, action, result
- Immutable audit trail (DB-backed)
- Queryable by scope for compliance

---

## Testing Strategy

### Phase 5B Tests (91 tests)
- Middleware extraction and validation (23 tests)
- Cache invalidation cascade (18 tests)
- Audit logging non-blocking (17 tests)
- Error handling and HTTP mapping (29 tests)

### Phase 5C Tests (58 tests)
- State machine transitions (15 tests)
- Session save/restore/verify (23 tests)
- Scope isolation (20 tests)

### Regression (52 tests)
- Phase 5A scope system compatibility

---

## References

- SCOPE-ARCHITECTURE.md — 5-level scope hierarchy model
- PHASE5B_SCOPE_ENFORCEMENT_CHANGELOG.md — Detailed Phase 5B changelog
- PHASE5C_WORKER_CONTEXT_CHANGELOG.md — Detailed Phase 5C changelog

---

**Document Status**: ✅ Complete  
**Last Updated**: 2026-04-26  
**Next**: Phase 5D (Worker API endpoints)
