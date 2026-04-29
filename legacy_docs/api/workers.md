# Worker API Reference — CyberSecSuite v0.1

**Status:** Stable (Phase 12+)  
**Mount Point:** `/api/workers`  
**Authentication:** Scope-based (project/session)

---

## Overview

The Worker API manages long-running task executors within CyberSecSuite. Workers progress through a state machine (queued → running → paused/completed/failed) and support batch operations, lifecycle management, audit trails, and metrics collection.

**Total Endpoints:** 21  
**Categories:** CRUD (5) + Lifecycle (5) + Batch (3) + History (4) + Metrics (4)

---

## State Machine

```
┌─────────┐
│ QUEUED  │ ← initial state after creation
└────┬────┘
     │ start()
     ▼
┌─────────┐      pause()       ┌────────┐
│ RUNNING │ ─────────────────► │ PAUSED │
└────┬────┘                    └───┬────┘
     │ success/failure             │ resume()
     │ + cleanup                   │
     ▼                             ▼
┌──────────────┬──────────────────┐
│ COMPLETED    │ FAILED           │
│ (success)    │ (error)          │
│ (cleanup)    │ (retry available)│
└──────────────┴──────────────────┘
```

---

## Scope-Based Access

All endpoints enforce scope isolation:
- **Project Scope:** Workers visible only within project
- **Session Scope:** Workers inherit project + session filtering
- **Headers Required:**
  - `X-Project-ID` (or project from JWT)
  - `X-Session-ID` (optional, for session scope)

---

## CRUD Endpoints (5)

### POST `/api/workers` — Create Worker
Create a new worker in queued state.

**Request:**
```python
{
    "name": str,                    # unique worker name
    "description": str,             # (optional) description
    "config": {                     # worker configuration
        "timeout_seconds": int,     # execution timeout
        "retry_max": int,          # max retries on failure
        "priority": int            # execution priority (0-10)
    },
    "tags": list[str]              # (optional) labels
}
```

**Response:** `201 Created`
```python
{
    "id": str,
    "name": str,
    "state": "queued",
    "created_at": datetime,
    "config": {...}
}
```

**Error Codes:**
- `400 Bad Request` — Missing required field or invalid config
- `409 Conflict` — Worker name already exists in project
- `403 Forbidden` — Insufficient scope permissions

---

### GET `/api/workers` — List Workers
List workers with filtering and pagination.

**Query Parameters:**
```
page: int (1+)                  # page number
size: int (1-100, default 50)   # page size
state: str (optional)            # filter by state (queued/running/paused/completed/failed)
tags: str (optional)             # comma-separated tag filter
```

**Response:** `200 OK`
```python
{
    "items": [
        {
            "id": str,
            "name": str,
            "state": str,
            "created_at": datetime,
            "updated_at": datetime
        }
    ],
    "total": int,
    "page": int,
    "size": int
}
```

---

### GET `/api/workers/{id}` — Get Worker
Retrieve a single worker by ID.

**Response:** `200 OK`
```python
{
    "id": str,
    "name": str,
    "state": str,
    "description": str,
    "config": {...},
    "created_at": datetime,
    "updated_at": datetime,
    "completed_at": datetime | null
}
```

**Error Codes:**
- `404 Not Found` — Worker doesn't exist
- `403 Forbidden` — Access denied (scope violation)

---

### PATCH `/api/workers/{id}` — Update Worker
Update worker configuration or metadata.

**Request:**
```python
{
    "name": str,                    # (optional) new name
    "description": str,             # (optional) new description
    "config": {                     # (optional) partial config update
        "timeout_seconds": int,
        "retry_max": int,
        "priority": int
    },
    "tags": list[str]              # (optional) replace tags
}
```

**Response:** `200 OK` (updated worker object)

**Note:** Can only update queued/paused workers. Running/completed workers are immutable.

---

### DELETE `/api/workers/{id}` — Delete Worker
Soft-delete a worker (marks as deleted, preserves audit trail).

**Response:** `204 No Content`

**Error Codes:**
- `409 Conflict` — Cannot delete running worker (stop first)
- `403 Forbidden` — Insufficient permissions

---

## Lifecycle Endpoints (5)

