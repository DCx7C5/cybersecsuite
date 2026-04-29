# Deprecation Audit: `src/api/`

**Date:** 2025-07-26  
**Verdict:** ✅ ACTIVE — fixed two registration gaps

## Evidence

| Signal | Detail |
|--------|--------|
| **Imports in `tests/`** | 5 test files import routers: `test_worker_api_crud.py`, `test_worker_metrics.py`, `test_worker_lifecycle.py`, `test_worker_history.py`, `test_worker_batch.py` |
| **Route files** | 5 FastAPI routers covering worker CRUD, lifecycle transitions, metrics, execution history, and batch operations |
| **DB models used** | `db.models.worker.WorkerSession`, `WorkerState`, `WorkerAuditLog` (all actively referenced) |
| **Test result (pre-fix)** | 141 tests passing across worker API suites |

## Issues Found & Fixed

### 1. Missing from `pyproject.toml` packages
`src/api` was absent from `[tool.hatch.build.targets.wheel].packages`, meaning the package
would not be included in a built wheel. **Fixed:** added `"src/api"` to the list.

### 2. Routes not mounted in ASGI app
All 5 routers were tested in isolation but never wired into `src/proxy/asgi.py`, so requests
to `/api/workers/*` would return 404 in production. **Fixed:** created a FastAPI sub-app
(`_worker_api`) that includes all 5 routers and mounted it at the root of the Starlette app.

## Rationale

`src/api/` provides the REST layer for the Worker management subsystem (tasks t369–t373).
It is backed by real ORM models, has comprehensive test coverage, and is an integral part of
the CyberSecSuite platform. It is not deprecated — it was simply missing its production
registration.
