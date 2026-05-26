# @otel — OpenTelemetry Observability

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document owns the executable telemetry and observability specification.

---

**Location**: `src/css/core/otel/`

**Responsibility**: Observability instrumentation (tracing, metrics, logs), OpenTelemetry SDK integration.

---

## Overview

OpenTelemetry (OTel) standardizes observability across distributed systems.

**Primary platform integration**:
- OpenObserve for append-heavy traces, telemetry, audit/log streams, and dashboard queries
- OTel instrumentation and context propagation feeding that data plane
- PostgreSQL only for mutable relational application state or explicitly retained aggregate metadata

---

## Implementation Status

🟡 **PARTIAL CONFIG SURFACE** — `config.py` and package exports exist; collector/export/stream/dashboard implementation remains pending.

---

## Architecture (Planned)

### Core Files

- `src/css/core/otel/__init__.py` — current exports for configuration
- `src/css/core/otel/config.py` — current `OTelConfig`, `get_otel_config()`
- `src/css/core/otel/collector.py` — planned `TelemetryCollector`
- `src/css/core/otel/openobserve.py` — planned OpenObserve client/flush queue
- `src/css/core/otel/streams.py` — planned stream definitions and retention
- `src/css/core/otel/dashboard.py` — planned dashboard query/aggregate service

### Feature Set (Planned)

1. **Distributed Tracing**
   - Request tracing across modules
   - Span creation for key operations
   - OpenObserve-compatible trace export and correlation

2. **Metrics**
   - HTTP request metrics
   - Database query metrics
   - Custom business metrics
   - OpenObserve/dashboard consumption

3. **Structured Logging**
   - JSON log formatting
   - Context propagation
   - OpenObserve stream correlation with traces

---

## Dependencies

- `opentelemetry-api` — OTel API
- `opentelemetry-sdk` — OTel SDK
- OpenObserve-compatible OTel/export API dependency selected during implementation; do not introduce a Jaeger storage path by default
- `opentelemetry-instrumentation-fastapi` — FastAPI auto-instrumentation
- Tortoise-compatible DB instrumentation selected after verifying current ORM hooks; do not assume SQLAlchemy

---

## Integration Plan

### Phase 1: Setup
- Initialize OTel SDK in app.py lifespan
- Configure exporter/collector path for OpenObserve
- Setup logging handler

### Phase 2: FastAPI Integration
- Auto-instrument FastAPI middleware
- Trace HTTP requests

### Phase 3: Database Integration
- Auto-instrument Tortoise ORM queries
- Trace database operations

### Phase 4: Custom Instrumentation
- Add custom spans for critical paths
- Export business metrics

---

## Phase 35 - Telemetry Infrastructure

Phase 35 turns SDK setup into the platform telemetry data plane. Its
OpenObserve client and queue are shared dependencies for SIEM, operational
graphs, event audit, provider usage accounting, and frontend dashboards.

| Todo ID | Status | Required result |
|---------|--------|-----------------|
| `telemetry-schema` | pending | Required PostgreSQL relational telemetry metadata, if retained after OpenObserve ownership is confirmed. |
| `telemetry-timescaledb` | pending | Validate whether TimescaleDB is still required for aggregates; do not duplicate OpenObserve storage without justification. |
| `db-oo-client-implementation` | pending | Async OpenObserve ingest/query client with a bounded queue and graceful lifespan flushing. |
| `db-oo-stream-definitions` | pending | Idempotent stream schema and retention configuration. |
| `telemetry-collector` | pending | Implement `TelemetryCollector` in `src/css/core/otel/collector.py`, not a new `core/telemetry` package. |
| `telemetry-dashboard` | pending | Dashboard query/aggregate contract consumed by frontend and graph services. |
| `telemetry-filesystem-md` | pending | Update architecture references to the retained `core/otel` ownership after implementation is verified. |

### Stream Contract

| Stream | Suggested retention | Producers/consumers |
|--------|---------------------|---------------------|
| `audit_logs` | 365 days | ORM/action audit and approval decisions. |
| `api_usage_log`, `llm_calls` | 90 days | Proxy/SDK usage, cost, latency; dashboards and graph services. |
| `agent_runs` | 60 days | Orchestrator/task diagnostics. |
| `chat_turns`, `events_stream`, `tool_executions` | 30 days | Chat/events/tools observability. |
| `intel_update_log` | 180 days | Threat-intel ingestion jobs. |

### Lifespan and Storage Boundaries

