# Phase 5E: Worker Dashboard UI — 2026-04-26

**Status**: In Progress  
**Todos**: t373–t375 (3 frontend components)  
**Dependencies**: Phase 5D API endpoints (19 endpoints, all live)

## Summary

Building React dashboard for worker monitoring with real-time updates. Integrates Phase 5D API (CRUD, lifecycle, metrics).

## Todos

### t373: Worker List Panel
- Table: name, status, progress, updated_at, owner
- Filters: project_id, status (queued/running/paused/completed/failed)
- Pagination (limit=30)
- Sort by name, status, updated_at
- GET /api/workers?project_id=X

### t374: Worker Detail Panel
- Config display (name, description, fields, scope_level)
- Metrics: step_count, success_rate, avg_duration
- Bookmarks list with timestamps
- History timeline (10 last steps)
- GET /api/workers/{id}/{metrics,bookmarks,history}

### t375: Worker State Controls
- Buttons: Start, Pause, Resume, Stop, Retry
- Disable invalid transitions
- Loading state, toast feedback
- POST /api/workers/{id}/{action}

## Deliverables

**Components:**
- WorkerListPanel.tsx
- WorkerDetailPanel.tsx
- WorkerStateControls.tsx
- hooks.ts (useWorkerList, useWorkerDetail, useWorkerMetrics)
- types.ts (TypeScript types)
- utils.ts (formatters, validators)

**Tests:**
- WorkerListPanel.test.tsx
- WorkerDetailPanel.test.tsx
- WorkerStateControls.test.tsx

**Stats:**
- 3 components (~600 lines)
- 60+ tests (~450 lines)
- 80%+ coverage
- Real-time polling: 5s

## Stack

- React 19 + TypeScript
- React Query (data fetching)
- Vite (bundler)
- Accessible (ARIA, keyboard nav)
- Responsive (mobile-friendly)