### POST `/api/workers/{id}/start` — Start Worker
Transition worker from queued → running.

**Request (Optional):**
```python
{
    "reason": str  # (optional) human-readable reason
}
```

**Response:** `200 OK`
```python
{
    "id": str,
    "state": "running",
    "started_at": datetime
}
```

**Error Codes:**
- `409 Conflict` — Invalid state transition (not queued)

---

### POST `/api/workers/{id}/pause` — Pause Worker
Transition worker from running → paused.

**Request:**
```python
{
    "reason": str,
    "checkpoint": dict  # (optional) save execution checkpoint
}
```

**Response:** `200 OK` (worker with state=paused)

---

### POST `/api/workers/{id}/resume` — Resume Worker
Transition worker from paused → running.

**Request:**
```python
{
    "reason": str,
    "restore_checkpoint": bool  # (optional, default=true)
}
```

**Response:** `200 OK`

---

### POST `/api/workers/{id}/stop` — Stop Worker
Transition worker from running → completed (with error cleanup).

**Request:**
```python
{
    "reason": str,
    "force": bool  # (optional, default=false) skip graceful shutdown
}
```

**Response:** `200 OK` (worker with state=completed)

---

### POST `/api/workers/{id}/retry` — Retry Worker
Retry a failed worker (failed → queued for restart).

**Request:**
```python
{
    "reason": str,
    "reset_config": bool  # (optional) reset to original config
}
```

**Response:** `200 OK` (worker with state=queued)

**Error Codes:**
- `409 Conflict` — Worker not in failed state
- `429 Too Many Requests` — Exceeded retry_max attempts

---

## Batch Endpoints (3)

### POST `/api/workers/batch/start` — Batch Start
Start multiple workers in a single request (atomic per worker).

**Request:**
```python
{
    "worker_ids": list[str],  # list of worker IDs
    "reason": str             # reason for batch operation
}
```

**Response:** `200 OK`
```python
{
    "batch_id": str,
    "results": [
        {
            "worker_id": str,
            "success": bool,
            "state": str,
            "error": str | null
        }
    ]
}
```

**Note:** Failures don't cascade. Each worker is processed independently.

---

### POST `/api/workers/batch/stop` — Batch Stop
Stop multiple workers.

**Request:**
```python
{
    "worker_ids": list[str],
    "reason": str,
    "force": bool
}
```

**Response:** `200 OK` (batch results)

---

### PATCH `/api/workers/batch/update` — Batch Update
Update configuration for multiple workers.

**Request:**
```python
{
    "worker_ids": list[str],
    "updates": {
        "config": {
            "timeout_seconds": int,
            "priority": int
        },
        "tags": list[str]
    }
}
```

**Response:** `200 OK` (batch results)

---

## History Endpoints (4)

### GET `/api/workers/{id}/history` — Execution History
Get execution history for a worker.

**Query Parameters:**
```
page: int (default 1)
size: int (default 50, max 1000)
action: str (optional) — filter by action (start/pause/resume/stop/error)
```

**Response:** `200 OK`
```python
{
    "items": [
        {
            "timestamp": datetime,
            "action": str,           # start/pause/resume/stop/error
            "duration_ms": int,
            "status": str,           # success/failure
            "details": dict
        }
    ],
    "total": int,
    "page": int
}
```

---

### POST `/api/workers/{id}/bookmarks` — Create Bookmark
Save a checkpoint/bookmark in execution history.

**Request:**
```python
{
    "name": str,          # bookmark name
    "data": dict,         # checkpoint data
    "description": str    # (optional)
}
```

**Response:** `201 Created`
```python
{
    "id": str,
    "timestamp": datetime,
    "name": str
}
```

---

### GET `/api/workers/{id}/bookmarks` — List Bookmarks
List all bookmarks for a worker.

**Response:** `200 OK`
```python
{
    "items": [
        {
            "id": str,
            "name": str,
            "timestamp": datetime,
            "description": str
        }
    ]
}
```

---

### DELETE `/api/workers/{id}/bookmarks/{bookmark_id}` — Delete Bookmark
Remove a specific bookmark.

**Response:** `204 No Content`

---

## Metrics Endpoints (4)