1. Start the OpenObserve client/flush queue in ASGI lifespan and drain it on shutdown.
2. Emit telemetry asynchronously; analytics write failure must not become an
   application-state transaction failure.
3. Keep sessions, permissions, settings, marketplace, report state, and
   canonical memory entries in PostgreSQL; OpenObserve is append/query
   telemetry, not the mutable application database.
4. Feed Phase 27 graph telemetry and Phase 37 SIEM processing through these
   stream definitions rather than creating parallel storage flows.

---

### Numbered Execution And Validation

1. Retain `OTelConfig` in `src/css/core/otel/config.py`, then implement
   `openobserve.py` and `streams.py` for bounded async OpenObserve delivery.
2. Implement `collector.py::TelemetryCollector` as the single producer-facing
   enqueue/flush context, consumed by events, SDK usage, graphs, and SIEM.
3. Decide whether PostgreSQL/Timescale metadata is justified only after the
   OpenObserve query/dashboard contract is measured; do not duplicate append
   data by assumption.
4. Validate correlation/redaction, queue backpressure, failed-export
   isolation, shutdown drain, stream idempotency/retention, dashboard query
   behavior, and absence of new `src/css/core/telemetry/` ownership.

## Historical Audit Results (2026-05-03)

**Agent 2 Core Infrastructure Audit**

### 5-File Pattern Compliance
This snapshot predates the current `config.py` surface and is retained only as
historical context; use the current file/contract sections above.

| File | Status |
|------|--------|
| `__init__.py` | ❌ Missing |
| `config.py` | ❌ Missing |
| `tracing.py` | ❌ Missing |
| `metrics.py` | ❌ Missing |
| `logging.py` | ❌ Missing |

**Runtime total**: 0 implementation files -> Not started

### Integration Status
- ⚠️ No reverse dependencies yet (will integrate with asgi, db)
- ⏳ Planned integrations: 2 (asgi, db)
- ⏳ 0 integration points active

### Implementation Status
- ❌ No OTel SDK setup
- ❌ No tracing configured
- ❌ No metrics collectors
- ❌ No structured logging
- ❌ No exporters configured

### Readiness Assessment
🔴 **NOT READY** — Phase 2 work; no blocking dependencies but deferred to Phase 3+

### Recommendations
1. **Priority**: Medium (observability, not critical path)
2. **Effort**: 8-12 hours for full implementation
3. **Dependencies**: opentelemetry-* packages (add to requirements.txt)
4. **Timeline**: Phase 3 or Phase 4 (after core functionality complete)
5. **Risk**: None (optional instrumentation layer)

---

**Status**: 🟡 Stub | **Priority**: 🟡 Medium | **Last Updated**: 2026-05-03

---

## Audit Timestamp (2026-05-03)

**Agent 2 Infrastructure Audit — NOT STARTED**

- **Status**: 🔴 0% Implemented (Stub Only)
- **5-File Pattern**: ❌ Missing (0/5 files)
- **Files**: 1 (plan.md only) | **LOC**: 0
- **Dependencies**: 0 (5 external packages planned)
- **Reverse Dependencies**: None yet (will integrate @asgi, @db)
- **Blockers**: None (optional infrastructure)
- **Phase Ready**: Phase 4+ 🔴 (NOT READY - deferred)
- **Last Audited**: 2026-05-03 by Agent 2
- **Audit Reference**: this local document; query `.plan/session.db` for live status
- **Effort Estimate**: 8-12 hours for full implementation
- **Action**: Schedule for Phase 4 backlog

---

## Phase 14 — OtelBridge

The `otel/` directory is the **SDK config layer** only. The bridge connecting `@events` to OTel lives elsewhere:

- **Bridge location**: `css/core/events/otel_bridge.py`
- **Bridge responsibility**: `OtelBridge.run()` groups all events sharing the same `correlation_id` into one OTel trace tree
- `DomainEvent`, `EventStore`, and `OtelBridge` live in `css/core/events/` (Phase 6 T6.3), NOT in `otel/`
- `otel/` provides SDK setup (exporters, resource, tracer/meter providers) consumed by the bridge

```
css/core/events/otel_bridge.py  ← consumes @events + css/core/otel/
css/core/otel/                  ← SDK config: exporters, tracer, meter
```

---

## Sync Reminder

> `.plan/session.db` is authoritative for implementation status. Update it for
> implementation-state changes and keep this local plan accurate for execution.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
