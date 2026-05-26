# @siem — SIEM/EDR Integration and Response

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document is the executable local specification for the SIEM/EDR area.

---

## Purpose

`@siem` will ingest, normalize, analyze, and respond to security telemetry from external SIEM and EDR platforms such as Splunk, CrowdStrike, and SentinelOne.

The core storage split is:
- **OpenObserve first** for raw/high-volume telemetry, audit streams, dashboards, and fast operational search
- **PostgreSQL** for curated alerts, incidents, response state, and structured application records
- **Neo4j / GraphRAG** for entity and attack-path relationships

## Current Code Reality

| File | Current surface | Gap |
|------|-----------------|-----|
| `enums.py` | `SiemSeverity` and `SiemSource`. | No normalized event value type or lifecycle/status enums yet. |
| `exceptions.py` | Base, ingest, and response exceptions. | No implemented service paths use them yet. |
| `__init__.py` | Exports enums and exceptions. | No models, endpoints, ingest, analyzer, or response runtime exists. |

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.events` | → consumes | EventStore, domain events, instrumentation |
| `css.modules.mcps` | → consumes | MCP-backed SIEM/EDR connectors and response actions |
| `css.core.observability` | → consumes | OpenObserve client + stream definitions for telemetry fan-out |
| `css.core.rag_graph` | → consumes | Graph projection of entities, techniques, and attack paths |
| `css.core.rag_vector` | → consumes | Similar incident and knowledge retrieval |
| `css.modules.workflows` | → consumes | Response playbooks |
| `css.modules.approvals` | → consumes | Human approval for destructive actions |
| `css.core.permissions` | → consumes | Policy/permission checks for response actions |
| `css.core.cache` | note | No direct SIEM KV-cache ownership; OpenObserve, PostgreSQL, and GraphRAG stay primary while retrieval/prompt caches are consumed indirectly |

## Execution Flow

```text
External SIEM / EDR platform
        ↓ via MCP runtime
SiemIngestService
        ↓ normalize to SecurityEvent
        ↓
OpenObserve first write (raw telemetry, dashboards, auditability)
        ↓
PostgreSQL curated alert / incident records
        ↓
GraphRAG entity + relationship projection
        ↓
SiemAnalyzerAgent correlation and remediation
        ↓
Workflow playbooks + approval gate for actions
```

## Phase 37 Implementation Scope

| Todo ID | What it must produce |
|---------|----------------------|
| `siem-types` | `core/siem/types.py` with `SecurityEvent` and SIEM event namespaces |
| `siem-module` | `modules/siem/` package with ORM models, endpoints, enums, exceptions, and module exports |
| `siem-ingest` | MCP-backed ingest service that normalizes external detections into `SecurityEvent` |
| `siem-models` | Storage fan-out: OpenObserve telemetry path, PostgreSQL relational records, GraphRAG projection |
| `siem-analyzer` | Analyzer that correlates telemetry with vector + graph retrieval and emits remediation context |
| `siem-response` | Workflow-backed response actions with approval enforcement |

### SecurityEvent Contract

The normalized ingest boundary must supply at least:

| Field | Meaning |
|-------|---------|
| `source` | Connector/vendor identity such as Splunk, CrowdStrike, or SentinelOne. |
| `severity`, `timestamp` | Normalized priority and event time. |
| `source_ip`, `host_id`, `process_id` | Entity keys used for storage and graph projection when present. |
| `mitre_technique` | ATT&CK candidate/reference when available. |
| `raw_data` | Preserved vendor payload with provenance controls. |
| `payload` | Normalized structured content consumed by application workflows. |

### API and Response Contract

| Surface | Requirement |
|---------|-------------|
| Alerts/incidents routes | Expose curated relational alert/incident state under `/api/siem/*`. |
| Attack-path query | Return GraphRAG-backed relationship evidence with provenance. |
| Ingest service | Use MCP connectors, normalize `SecurityEvent`, and send raw telemetry to OpenObserve first. |
| Analyzer | Correlate OpenObserve events with vector/graph evidence before model-assisted remediation generation. |
| Response manager | Support isolate endpoint, block IP, and kill process actions only through workflow and human-approval enforcement. |

## Non-Negotiable Boundary

Do not build SIEM as a Postgres-only feature.

For this codebase:
- OpenObserve is the primary operational telemetry substrate
- PostgreSQL is the application record layer
- GraphRAG is the relationship/correlation layer

If only one of those gets implemented, the order is:
1. OpenObserve ingestion path
2. PostgreSQL alert/incident records
3. GraphRAG projection
