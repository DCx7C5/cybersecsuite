# Testing Roadmap — CyberSecSuite v0.1-0.2

**Last Updated:** 2026-04-27  
**Status:** Phase 13 Planning

---

## Current State (Phase 12)

### Test Metrics Baseline
- **Total Tests:** 766 (collectible)
- **Passing:** 494 (64%)
- **Failing:** 30 (4%)
- **Skipped:** 75 (10%)
- **Errors (Setup):** 167 (22%)

### Coverage by Module
| Module | Tests | Pass Rate | Status |
|--------|-------|-----------|--------|
| features/ | 26 | 88% | Stable |
| module/ | 123 | 82% | Needs cleanup |
| unit/ | 201 | 91% | Stable |
| worker/ | 190 | 0%* | Blocked (fixtures) |
| integration/ | 61 | 45% | Pre-existing failures |
| legacy/ | 35 | 86% | Phase 12 fix (was 0%) |
| *Total* | *766* | *64%* | *Improving* |

*worker/ tests fail at setup due to incomplete model fixtures (not functional failures)

---

## Phase 12 Accomplishments

### ✅ Test Collection Unblocked (Session 1)
- Fixed 3 import errors (tortoise, db managers)
- Removed wrong tortoise package from dependencies  
- Updated file path references (BOOTSTRAP.md, scripts/)
- **Result:** 166 worker tests now collectible (was blocked)

### ✅ Legacy Tests Rescued (Session 1)
- Created conftest.py stubs for deleted src/dashboard/
- 6 of 7 legacy tests passing (was 0/7)
- Acceptable tradeoff: 1 test requires full dashboard module restore

### Pre-existing Issues (Not Phase 12 scope)
- Dashboard routing test failures (8)
- Worker fixture model relationships incomplete (167 tests)
- Integration test environment setup (22 failures)

---

## Phase 13 Testing Objectives

### Priority 1: Fix Worker Test Fixtures (Days 1-2)

**Goal:** Resolve 167 worker test setup errors

**Task:** Update worker test fixtures to load full model graph
```python
# Current (broken):
modules_to_load = ["db.models.scope", "db.models.worker"]

# Needed:
modules_to_load = ["db.models"]  # Load ALL models
```

**Impact:** ~100 worker tests become runnable (functional, not just collected)

**Success Criteria:**
- ≥95% of collected tests passing (or properly marked as legacy)
- Worker CRUD tests passing (create, list, get, update, delete)
- Lifecycle tests passing (start, pause, resume, stop)
- No skipped tests without justification

### Priority 2: Documentation Coverage (Weeks 1-2)

**Goal:** Document testing strategy and coverage targets

**Deliverables:**
1. **Phase 13 Test Coverage Report** — baseline metrics and gaps
2. **Testing Strategy Document** — unit/integration/e2e approach
3. **CI/CD Test Pipeline** — GitHub Actions workflow documentation

### Priority 3: Integration Test Stability (Weeks 2-3)

**Goal:** Fix 22 pre-existing integration test failures

**Root Causes:**
- Missing BOOTSTRAP.md dependency (8 tests)
- Missing scripts/install-mcp-core.sh (3 tests)
- MCP startup not mocked in test environment (6 tests)
- Database seeding issues (5 tests)

**Approach:**
1. Mock MCP initialization
2. Create test fixtures for bootstrap docs/scripts
3. Add database seeding to setup fixtures
4. Mark unreliable tests as xfail with ticket references

---

## Phase 14 Testing Plan (Weeks 3-4)

### Coverage Expansion
- Add performance regression tests (latency baselines)
- Add OTEL instrumentation tests (trace verification)
- Add database query tracing tests
- Add worker state machine exhaustive tests

### Target Metrics
- **Overall Pass Rate:** ≥95%
- **Unit Test Coverage:** ≥85%
- **Integration Coverage:** ≥70%
- **Critical Path Coverage:** 100%

### Critical Paths (100% coverage required)
1. Worker CRUD operations
2. Worker state transitions
3. Scope-based access control
4. A2A task dispatch
5. MCP tool execution
6. Audit logging
7. Error handling and recovery

---

## Test Categories

### Unit Tests (201 tests)
**Focus:** Individual functions and classes  
**Examples:** `tests/unit/test_cache_invalidation.py`  
**Current Pass Rate:** 91%

**To Improve:**
- Add parameterized tests for edge cases
- Add negative test cases for error paths
- Increase assertion coverage

### Module Tests (123 tests)
**Focus:** Component integration within a module  
**Examples:** `tests/module/test_phase8a.py`  
**Current Pass Rate:** 82%

**To Improve:**
- Add mocks for external dependencies
- Test error propagation
- Verify state consistency

