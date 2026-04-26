# CyberSecSuite Tests

## Test Organization

### Python Tests (This Directory)
All Python backend tests are located in this directory:
- `backend/` — Backend API unit tests
- `integration/` — Integration tests
- `e2e/` — End-to-end tests
- `fixtures/` — Test fixtures and mocks

**Run Python tests:**
```bash
pytest
```

### TypeScript/Frontend Tests (Colocated)
Frontend tests are colocated with their components in `src/frontend/src/`:

```
src/frontend/src/
├── components/
│   ├── workers/
│   │   ├── WorkerList.tsx
│   │   └── WorkerList.test.tsx      ← Test next to component
│   └── orchestrator/
│       ├── OrchestratorLayout.tsx
│       └── OrchestratorLayout.test.tsx
└── hooks/
    ├── useWebSocket.ts
    └── useWebSocket.test.ts
```

**Run TypeScript tests:**
```bash
# From src/frontend/
npm test

# Or via test runner from tests/frontend/
./tests/frontend/test-runner.sh
```

## Test Coverage

| Type | Location | Count |
|------|----------|-------|
| Python Unit | `tests/` | ~150+ |
| Python E2E | `tests/e2e/` | ~50+ |
| TypeScript Unit | `src/frontend/src/**/*.test.tsx` | 16 |
| **Total** | Mixed | **216+** |

## Running All Tests

```bash
# Python tests
cd /home/daen/Projects/cybersecsuite
pytest

# TypeScript tests
cd /home/daen/Projects/cybersecsuite/src/frontend
npm test
```
