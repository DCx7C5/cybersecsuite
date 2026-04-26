# Phase 5D Briefing: Worker API & Lifecycle — 2026-04-26

**Status**: Phase 5B & 5C Complete ✅ | Phase 5D Ready to Dispatch  
**Session**: d1cb85db-c7c8-42e0-bf0c-018029e31bee  
**Date**: 2026-04-26 15:07 UTC

---

## 🎯 What Is Phase 5D?

**Objective**: Build RESTful API endpoints for worker lifecycle management  
**Scope**: 4-6 todos, ~8-12 hours estimated  
**Position**: Phase 5D comes after Phase 5C (worker state machine)  
**Next**: Phase 5E (worker dashboard UI)

### Architecture Stack
```
Phase 5A ✅ — Scope enforcement (5-level hierarchy, RBAC)
Phase 5B ✅ — Scope middleware (<5ms overhead)
Phase 5C ✅ — Worker state machine + session persistence
Phase 5D 👈 — Worker API endpoints (CRUD, lifecycle, monitoring)
Phase 5E ⏳ — Worker dashboard UI (React components)
```

---

## 📋 Quick Todo Reference

| ID | Title | Effort | Tests | Status |
|----|----|--------|-------|--------|
| **t369** | Worker CRUD API | 3h | 25-35 | pending |
| **t370** | Worker lifecycle transitions | 2.5h | 20-25 | pending |
| **t371** | Execution history & bookmarks | 2.5h | 20-25 | pending |
| **t372** | Worker metrics & monitoring | 2h | 15-20 | pending |
| **t373** | Worker batch operations (opt.) | 1.5h | 10-15 | pending |

**Total**: 4-6 todos, ~11-15 hours, 90-120 tests expected

---

## 🔑 Key Todos Explained

### t369: Worker CRUD API
Create the fundamental REST endpoints for workers:
- `POST /api/workers` — Create new worker
- `GET /api/workers?project_id=X` — List + filter
- `GET /api/workers/{id}` — Fetch one
- `PATCH /api/workers/{id}` — Update config
- `DELETE /api/workers/{id}` — Soft delete

**Scope Binding**: All endpoints validate scope via middleware  
**Test Focus**: Permission checks, cross-project isolation  
**Effort**: ~3 hours

### t370: Worker Lifecycle Transitions
State machine endpoints for worker lifecycle:
- `POST /api/workers/{id}/start` — queued → running
- `POST /api/workers/{id}/pause` — running → paused
- `POST /api/workers/{id}/resume` — paused → running
- `POST /api/workers/{id}/stop` — running/paused → completed
- `POST /api/workers/{id}/retry` — failed → queued

**Key**: Delegate to WorkerStateMachine (Phase 5C) for transitions  
**Test Focus**: Valid/invalid transitions, 409 conflict handling  
**Effort**: ~2.5 hours

### t371: Execution History & Bookmarks
Query API for worker execution tracking:
- `GET /api/workers/{id}/history` — List execution steps (paginated)
- `POST /api/workers/{id}/bookmarks` — Create save point
- `GET /api/workers/{id}/bookmarks` — List bookmarks
- `DELETE /api/workers/{id}/bookmarks/{bid}` — Remove bookmark

**Key**: Leverage WorkerSessionManager + ExecutionHistoryManager from Phase 5C  
**Test Focus**: Pagination, filtering, bookmark lifecycle  
**Effort**: ~2.5 hours

### t372: Worker Metrics & Monitoring
Observability endpoints:
- `GET /api/workers/{id}/metrics` — Current metrics (step count, success rate)
- `GET /api/workers/{id}/audit` — Audit trail (scope + action + user)
- `GET /api/workers/summary?project_id=X` — Aggregate stats
- `GET /api/health/workers` — Subsystem health

**Key**: No N+1 queries (use select_related, aggregate functions)  
**Test Focus**: Aggregation, filtering, performance  
**Effort**: ~2 hours

### t373: Worker Batch Operations (Optional)
Bulk operations for convenience:
- `POST /api/workers/batch/start` — Start multiple workers
- `POST /api/workers/batch/stop` — Stop multiple workers
- `PATCH /api/workers/batch/update` — Update config for multiple

