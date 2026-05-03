# @otel — OpenTelemetry Observability

**Location**: `src/css/core/otel/`

**Responsibility**: Observability instrumentation (tracing, metrics, logs), OpenTelemetry SDK integration.

---

## Overview

OpenTelemetry (OTel) standardizes observability across distributed systems.

**Integration Points**:
- Jaeger/Zipkin for distributed tracing
- Prometheus for metrics collection
- ELK stack for log aggregation

---

## Implementation Status

🟡 **STUB PHASE** — Plan defined but implementation pending

---

## Architecture (Planned)

### Core Files (5-file pattern)

- `__init__.py` — Module exports
- `config.py` — OTel SDK configuration
- `tracing.py` — Trace instrumentation
- `metrics.py` — Metric collectors
- `logging.py` — Structured logging setup

### Feature Set (Planned)

1. **Distributed Tracing**
   - Request tracing across modules
   - Span creation for key operations
   - Jaeger/Zipkin export

2. **Metrics**
   - HTTP request metrics
   - Database query metrics
   - Custom business metrics
   - Prometheus export

3. **Structured Logging**
   - JSON log formatting
   - Context propagation
   - Log correlation with traces

---

## Dependencies

- `opentelemetry-api` — OTel API
- `opentelemetry-sdk` — OTel SDK
- `opentelemetry-exporter-jaeger` — Jaeger exporter
- `opentelemetry-instrumentation-fastapi` — FastAPI auto-instrumentation
- `opentelemetry-instrumentation-sqlalchemy` — SQLAlchemy auto-instrumentation

---

## Integration Plan

### Phase 1: Setup
- Initialize OTel SDK in app.py lifespan
- Configure exporter (Jaeger/Zipkin)
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

## Audit Results (2026-05-03)

**Agent 2 Core Infrastructure Audit**

### 5-File Pattern Compliance
❌ **MISSING** — Empty stub, plan.md is 0 bytes

| File | Status |
|------|--------|
| `__init__.py` | ❌ Missing |
| `config.py` | ❌ Missing |
| `tracing.py` | ❌ Missing |
| `metrics.py` | ❌ Missing |
| `logging.py` | ❌ Missing |

**Total**: 0 files, 0 LOC → Not started

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