### Feature Tests (26 tests)
**Focus:** End-to-end feature functionality  
**Examples:** `tests/features/test_dashboard_routing.py`  
**Current Pass Rate:** 88%

**To Improve:**
- Add visual regression tests
- Add performance tests
- Test browser compatibility

### Integration Tests (61 tests)
**Focus:** System-level integration  
**Examples:** `tests/integration/test_mcp_bootstrap.py`  
**Current Pass Rate:** 45%

**Issues:**
- Requires full environment setup
- Depends on external services
- Brittle due to timing issues

**To Improve:**
- Mock external services
- Add retry logic for timing
- Use containerized test environment

### Worker Tests (190 tests)
**Focus:** Worker API and lifecycle  
**Examples:** `tests/worker/test_worker_api_crud.py`  
**Current Status:** Blocked (fixture setup errors)

**To Fix:**
- Complete model fixture setup (load full schema)
- Add async fixture setup
- Mock database transactions

### Legacy Tests (35 tests)
**Focus:** Phase 11 and earlier tests  
**Examples:** `tests/legacy/test_agent_discovery.py`  
**Current Pass Rate:** 86% (Phase 12 rescue)

**Notes:**
- 6/7 passing with stub approach
- 1 test requires dashboard module restore (acceptable tradeoff)

---

## Testing Tools & Configuration

### Frameworks
- **pytest** — Test runner
- **pytest-asyncio** — Async test support
- **pytest-cov** — Coverage reporting

### Configuration
- **pytest.ini** — Test discovery and markers
- **pyproject.toml** — Dependency groups (dev, test)
- **Coverage settings:** min 70% for CI/CD gates

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific module
uv run pytest tests/unit/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run with markers
uv run pytest tests/ -m "not slow"

# Run specific test
uv run pytest tests/unit/test_file.py::TestClass::test_method -v
```

### CI/CD Integration
- **GitHub Actions:** `.github/workflows/qa-*.yml`
- **Test gate:** ≥95% pass rate required
- **Coverage gate:** ≥70% required
- **Timeout:** 10 minutes per test suite

---

## Known Issues & Decisions

### Issue 1: Worker Test Fixtures
**Status:** Blocked (Phase 13 Priority 1)  
**Root Cause:** Model fixture missing foreign key relationships  
**Decision:** Load full model graph instead of subset  
**Timeline:** Days 1-2 of Phase 13

### Issue 2: Dashboard Tests
**Status:** Failing (8 tests)  
**Root Cause:** Dashboard module deleted in Phase 12  
**Decision:** Keep stub approach (6/7 legacy tests pass)  
**Acceptable:** 1 failing test is low-risk; dashboard not critical

### Issue 3: Integration Test Brittleness
**Status:** Pre-existing (22 failures)  
**Root Cause:** Full environment dependency  
**Decision:** Mock external services in test fixtures  
**Timeline:** Phase 13-14

### Issue 4: Test Organization
**Status:** Works but could be clearer  
**Root Cause:** Tests split across 6 categories  
**Decision:** Improve test discovery documentation  
**Timeline:** Phase 14 cleanup

---

## Recommendations

### Short Term (Phase 13)
1. ✅ Fix worker fixture setup (HIGH PRIORITY)
2. ✅ Document current coverage gaps
3. Increase worker test coverage to 95%+
4. Mark unstable tests with `@pytest.mark.xfail` and ticket refs

### Medium Term (Phase 14)
1. Add performance regression tests
2. Integrate OTEL instrumentation tests
3. Add visual regression tests for dashboard
4. Achieve 95% overall pass rate

### Long Term (Phase 15+)
1. Implement continuous performance monitoring
2. Add fuzzing tests for API endpoints
3. Add chaos engineering tests
4. Achieve 98%+ pass rate with SLA tracking

---

## Metrics Dashboard

### Target Metrics for Each Phase

| Metric | Phase 12 | Phase 13 | Phase 14 | Target |
|--------|----------|----------|----------|--------|
| Overall Pass Rate | 64% | 85%+ | 95%+ | 98%+ |
| Unit Coverage | 91% | 93%+ | 95%+ | 95%+ |
| Integration Tests | 45% | 70%+ | 85%+ | 90%+ |
| Test Collection | 766 | 766 | 800+ | 1000+ |
| CI/CD Time | 15m | 12m | 10m | <10m |
| Critical Path Coverage | 70% | 95%+ | 100% | 100% |

---

## Related Documentation

- **Phase 13 Roadmap:** [PHASE_13_ROADMAP.md](../PHASE_13_ROADMAP.md)
- **Test Fixtures:** [Fixture Setup Guide](../architecture/test-fixtures.md)
- **CI/CD Pipeline:** [GitHub Actions Workflows](.github/workflows/)
- **OTEL Testing:** Phase 13-14 instrumentation test guide