### GET `/api/workers/{id}/metrics` — Worker Metrics
Get performance metrics for a worker.

**Response:** `200 OK`
```python
{
    "worker_id": str,
    "total_runs": int,
    "successful_runs": int,
    "failed_runs": int,
    "average_duration_ms": float,
    "p50_duration_ms": float,
    "p95_duration_ms": float,
    "p99_duration_ms": float,
    "last_run_at": datetime,
    "success_rate": float         # 0.0-1.0
}
```

---

### GET `/api/workers/{id}/audit` — Audit Trail
Get detailed audit trail for a worker (paginated).

**Query Parameters:**
```
page: int (default 1)
size: int (default 50, max 1000)
action: str (optional) — filter by action type
```

**Response:** `200 OK`
```python
{
    "items": [
        {
            "timestamp": datetime,
            "user_id": str,
            "action": str,
            "changes": dict,
            "ip_address": str,
            "status": str
        }
    ],
    "total": int
}
```

---

### GET `/api/workers/summary` — Project Summary
Get aggregate statistics for all workers in a project.

**Query Parameters:**
```
project_id: int (optional, defaults to scope project)
```

**Response:** `200 OK`
```python
{
    "project_id": int,
    "total_workers": int,
    "by_state": {
        "queued": int,
        "running": int,
        "paused": int,
        "completed": int,
        "failed": int
    },
    "success_rate": float,
    "average_duration_ms": float,
    "total_executions": int
}
```

---

### GET `/api/workers/health` — Health Status
Get overall health status of worker system.

**Response:** `200 OK`
```python
{
    "status": str,              # healthy/degraded/unhealthy
    "workers_running": int,
    "workers_paused": int,
    "queue_depth": int,
    "average_wait_time_ms": float,
    "error_rate": float,
    "message": str
}
```

---

## Error Handling

All endpoints return standardized error responses:

```python
{
    "error": str,                # error code (e.g., "invalid_state")
    "message": str,              # human-readable message
    "request_id": str,           # correlate with logs
    "details": dict              # (optional) additional context
}
```

### Common Status Codes
- `200 OK` — Success
- `201 Created` — Resource created
- `204 No Content` — Success, no response body
- `400 Bad Request` — Invalid request
- `403 Forbidden` — Permission denied
- `404 Not Found` — Resource not found
- `409 Conflict` — Invalid state transition or conflict
- `429 Too Many Requests` — Rate limit exceeded
- `500 Internal Server Error` — Server error

---

## Examples

### Create and Start a Worker
```bash
# Create
curl -X POST http://localhost:8000/api/workers \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: 42" \
  -d '{
    "name": "forensics-scan",
    "config": {"timeout_seconds": 3600}
  }'

# Start
curl -X POST http://localhost:8000/api/workers/w-12345/start \
  -H "X-Project-ID: 42" \
  -d '{"reason": "User initiated"}'
```

### Batch Start 5 Workers
```bash
curl -X POST http://localhost:8000/api/workers/batch/start \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: 42" \
  -d '{
    "worker_ids": ["w-1", "w-2", "w-3", "w-4", "w-5"],
    "reason": "Daily scan batch"
  }'
```

### Get Metrics for a Worker
```bash
curl http://localhost:8000/api/workers/w-12345/metrics \
  -H "X-Project-ID: 42"
```

---

## Rate Limiting

Workers API enforces rate limits per project:
- **List/Get:** 100 req/min
- **Create/Update:** 50 req/min
- **Batch:** 10 req/min
- **Metrics:** 60 req/min

See `X-RateLimit-*` response headers for current quota.

---

## Pagination

List endpoints support cursor-based pagination:
- `page` — page number (1-based)
- `size` — results per page (1-100, default 50)

Response includes:
- `total` — total matching records
- `page` — current page number
- `size` — requested page size

---

## Related Documentation

- **Worker State Machine:** [Architecture → Worker API](../architecture/overview.md#layer-2-worker-api)
- **Scope System:** [Scope-Based Access Control](../architecture/scope-system.md)
- **ASGI Routing:** [ASGI Proxy Mounts](../architecture/asgi-proxy.md)
- **Audit Logging:** [Audit Trail System](../architecture/audit-logging.md)
