# Phase 13 Roadmap — CyberSecSuite v0.1

**Status:** Planning Complete (Phase 12 Session 1)  
**Duration:** 4 weeks (estimated)  
**Focus:** Cleanup Validation → OTEL Instrumentation → Performance Baseline

---

## Phase 13 Overview

Phase 13 completes the cleanup initiated in Phase 12 and establishes OpenTelemetry instrumentation foundation across the system. The phase produces comprehensive observability baseline metrics and prepares for Phase 14 production hardening.

---

## Priority 1: Phase 12 Cleanup Validation (Days 1-2)

### Objectives
- Validate test suite with Phase 12 cleanup consequences
- Restore or stub deleted Bootstrap components
- Update integration tests for new reality

### Tasks
1. **Restore/Stub BOOTSTRAP.md**
   - Location: `docs/BOOTSTRAP.md`
   - Options:
     - Option A: Restore from git history (5 KB, historical)
     - Option B: Create new bootstrap guide for Phase 13+ (recommended)
   - Impact: 8 integration tests depend on this

2. **Restore/Stub Bootstrap Script**
   - Location: `scripts/install-mcp-core.sh`
   - Options:
     - Option A: Restore existing script (historical bootstrap)
     - Option B: Replace with Python bootstrap (src/startup/first_run.py)
   - Impact: 3 integration tests depend on this

3. **Update Integration Tests**
   - Mark tests as conditional on deleted components
   - Or restore minimal stubs
   - Target: All tests passing

### Success Criteria
- ✅ All integration tests passing or properly marked as legacy
- ✅ Bootstrap components identified/restored/stubbed
- ✅ Test suite reports ≥95% pass rate

---

## Priority 2: Documentation Tier 2-3 (Days 3-4)

### Tier 2 — IMPORTANT (40 minutes)
1. **Create `/docs/api/workers.md`**
   - Document all 21 worker routes
   - Breakdown: 5 CRUD + 5 lifecycle + 4 history + 4 metrics + 3 batch
   - Include request/response examples
   - Add state transition diagrams

2. **Integrate Deprecation Audit Findings**
   - Link to `docs/architecture/deprecation-status.md`
   - Update main architecture docs

### Tier 3 — QUALITY (30 minutes)
3. **Update `/docs/bootstrap.md`**
   - Document new worker API availability
   - Add Phase 13 bootstrap notes

4. **Create `/docs/testing-roadmap.md`**
   - Phase 12 coverage targets
   - Phase 13 test objectives
   - Phase 14 coverage goals

### Success Criteria
- ✅ All API routes documented with examples
- ✅ Bootstrap process current
- ✅ Testing roadmap clear for Phase 14

---

## Priority 3: OTEL Instrumentation — Foundation (Week 1)

### Objectives
- Establish tracing in A2A and MCP layers
- Set baseline latency metrics
- Enable distributed tracing across system

### Tasks

#### 3.1 A2A Instrumentation (`src/a2a/otel.py`)
```python
# Create tracer for A2A JSON-RPC server
- Service name: cybersecsuite-a2a
- Spans:
  - jsonrpc.{method} (for each JSON-RPC method)
  - tasks.send, tasks.get, tasks.cancel
  - sse.stream (SSE events)
- Attributes:
  - request_id, task_id, method
  - worktree.sid (session ID)
  - status, latency_ms
```

#### 3.2 MCP Instrumentation (`src/csmcp/otel.py`)
```python
# Create tracer for MCP tool execution
- Service name: cybersecsuite-mcp
- Spans:
  - mcp.tool.{tool_name} (tool execution)
  - mcp.load_external (external MCP loading)
- Attributes:
  - tool_name, input_size, result
  - status, error (if any)
  - latency_ms
```

#### 3.3 A2A JSON-RPC Dispatcher
- Instrument `src/a2a/server.py::_jsonrpc()`
- Add span wrapping around method dispatch
- Capture method, request_id, status
- Track latency and errors

#### 3.4 MCP Tool Execution
- Instrument tool dispatcher
- Track execution time per tool
- Capture input size, output size
- Record errors with exception type

### Baseline Metrics (Week 1 End)
| Metric             | Target   | Alert Threshold |
|--------------------|----------|-----------------|
| A2A JSON-RPC P95   | < 500ms  | > 575ms         |
| MCP tool P95       | < 2000ms | > 2300ms        |
| SSE stream latency | < 100ms  | > 115ms         |

