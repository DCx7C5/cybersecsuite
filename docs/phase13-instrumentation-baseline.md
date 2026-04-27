# Phase 13 OTEL Instrumentation Baseline

**Completed:** Phase 13 Priority 3 Weeks 1-2 (Foundation & Depth)  
**Date:** 2026-04-27  
**Status:** Ready for integration testing and observability setup

## Overview

Phase 13 Priority 3 establishes the foundational OTEL instrumentation for CyberSecSuite. All critical service paths now emit metrics and traces to enable observability and performance baseline tracking.

## Instrumentation Coverage

### A2A JSON-RPC Service (`src/a2a/otel.py`)
**Service:** cybersecsuite-a2a  
**Metrics Created:**
- `a2a.jsonrpc.duration` (histogram) — JSON-RPC method execution time
- `a2a.task.send.duration` (histogram) — Task send operation duration
- `a2a.task.get.duration` (histogram) — Task retrieval duration
- `a2a.task.cancel.duration` (histogram) — Task cancellation duration
- `a2a.sse.stream.duration` (histogram) — SSE streaming duration
- Counters for operations and errors

**Baselines (P95):**
- JSON-RPC methods: 500ms
- Task send: 300ms
- Task get: 100ms
- SSE streaming: 100ms

**Implementation:**
- All handlers instrumented with request_id propagation
- Baseline checks log warnings for 15%+ overages
- Spans include method name, request_id, and operation status

---

### MCP Tool Execution (`src/csmcp/otel.py` + instrumented in `src/csmcp/_sdk_compat.py`)
**Service:** cybersecsuite-mcp  
**Metrics Created:**
- `mcp.tool.duration` (histogram) — Tool execution time by name
- `mcp.tool.input_size_bytes` (histogram) — Input payload size
- `mcp.tool.output_size_bytes` (histogram) — Output payload size
- `mcp.tool.invocations` (counter) — Total tool calls
- `mcp.tool.errors` (counter) — Tool execution failures

**Baselines (P95):**
- Tool execution: 2000ms
- External MCP load: 1000ms

**Implementation:**
- Instrumented in `call_tool()` method of SdkMcpServer
- Tracks input/output sizes for cardinality analysis
- Per-tool error tracking

---

### Database Operations (`src/db/otel.py`)
**Service:** cybersecsuite-db  
**Metrics Created:**
- `db.query.duration` (histogram) — Query execution time by operation and table
- `db.transaction.duration` (histogram) — Transaction duration
- `db.query.count` (counter) — Total queries by operation
- `db.query.errors` (counter) — Query failures
- `db.query.slow` (counter) — Queries exceeding 150% of baseline

**Baselines (P95):**
- Query execution: 100ms
- Transactions: 500ms

**Features:**
- SQL normalization for span naming (SELECT, INSERT, UPDATE, DELETE)
- Table name extraction from queries
- Slow query detection and warning logs
- Supports both async and sync queries

---

### Worker State Machine (`src/db/worker_otel.py`)
**Service:** cybersecsuite-worker  
**Metrics Created:**
- `worker.transition.duration` (histogram) — State transition time
- `worker.state.duration` (histogram) — Time in state
- `worker.transition.count` (counter) — Total transitions by from/to state
- `worker.transition.errors` (counter) — Failed transitions
- `worker.pause_resume.count` (counter) — Pause/resume events
- `worker.failure.count` (counter) — Worker failures by reason

**Baselines (P95):**
- Transition to running: 10,000ms (10s average task time)
- Transition to paused: 5,000ms

**States Tracked:**
- `queued` → `running` → `paused` → `completed`|`failed`

---

### Business Metrics (`src/business_metrics.py`)
**Service:** cybersecsuite-business  
**Metrics Created:**
- `business.tokens.prompt` (histogram) — Prompt tokens by model
- `business.tokens.completion` (histogram) — Completion tokens by model
- `business.tokens.total` (counter) — Total tokens
- `business.cost.api` (counter) — API costs in USD
- `business.cache.savings` (counter) — Cache hit savings in USD
- `business.cache.hits|misses|evictions` (counters)
- `business.tool.invocations|latency|errors` (counter/histogram by tool)
- `business.threat_intel.lookups|cache_hits` (counters)
- `business.findings.created|updated|archived` (counters)
- `business.cases.created|completed|duration` (counter/histogram)
- `business.workers.active|completed|failed|duration` (counter/histogram)

**Record Functions:**
```python
from business_metrics import (
    record_token_usage,
    record_api_cost,
    record_cache_hit,
    record_tool_invocation,
    record_finding_created,
    record_case_completed,
    record_worker_completed,
)

# Usage examples
record_token_usage(TokenUsage(prompt_tokens=100, completion_tokens=50), model="claude-3")
record_api_cost(0.50, api_name="anthropic")
record_cache_hit(cache_name="response_cache", saved_usd=0.10)
record_tool_invocation("vault_search", latency_ms=250.5, success=True)
```

---

### Context Propagation (`src/propagation.py`)
**Service:** cybersecsuite-propagation  
**Features:**
- Trace context extraction from HTTP headers (Jaeger, B3, W3C formats)
- Request ID generation and correlation across services
- Header injection for downstream service calls
- Async/sync boundary preservation

**API:**
```python
from propagation import (
    extract_trace_context_from_request,
    create_trace_headers,
    TraceContextManager,
)

# In FastAPI endpoint
@app.post("/api/tasks")
async def create_task(request: Request):
    trace_ctx = extract_trace_context_from_request(request)
    request_id = trace_ctx.get("request_id")
    
    # Call downstream service with trace headers
    headers = create_trace_headers(request_id=request_id)
    response = await httpx.post(
        "http://worker-service/execute",
        headers=headers,
        json=task_data
    )
```

