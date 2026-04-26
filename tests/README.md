# CyberSecSuite Tests

## Test Organization

### TypeScript/Frontend Tests
**Location**: `src/frontend/tests/`

All TypeScript tests are now colocated in the frontend package:

```
src/frontend/tests/
├── *.test.tsx (25 component & hook tests)
├── fixtures.ts (Playwright test fixtures)
├── e2e/
│   ├── *.spec.ts (4 e2e tests - includes planMode.e2e.ts)
│   └── ...
└── ...
```

**Run TypeScript tests:**
```bash
# From src/frontend/
npm test

# With UI
npm run test:ui

# Watch mode
npm test -- --watch
```

### Python Tests (Backend)
Backend tests remain in `tests/`:

```
tests/
├── backend/          ← Unit tests for API
├── integration/      ← Integration tests
└── pytest.ini        ← Python test config
```

**Run Python tests:**
```bash
pytest
pytest -k "test_worker"  # Specific tests
```

## Test Coverage

| Type | Location | Count |
|------|----------|-------|
| TypeScript Unit | `src/frontend/tests/` | 25 |
| TypeScript E2E | `src/frontend/tests/e2e/` | 4 |
| Python Unit | `tests/backend/` | 150+ |
| Python Integration | `tests/integration/` | 50+ |
| **Total** | Mixed | **229+** |

## Running All Tests

```bash
# From src/frontend/ - run TypeScript tests
npm test

# From project root - run Python tests
pytest

# Run both sequentially
npm test -w src/frontend && pytest
```

## Test Structure

### Frontend Tests (src/frontend/tests/)
- Component tests (Worker*, Orchestrator*, etc.)
- Hook tests (useWebSocket, router, etc.)
- Layout tests (Sidebar, Breadcrumb, etc.)
- Route tests (authProtectedRoutes, etc.)
- E2E tests (planMode, response-window, worker-context, tier-routing)
- Fixtures (Playwright test fixtures for E2E tests)

### Backend Tests (tests/)
- `backend/` — Unit tests for API endpoints
- `integration/` — Integration and backend-specific tests

## Configuration

### Vitest Config (src/frontend/vitest.config.ts)
```typescript
test: {
  include: ['tests/**/*.test.{ts,tsx}', 'tests/**/*.spec.ts'],
}
```
- Discovers tests in `src/frontend/tests/`
- Uses jsdom environment for React components
- Includes test globals (describe, it, expect)

### Pytest Config (tests/pytest.ini)
```ini
[pytest]
testpaths = .
python_files = test_*.py
```

## Test Execution Flow

```
User runs: npm test (from src/frontend/)
  ↓
Loads: vitest.config.ts
  ↓
Discovers: tests/**/*.test.{ts,tsx}
  ↓
Runs: All tests in src/frontend/tests/
  ↓
Result: TypeScript tests executed
```

## Quick Reference

```bash
# TypeScript tests
npm -w src/frontend test              # Run all
npm -w src/frontend test -- --watch   # Watch mode
npm -w src/frontend run test:ui       # UI mode
npm -w src/frontend test -- ExecutionTimeline  # Single file

# Python tests
pytest                     # Run all
pytest -v                  # Verbose
pytest -k "pattern"        # Pattern matching
pytest --collect-only      # List tests

# Both
npm test -w src/frontend && pytest
```

## Test File Organization

```
src/frontend/tests/
├── ExecutionTimeline.test.tsx
├── OrchestratorLayout.test.tsx
├── WorkerList.test.tsx
├── WorkerDetail.test.tsx
├── MetricsCard.test.tsx
├── BatchOperations.test.tsx
├── TemplateBuilder.test.tsx
├── ConfigManager.test.tsx
├── NotificationCenter.test.tsx
├── BatchScheduler.test.tsx
├── HealthDashboard.test.tsx
├── UserSettings.test.tsx
├── AnalyticsDashboard.test.tsx
├── Sidebar.test.tsx
├── Breadcrumb.test.tsx
├── authProtectedRoutes.test.tsx
├── router.test.tsx
├── useWebSocket.test.tsx
├── useWebSocket.test.tsx
├── useLocation.test.ts
├── useKeyboardShortcuts.test.ts
├── commandEngine.test.ts
├── mentionValidation.test.ts
├── sidebarPersist.test.ts
├── useHideElement.test.ts
├── useMenuInput.test.ts
├── fixtures.ts
└── e2e/
    ├── planMode.e2e.ts
    ├── response-window.spec.ts
    ├── worker-context.spec.ts
    └── tier-routing.spec.ts
```