### Success Criteria
- ✅ A2A tracer operational
- ✅ MCP tracer operational
- ✅ All critical spans traced
- ✅ Baseline P50/P95/P99 recorded

---

## Priority 4: OTEL Instrumentation — Depth (Week 2)

### Objectives
- Complete instrumentation across all layers
- Establish business metrics
- Enable context propagation

### Tasks

#### 4.1 Database Query Instrumentation
```python
# Create src/db/otel.py
- Hook into Tortoise ORM query lifecycle
- Spans per query: table, operation, latency
- Attributes: row_count, status, error
- Cardinality control for table names
```

#### 4.2 Worker State Machine Tracing
```python
# Instrument src/a2a/agent.py state transitions
- Span per transition: queued→running, running→paused, etc.
- Attributes: worker_id, from_state, to_state, timestamp
- Track state duration
```

#### 4.3 Business Metrics (Meters)
```python
# Create meters for:
- llm.tokens.usage (counter) - by model, token_type
- llm.cost_usd (counter) - by model, provider
- cache.hit_rate (gauge) - percentage
- tool.execution_ms (histogram) - by tool_name
```

#### 4.4 Context Propagation
- Ensure worktree.sid propagates through all spans
- Trace ID correlation across layers
- Parent-child span relationships

### Baseline Metrics (Week 2 End)
| Metric                | Target  |
|-----------------------|---------|
| DB query P95          | < 100ms |
| Worker transition P95 | < 50ms  |
| Token usage tracking  | Enabled |
| Cost tracking         | Enabled |

### Success Criteria
- ✅ Database queries traced
- ✅ Worker state machine traced
- ✅ Business metrics captured
- ✅ Context propagates correctly
- ✅ All baseline metrics recorded

---

## Priority 5: Performance & Integration (Weeks 3-4)

### Week 3: Integration & Validation
1. **OpenObserve Integration**
   - Verify all traces reach OpenObserve
   - Confirm stream creation (cybersecsuite-a2a, cybersecsuite-mcp, cybersecsuite-db)
   - Validate cardinality controls

2. **Sampling Strategy**
   - Establish 100% sampling during Phase 13 (production testing)
   - Plan for reduced sampling in Phase 14
   - Document sampling decisions

3. **Dashboard & Alerts**
   - Create OpenObserve dashboards for key metrics
   - Set up alerts for regression thresholds
   - Test alert notifications

### Week 4: Testing & Planning
1. **Regression Testing**
   - Performance tests with tracing enabled
   - Validate baselines hold
   - Measure instrumentation overhead

2. **Documentation**
   - Create `docs/phase13-instrumentation-baseline.md`
   - Document OTEL sampling strategy
   - Provide debugging guide (enable trace logging)

3. **Phase 14 Planning**
   - Analyze baseline metrics
   - Identify optimization opportunities
   - Draft Phase 14 performance roadmap

### Success Criteria
- ✅ OTEL fully integrated with OpenObserve
- ✅ Baseline metrics stable and recorded
- ✅ Regression thresholds established
- ✅ Phase 14 planning complete
- ✅ Team ready for production deployment

---

## Timeline

| Phase                  | Week         | Key Milestones                        |
|------------------------|--------------|---------------------------------------|
| Cleanup Validation     | 0 (Days 1-2) | Bootstrap restored, tests passing     |
| Docs & Planning        | 0 (Days 3-4) | API reference complete, roadmap ready |
| OTEL Foundation        | 1            | A2A/MCP tracing live, baseline P95s   |
| OTEL Depth             | 2            | DB/worker tracing, business metrics   |
| Performance & Phase 14 | 3-4          | Baselines stable, Phase 14 drafted    |

---

## Success Criteria

- ✅ All Phase 12 cleanup impacts validated/resolved
- ✅ Documentation complete and current
- ✅ OTEL instrumentation foundation operational
- ✅ Baseline metrics (A2A, MCP, DB) P50/P95/P99 recorded
- ✅ Phase 14 roadmap drafted and prioritized
- ✅ System ready for production observability

---

## Phase 14 Preview

- Performance optimization (based on Phase 13 baselines)
- Advanced observability (custom metrics, alerts)
- Production hardening and security audit
- Scale testing and load optimization

---

**Created:** 2026-04-27  
**Status:** Ready for Phase 13 execution  
**See:** `briefing.md` for Phase 12 summary
