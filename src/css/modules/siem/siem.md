# @siem — SIEM/EDR Integration and Response

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly.

---

## Purpose

`@siem` will ingest, normalize, analyze, and respond to security telemetry from external SIEM and EDR platforms such as Splunk, CrowdStrike, and SentinelOne.

The core storage split is:
- **OpenObserve first** for raw/high-volume telemetry, audit streams, dashboards, and fast operational search
- **PostgreSQL** for curated alerts, incidents, response state, and structured application records
- **Neo4j / GraphRAG** for entity and attack-path relationships

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.events` | → consumes | EventStore, domain events, instrumentation |
| `css.modules.mcps` | → consumes | MCP-backed SIEM/EDR connectors and response actions |
| `css.core.observability` | → consumes | OpenObserve client + stream definitions for telemetry fan-out |
| `css.core.graph_rag` | → consumes | Graph projection of entities, techniques, and attack paths |
| `css.core.vector_rag` | → consumes | Similar incident and knowledge retrieval |
| `css.modules.workflows` | → consumes | Response playbooks |
| `css.modules.approvals` | → consumes | Human approval for destructive actions |
| `css.modules.permissions` | → consumes | Policy/permission checks for response actions |

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
