# Phase 5E Briefing: Worker Dashboard UI — 2026-04-26

**Status**: Phase 5A-5D Complete ✅ | Phase 5E Ready to Dispatch  
**Session**: d1cb85db-c7c8-42e0-bf0c-018029e31bee  
**Date**: 2026-04-26 16:08 UTC

---

## 🎯 What Is Phase 5E?

**Objective**: Build React dashboard UI for worker lifecycle visualization and management  
**Scope**: 4-6 todos, ~12-18 hours estimated  
**Position**: Phase 5E comes after Phase 5D (worker API endpoints)  
**Next**: Phase 6 (orchestrator enhancements)

### Architecture Stack
```
Phase 5A ✅ — Scope enforcement (5-level hierarchy, RBAC)
Phase 5B ✅ — Scope middleware (<5ms overhead)
Phase 5C ✅ — Worker state machine + session persistence
Phase 5D ✅ — Worker API endpoints (CRUD, lifecycle, monitoring)
Phase 5E 👈 — Worker dashboard UI (React components, WebSocket)
```

---

## 📋 Quick Todo Reference

| ID | Title | Effort | Tests | Status |
|----|----|----|-------|--------|
| **t374** | Worker list view + search | 3h | 20-25 | pending |
| **t375** | Worker detail view + actions | 2.5h | 15-20 | pending |
| **t376** | Real-time WebSocket updates | 3h | 15-20 | pending |
| **t377** | Execution timeline + bookmarks UI | 2.5h | 10-15 | pending |
| **t378** | Metrics dashboard + charts | 2h | 10-15 | pending |
| **t379** | Batch operations UI (optional) | 1.5h | 8-10 | pending |

**Total**: 5-6 todos, ~12-18 hours, 70-100 tests expected

---

## 🔑 Key Todos Explained

### t374: Worker List View + Search
Build the main worker list dashboard:
- Paginated list with columns: worker_id, name, state, steps, success_rate
- Search by worker name/ID
- Filter by state (queued, running, paused, completed, failed)
- Sort by: name, state, created_at, last_activity
- Select multiple workers (for batch ops)
- Real-time status badge colors

**Components**: WorkerList, WorkerSearchBar, WorkerListItem, StateFilter  
**API Integration**: GET /api/workers with pagination + filters  
**Effort**: ~3 hours

### t375: Worker Detail View + Actions
Build detailed worker profile:
- Header: worker_id, name, description, worker_type
- Current state with transition buttons (start/pause/resume/stop/retry)
- Config details: timeout, retry_count, priority
- Execution metrics: steps, success_rate, uptime, avg_duration
- Action menu: edit config, delete, view bookmarks

**Components**: WorkerDetail, WorkerActions, WorkerMetrics, StateTransitionButtons  
**API Integration**: GET /api/workers/{id}, POST /api/workers/{id}/start, etc.  
**Effort**: ~2.5 hours

### t376: Real-time WebSocket Updates
Enable live data pushing to dashboard:
- WebSocket connection to /ws/workers/{project_id}
- Push events: worker_state_changed, metrics_updated, audit_logged
- Auto-reconnect on disconnect
- Message batching (update every 500ms)
- Unsubscribe on component unmount

**Technical**: Socket.io or raw WebSocket, message queue, reconnection logic  
**Effort**: ~3 hours

### t377: Execution Timeline + Bookmarks UI
Visualize worker execution history:
- Timeline view: execution steps with timestamps
- Filter by action type, date range
- Bookmark markers on timeline
- Create/delete bookmarks from UI
- Jump to bookmark (restore state)
- Export timeline as JSON

**Components**: ExecutionTimeline, TimelineItem, BookmarkManager  
**API Integration**: GET /api/workers/{id}/history, POST/DELETE /api/workers/{id}/bookmarks  
**Effort**: ~2.5 hours

### t378: Metrics Dashboard + Charts
Display worker metrics with visualization:
- Worker metrics card: steps, success_rate, uptime_ms
- Project summary stats: total, running, paused, completed, failed, queued
- Health status indicator (green/yellow/red)
- Charts: state distribution (pie), success rate (line), uptime trends
- Audit log pagination

**Components**: MetricsCard, ProjectSummary, StateChart, HealthIndicator  
**API Integration**: GET /api/workers/{id}/metrics, GET /api/workers/summary, GET /api/health/workers  
**Effort**: ~2 hours

### t379: Batch Operations UI (Optional)
Build UI for bulk worker operations:
- Multi-select workers from list
- Batch action buttons: Start All, Stop All, Edit Config
- Modal dialog for batch updates
- Progress bar during batch operation
- Results modal: success count, failure details

