# CyberSecSuite Tests

## Test Organization

### TypeScript/Frontend Tests (This Directory)
All TypeScript and frontend tests are in `tests/frontend/`:

```
tests/frontend/
├── ExecutionTimeline.test.tsx
├── OrchestratorLayout.test.tsx
├── WorkerList.test.tsx
├── *.test.tsx (20+ component tests)
├── test-runner.sh (executor script)
└── README.md (this file)
```

**Run TypeScript tests:**
```bash
# From src/frontend/
npm test

# From anywhere via executor script
./tests/frontend/test-runner.sh

# Run specific test
npm test -- ExecutionTimeline
```

### Python Tests (Backend)
All Python backend and integration tests are in `tests/backend/` and `tests/e2e/`:

```
tests/
├── backend/          ← Unit tests for API
├── e2e/              ← End-to-end integration tests
├── pytest.ini        ← Python test config
└── frontend/         ← TypeScript tests
```

**Run Python tests:**
```bash
pytest
pytest -k "test_worker"  # Specific tests
```

## Test Coverage

| Type | Location | Count |
|------|----------|-------|
| TypeScript Unit | `tests/frontend/` | 25+ |
| Python Unit | `tests/backend/` | 150+ |
| Python E2E | `tests/e2e/` | 50+ |
| **Total** | Mixed | **225+** |

## Running All Tests

```bash
# From project root - run all tests
pytest                              # Python tests
npm -w src/frontend test           # TypeScript tests

# Or sequentially
pytest && npm -w src/frontend test
```

## Test Structure

### Frontend Tests (tests/frontend/)
Organized by component type:
- Orchestrator components (OrchestratorLayout, TemplateBuilder, ConfigManager, etc.)
- Worker components (WorkerList, WorkerDetail, ExecutionTimeline, etc.)
- Hooks (useWebSocket, router, etc.)
- Layout (Sidebar, Breadcrumb, etc.)
- Routes (authProtectedRoutes, etc.)

### Backend Tests
- `tests/backend/` — Unit tests for API endpoints
- `tests/e2e/` — Integration and end-to-end tests

## Configuration

### Vitest Config (src/frontend/vitest.config.ts)
- Discovers tests in `../tests/frontend/**/*.test.tsx`
- Uses jsdom environment
- Includes test globals (describe, it, expect)

### Pytest Config (tests/pytest.ini)
```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Test Execution Flow

```
User runs: npm test
  ↓
Executes: src/frontend/vitest.config.ts
  ↓
Looks in: ../tests/frontend/**/*.test.tsx
  ↓
Runs: 25+ TypeScript tests with vitest
```

Or with executor script:
```
User runs: ./tests/frontend/test-runner.sh
  ↓
Changes to: src/frontend/
  ↓
Executes: npm test
  ↓
Result: Same as above
```

## Quick Reference

```bash
# Run all tests
npm -w src/frontend test

# Run tests with UI
npm -w src/frontend run test:ui

# Run tests in watch mode
npm -w src/frontend test -- --watch

# Run specific test file
npm -w src/frontend test -- ExecutionTimeline

# Run Python tests
pytest -v

# Run Python tests matching pattern
pytest -k "test_worker"
```