**Key**: Atomic per worker (one failure doesn't block others)  
**Test Focus**: Mixed success/failure, large batches  
**Effort**: ~1.5 hours

---

## 📂 Files Involved

### Route Files (New ~1,200 lines)
```
src/api/routes/workers.py              ~ 400 lines (CRUD + lifecycle)
src/api/routes/worker_history.py       ~ 250 lines (history + bookmarks)
src/api/routes/worker_metrics.py       ~ 200 lines (metrics + health)
src/api/routes/worker_batch.py         ~ 150 lines (optional)
```

### Test Files (New ~1,500 lines)
```
tests/test_worker_api_crud.py          ~ 350 lines
tests/test_worker_lifecycle.py         ~ 300 lines
tests/test_worker_history.py           ~ 250 lines
tests/test_worker_metrics.py           ~ 200 lines
tests/test_worker_batch.py             ~ 150 lines (optional)
```

### Modifications
```
src/startup/routes.py                  (add route registration)
src/api/__init__.py                    (add exports)
```

### No Schema Changes
✅ All database models already exist from Phase 5C (WorkerState, WorkerSession, WorkerAuditLog)

---

## 🧠 Implementation Strategy

### Sequence (Recommended)
1. **t369 first** — Foundation (CRUD endpoints, response structure)
2. **t370 second** — Builds on t369 (state transitions via CRUD routes)
3. **t371 third** — Independent (history API, bookmarks)
4. **t372 fourth** — Independent (metrics, health check)
5. **t373 last** — Optional bonus (batch operations)

### Key Patterns to Follow

**Route Dependency Injection**:
```python
from fastapi import APIRouter, Depends, Request
from src.db.worker_manager import WorkerStateMachine
from src.db.session_manager import WorkerSessionManager

async def get_scope_context(request: Request):
    return request.state.scope_context  # From middleware

router = APIRouter()

@router.post("/workers/{worker_id}/start")
async def start_worker(
    worker_id: str,
    scope: ScopeContext = Depends(get_scope_context)
):
    # Validate scope
    # Call WorkerStateMachine.transition()
    # Log to audit trail
    # Return response
```

**Error Response Template**:
```python
{
    "error": "scope_permission_denied",
    "message": "User lacks permission for project scope",
    "scope_level": "project",
    "resource": "worker:w123",
    "request_id": "req-abc123"
}
```

**Pagination Template**:
```python
@router.get("/workers/{id}/history")
async def get_history(
    worker_id: str,
    limit: int = Query(30, le=100),
    offset: int = Query(0),
    action: Optional[str] = Query(None),
    since: Optional[str] = Query(None)
):
    # Build ORM query with filters
    # Paginate (offset, limit)
    # Return {items: [...], total: N, offset: O, limit: L}
```

---

## ✅ Acceptance Criteria

### All Todos Must Have:
- [x] All endpoints implemented (no placeholders)
- [x] 80%+ test coverage (happy path + errors)
- [x] Scope enforcement on every endpoint
- [x] Proper HTTP status codes (200/201/400/403/404/409/422)
- [x] Audit logging for all state-changing operations
- [x] Pagination support (list/history endpoints)
- [x] Error responses with context (error, message, request_id)
- [x] No N+1 queries verified in tests
- [x] All Phase 5A/5B/5C tests still passing (no regressions)

### Performance Requirements:
- ✅ List endpoints: <500ms (100 items)
- ✅ Metrics aggregation: <1s (1000+ workers)
- ✅ State transitions: <100ms
- ✅ History pagination: <300ms (100 items)

---

## 🔗 Phase 5C Dependencies (Already Available)

### WorkerStateMachine (Phase 5C)
```python
from src.db.worker_manager import WorkerStateMachine

# Use this to validate state transitions
machine = WorkerStateMachine(worker_id, project_id, session_id)
await machine.transition(
    from_state=WorkerStateEnum.running,
    to_state=WorkerStateEnum.paused,
    context={"checkpoint_id": "cp123"}
)
```

### WorkerSessionManager (Phase 5C)
```python
from src.db.session_manager import WorkerSessionManager

# Use this to save/restore worker context
manager = WorkerSessionManager(worker_id, project_id)
session = await manager.save_state(context, bookmarks)
restored = await manager.restore_state(session_id)
```

### AuditLog Model (Phase 5B)
```python
from src.db.models.core import AuditLog

# Log all operations
await AuditLog.create(
    scope_level="project",
    resource="worker:w123",
    action="start_worker",
    user_id="user123",
    result="success",
    details={"old_state": "queued", "new_state": "running"}
)
```

### ScopeMiddleware (Phase 5B)
```
# All routes automatically have scope_context in request.state
scope_context = request.state.scope_context
# Contains: project_id, session_id, user_id, scope_level, permissions
```

---

## 📊 Expected Test Matrix

For each endpoint, test:

| Scenario | Expected | Tests |
|----------|----------|-------|
| Happy path (200 OK) | Data returned | 1 |
| Missing auth | 401 Unauthorized | 1 |
| Scope denied | 403 Forbidden | 1 |
| Resource not found | 404 Not Found | 1 |
| Invalid input | 400 Bad Request | 1 |
| Invalid state transition | 409 Conflict | 1 |
| Cross-project isolation | 403 Forbidden | 1 |

**Per-todo estimate**: 4-6 endpoints × 6-7 scenarios = 24-42 tests

---

## 🚀 Dispatch Template for Agents

When delegating, use:

```
Implement Phase 5D: Worker API & Lifecycle (4-6 todos)

**Todos to implement:**
1. t369: Worker CRUD API
2. t370: Worker lifecycle transitions  
3. t371: Execution history & bookmarks
4. t372: Worker metrics & monitoring
5. (Optional) t373: Batch operations

**Architecture:**
- Build on WorkerStateMachine + WorkerSessionManager from Phase 5C
- All routes in src/api/routes/*.py
- Use ScopeMiddleware for authorization (Phase 5B)
- Log via AuditLog model
- Return structured JSON with error context

**Performance targets:**
- <500ms for list endpoints (100 items)
- <1s for metrics aggregation
- <100ms for state transitions

**Testing requirements:**
- 80%+ coverage per route file
- Test happy path + all error cases
- Verify scope isolation (cross-project boundaries)
- Check for N+1 queries
- Ensure Phase 5A/5B/5C tests still pass

Ready to proceed?
```

---

## 🔍 SQL Queries (Copy-Paste Ready)

Load Phase 5D todos:
```sql
INSERT INTO todos (id, title, description, status) VALUES
  ('t369', 'Worker CRUD API', 'Create/read/update/delete endpoints', 'pending'),
  ('t370', 'Worker lifecycle transitions', 'Start/pause/resume/stop endpoints', 'pending'),
  ('t371', 'Execution history & bookmarks', 'Query history and manage bookmarks', 'pending'),
  ('t372', 'Worker metrics & monitoring', 'Query metrics, audit trail, health', 'pending');

-- Optional:
INSERT INTO todos (id, title, description, status) VALUES
  ('t373', 'Worker batch operations', 'Batch start/stop/update', 'pending');
```

Check status:
```sql
SELECT id, title, status FROM todos WHERE id IN ('t369', 't370', 't371', 't372', 't373') ORDER BY id;
```

Mark as done:
```sql
UPDATE todos SET status = 'done' WHERE id = 't369';
```

---

## 📌 Important Links

**Session Data**:
- Plan: `/home/daen/.copilot/session-state/d1cb85db-c7c8-42e0-bf0c-018029e31bee/plan.md`
- Database: `/home/daen/.copilot/session-state/d1cb85db-c7c8-42e0-bf0c-018029e31bee/session.db`

**Documentation**:
- Phase 5B: `docs/changelog/phase5b_scope_enforcement_changelog.md`
- Phase 5C: `docs/changelog/phase5c_worker_context_changelog.md`
- Architecture: `docs/architecture/scope-enforcement-worker-architecture.md`

**Key Source Files**:
- WorkerStateMachine: `src/db/worker_manager.py` (294 lines)
- WorkerSessionManager: `src/db/session_manager.py` (476 lines)
- Worker models: `src/db/models/worker.py` (443 lines)
- Middleware: `src/ai_proxy/middleware.py` (487 lines)

---

## 🎯 Success Criteria

Phase 5D is **complete** when:
- [x] All 4-6 todos implemented
- [x] 90%+ total test coverage
- [x] All endpoints scope-enforced
- [x] No N+1 queries in metrics/history
- [x] All Phase 5A/5B/5C tests passing
- [x] Performance targets met

**Estimated Total Time**: 8-12 hours (4-6 hours analysis + code review + testing)

---

**Status**: 🚀 Ready to dispatch Phase 5D  
**Next Update**: After Phase 5D completion