---

## Testing & Validation

### Unit Test Coverage
- ✅ A2A unit tests: 23/23 passing
- ✅ MCP features: 3/3 passing
- ✅ All OTEL modules import successfully with graceful degradation

### Collection Status
- **Total tests collectible:** 766
- **Collection errors:** 0
- **Pass rate:** 494/766 (64% baseline)

### Known Test Issues (Not OTEL scope)
- 167 worker tests setup errors (worker fixture model graph issue)
- 24 integration tests skipped (MCP startup environment-dependent)
- Pre-existing failures not related to OTEL instrumentation

---

## Integration Checklist

**Phase 13 Priority 3 Week 1-2 Complete ✅**

- [x] A2A JSON-RPC dispatcher instrumentation
- [x] MCP tool execution instrumentation
- [x] Database query instrumentation
- [x] Worker state machine instrumentation
- [x] Business metrics collection framework
- [x] Context propagation implementation
- [x] All modules import successfully

**Phase 13 Priority 3 Week 3 (To Do)**

- [ ] OpenObserve connection and metric export verification (p13-otel-integration)
- [ ] Performance regression testing with observed baselines (p13-regression-tests)
- [ ] OpenObserve dashboards for each service (p13-dashboards)
- [ ] Final documentation and baseline capture (p13-final-docs)

---

## Performance Baseline Reference

### Service Latency Targets (P95)

| Service | Operation | Baseline | 15% Threshold |
|---------|-----------|----------|----------------|
| A2A | JSON-RPC method | 500ms | 575ms |
| A2A | Task send | 300ms | 345ms |
| A2A | Task get | 100ms | 115ms |
| A2A | SSE stream | 100ms | 115ms |
| MCP | Tool execution | 2000ms | 2300ms |
| MCP | External MCP load | 1000ms | 1150ms |
| DB | Query execution | 100ms | 115ms |
| DB | Transaction | 500ms | 575ms |
| Worker | Transition to running | 10000ms | 11500ms |
| Worker | Transition to paused | 5000ms | 5750ms |

### Token Metrics

| Metric | Unit | Tracked By |
|--------|------|-----------|
| Prompt tokens | 1 | business_metrics.record_token_usage() |
| Completion tokens | 1 | business_metrics.record_token_usage() |
| Total tokens | 1 | auto-calculated |

### Cost Metrics

| Metric | Unit | Source |
|--------|------|--------|
| API costs | USD | business_metrics.record_api_cost() |
| Cache savings | USD | business_metrics.record_cache_hit(saved_usd=...) |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CyberSecSuite v0.1                          │
└─────────────────────────────────────────────────────────────────┘
    │                    │                    │
    ├── A2A Service ─────┼── MCP Service ────┼── DB Service
    │  (otel.py)         │  (otel.py)        │  (otel.py)
    │  ├─ JSONRPC        │  ├─ Tools         │  ├─ Queries
    │  ├─ Tasks          │  ├─ Invocation    │  ├─ Transactions
    │  └─ SSE            │  └─ I/O Size      │  └─ Slow Queries
    │                    │                    │
    └────────────────────┴────────────────────┴──────────────────┐
                                                                 │
                    ┌─────────────────────────────────────┐      │
                    │     OTEL Collector / OpenObserve    │◄─────┘
                    │                                     │
                    ├─ Metrics (Prometheus)              │
                    ├─ Traces (Jaeger)                   │
                    └─ Logs (Loki)                       │
                                                         │
                    ┌─ Dashboards                        │
                    │  ├─ Service health                 │
                    │  ├─ Latency tracking               │
                    │  ├─ Token usage                    │
                    │  └─ Cost analysis                  │
```

---

## Next Steps

1. **Integration Testing (p13-otel-integration)**
   - Verify OpenObserve connection and metric export
   - Validate trace context propagation end-to-end
   - Test graceful degradation when collector unavailable

2. **Performance Baselines (p13-regression-tests)**
   - Run load tests with existing baselines
   - Record actual P50/P95/P99 latencies
   - Identify any regressions from Phase 12

3. **Dashboards (p13-dashboards)**
   - Create service health dashboards
   - Add latency tracking visualizations
   - Build token/cost analysis views

4. **Documentation (p13-final-docs)**
   - Document integration points for new instrumentation
   - Create troubleshooting guide for common metrics
   - Plan for Phase 14 production hardening

---

## Reference

**Files Created:**
- `src/a2a/otel.py` — A2A JSON-RPC instrumentation
- `src/csmcp/otel.py` — MCP tool instrumentation
- `src/db/otel.py` — Database query instrumentation
- `src/db/worker_otel.py` — Worker state machine instrumentation
- `src/business_metrics.py` — Business metrics collection
- `src/propagation.py` — Context propagation

**Files Modified:**
- `src/a2a/server.py` — Added instrumentation to all handlers
- `src/csmcp/_sdk_compat.py` — Added instrumentation to `call_tool()`
- `pyproject.toml` — Removed incorrect tortoise dependency

**Git Commits:**
- `72ec76ab` — A2A dispatcher and MCP tool OTEL instrumentation
- `6f3bca0f` — Complete OTEL foundation (DB, worker, business, propagation)

---

**Phase 13 Status:** 🟢 Ready for Week 3 integration testing