**Components**: BatchActionButtons, BatchModal, ProgressBar, ResultsModal  
**API Integration**: POST /api/workers/batch/start, POST /api/workers/batch/stop, PATCH /api/workers/batch/update  
**Effort**: ~1.5 hours

---

## 📂 Files Involved

### Component Files (New ~800 lines)
```
src/frontend/src/components/workers/
├── WorkerList.tsx               ~ 250 lines
├── WorkerDetail.tsx             ~ 200 lines
├── WorkerActions.tsx            ~ 100 lines
├── ExecutionTimeline.tsx        ~ 150 lines
├── MetricsCard.tsx              ~ 100 lines
└── BatchOperations.tsx          ~ 100 lines
```

### Hook Files (New ~400 lines)
```
src/frontend/src/hooks/
├── useWorkers.ts                ~ 120 lines (list + search)
├── useWorkerDetail.ts           ~ 100 lines (single worker)
├── useWebSocket.ts              ~ 100 lines (real-time updates)
└── useMetrics.ts                ~ 80 lines (metrics queries)
```

### Test Files (New ~600 lines)
```
tests/frontend/
├── WorkerList.test.tsx          ~ 150 lines
├── WorkerDetail.test.tsx        ~ 150 lines
├── ExecutionTimeline.test.tsx   ~ 100 lines
├── MetricsCard.test.tsx         ~ 100 lines
└── BatchOperations.test.tsx     ~ 100 lines
```

---

## 🧠 Implementation Strategy

### Sequence (Recommended)
1. **t374 first** — Foundation (list, search, filters, pagination)
2. **t375 second** — Detail view (depends on t374, reuses components)
3. **t376 third** — WebSocket (infrastructure layer)
4. **t377 fourth** — Timeline (independent query component)
5. **t378 fifth** — Metrics (independent query component)
6. **t379 last** — Batch UI (optional, builds on t374)

### Tech Stack
- **Framework**: React 18+ with TypeScript
- **State**: React Query (for data fetching + caching)
- **Styling**: Tailwind CSS / styled-components
- **Charts**: Chart.js or D3.js (for metrics visualization)
- **WebSocket**: Socket.io-client or native WebSocket
- **Testing**: Jest + React Testing Library

### Key Patterns

**React Query Hook Pattern**:
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

export const useWorkers = (projectId: number, page: number) => {
  return useQuery({
    queryKey: ['workers', projectId, page],
    queryFn: () => api.getWorkers(projectId, page),
  });
};
```

**WebSocket Connection Pattern**:
```typescript
export const useWorkerUpdates = (projectId: number) => {
  const [updates, setUpdates] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket(`/ws/workers/${projectId}`);
    ws.onmessage = (e) => setUpdates(JSON.parse(e.data));
    return () => ws.close();
  }, [projectId]);
  
  return updates;
};
```

---

## ✅ Acceptance Criteria

### All Todos Must Have:
- [x] All components implemented (no placeholders)
- [x] TypeScript types throughout
- [x] Unit tests for all hooks and components
- [x] E2E tests for main workflows
- [x] Responsive design (mobile + tablet + desktop)
- [x] Error boundary coverage
- [x] Loading/skeleton states
- [x] Real-time updates via WebSocket
- [x] Accessibility (ARIA labels, keyboard nav)
- [x] Dark mode support (if applicable)

### Performance Requirements:
- ✅ List view: <500ms initial load (100 workers)
- ✅ Detail view: <300ms (cached data)
- ✅ WebSocket updates: <100ms latency
- ✅ Charts: <1s render (100+ data points)
- ✅ Search: <200ms with debounce

---

## 🔗 Phase 5D Dependencies (Already Available)

### API Endpoints (Phase 5D)
```
GET    /api/workers
GET    /api/workers/{id}
POST   /api/workers/{id}/start
POST   /api/workers/{id}/pause
POST   /api/workers/{id}/resume
POST   /api/workers/{id}/stop
POST   /api/workers/{id}/retry
GET    /api/workers/{id}/history
GET    /api/workers/{id}/bookmarks
POST   /api/workers/{id}/bookmarks
DELETE /api/workers/{id}/bookmarks/{bid}
GET    /api/workers/{id}/metrics
GET    /api/workers/{id}/audit
GET    /api/workers/summary
GET    /api/health/workers
POST   /api/workers/batch/start
POST   /api/workers/batch/stop
PATCH  /api/workers/batch/update
```

### Data Models (Phase 5D)
```
WorkerResponse {
  id, worker_id, name, description, worker_type,
  current_state, config, project_id, session_id,
  steps_executed, total_duration_ms, start_time, last_activity_at
}

WorkerMetrics {
  worker_id, step_count, success_rate, avg_duration_ms,
  current_state, uptime_ms
}

WorkerSummary {
  project_id, total_workers, running, paused, completed,
  failed, queued, avg_step_count, avg_success_rate
}
```

---

## 📊 Expected Test Matrix

For each component/hook, test:

| Scenario | Expected | Tests |
|----------|----------|-------|
| Render | Component displays | 1 |
| Data loading | Spinner shows, then data | 1 |
| Empty state | Empty message displayed | 1 |
| Error state | Error boundary catches | 1 |
| User interaction | State changes correctly | 1-2 |
| Real-time update | WebSocket message updates UI | 1 |

**Per-todo estimate**: 3-5 components × 5-6 scenarios = 15-30 tests

---

## 🚀 Dispatch Template for Agents

When delegating, use:

```
Implement Phase 5E: Worker Dashboard UI (5-6 todos)

**Todos to implement:**
1. t374: Worker list view + search
2. t375: Worker detail view + actions
3. t376: Real-time WebSocket updates
4. t377: Execution timeline + bookmarks UI
5. t378: Metrics dashboard + charts
6. (Optional) t379: Batch operations UI

**Architecture:**
- React 18+ with TypeScript
- React Query for data fetching
- Socket.io or WebSocket for real-time
- Tailwind CSS for styling
- Jest + React Testing Library for tests

**API Dependencies (from Phase 5D):**
- 22 endpoints covering CRUD, lifecycle, history, metrics, batch

**Performance targets:**
- <500ms list view initial load
- <300ms detail view (cached)
- <100ms WebSocket latency
- <1s chart rendering

**Testing requirements:**
- 70%+ coverage per component
- Unit tests for all hooks
- E2E tests for main workflows
- Accessibility testing (WCAG 2.1 AA)
- Mobile responsiveness (375px, 768px, 1920px viewports)

Ready to proceed?
```

---

## 🔍 SQL Queries (Copy-Paste Ready)

Load Phase 5E todos:
```sql
INSERT INTO todos (id, title, description, status) VALUES
  ('t374', 'Worker list view + search', 'Paginated list, search, filter by state, sort options. ~3h, 20-25 tests.', 'pending'),
  ('t375', 'Worker detail view + actions', 'Detail profile, state transitions, config edit, delete. ~2.5h, 15-20 tests.', 'pending'),
  ('t376', 'Real-time WebSocket updates', 'WebSocket /ws/workers/{id}, auto-reconnect, message batching. ~3h, 15-20 tests.', 'pending'),
  ('t377', 'Execution timeline + bookmarks', 'Timeline visualization, bookmark markers, export. ~2.5h, 10-15 tests.', 'pending'),
  ('t378', 'Metrics dashboard + charts', 'Charts (pie, line), health indicator, audit log. ~2h, 10-15 tests.', 'pending'),
  ('t379', 'Batch operations UI (optional)', 'Multi-select, batch modals, progress bar. ~1.5h, 8-10 tests.', 'pending');

INSERT INTO todo_deps (todo_id, depends_on) VALUES
  ('t375', 't374'),
  ('t377', 't374'),
  ('t378', 't374'),
  ('t379', 't374');
```

Check status:
```sql
SELECT id, title, status FROM todos WHERE id IN ('t374', 't375', 't376', 't377', 't378', 't379') ORDER BY id;
```

---

## 📌 Important Links

**Session Data**:
- Plan: `/home/daen/.copilot/session-state/d1cb85db-c7c8-42e0-bf0c-018029e31bee/plan.md`
- Database: `/home/daen/.copilot/session-state/d1cb85db-c7c8-42e0-bf0c-018029e31bee/session.db`

**Documentation**:
- Phase 5D: `docs/changelog/phase5d_worker_api_changelog.md`
- API Reference: `docs/api/worker-api.md` (if exists)
- Architecture: `docs/architecture/`

**Key Source Files**:
- API Endpoints: `src/api/routes/workers.py` (584 lines)
- Data Models: `src/db/models/worker.py`
- Middleware: `src/ai_proxy/middleware.py`

---

## 🎯 Success Criteria

Phase 5E is **complete** when:
- [x] All 5-6 todos implemented
- [x] 70%+ component test coverage
- [x] All E2E workflows tested
- [x] Real-time updates working
- [x] Mobile responsive (375px+)
- [x] Accessibility verified (WCAG AA)
- [x] All Phase 5A/5B/5C/5D tests still passing
- [x] Performance targets met

**Estimated Total Time**: 12-18 hours (6-8 hours code + 4-6 hours testing + 2-4 hours integration)

---

**Status**: 🚀 Ready to dispatch Phase 5E  
**Next Update**: After Phase 5E completion
