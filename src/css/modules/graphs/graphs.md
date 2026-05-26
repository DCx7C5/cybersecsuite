# @graphs - Operational Graph Visualization Plan

**Status**: Planned Phase 27 module; distinct from GraphRAG retrieval.

## Purpose

Operational graph views represent live or historical execution:

- workflow DAGs
- session turn flow
- tool call trees
- approval gates
- telemetry cost, latency and error charts

This module does not own knowledge retrieval graphs; `core/rag_graph` remains the GraphRAG subsystem.

## Data Sources and Rendering

| Source | Graph surface | Frontend renderer |
|--------|---------------|-------------------|
| PostgreSQL session/task/event records | workflow and session DAGs | XYFlow / `@xyflow/react` |
| Approval state | workflow overlays | XYFlow nodes/actions |
| OpenObserve metrics | cost/latency/error time series | Apache ECharts with worker-side aggregation |

## Required Types and APIs

- `GraphNode`, `GraphEdge`, `GraphSnapshot` as provider-agnostic `msgspec.Struct` types.
- Graph types for workflow, session, tool-call, agent dependency, approval and telemetry families.
- Snapshot API for historical graph retrieval.
- WebSocket graph patches for live operational views; SSE fallback only when justified by the transport design.

### API Surface

| Surface | Required result |
|---------|-----------------|
| `GET /graphs/workflow/{session_id}` | Full workflow/session DAG snapshot. |
| `GET /graphs/telemetry/{type}` | Time-windowed OpenObserve-backed chart series, filterable by project where available. |
| `GET /graphs/snapshots/{ref_id}` | Historical snapshots for playback/audit. |
| `POST /graphs/snapshots` | Save a named current snapshot. |
| `WS /ws/graphs/{graph_type}/{ref_id}` | Stream node/edge patches for live views. |
| `GET /graphs/stream/{type}/{id}` | SSE fallback where WebSocket transport is unavailable. |

## Required Builders

| Builder | Inputs | Output |
|---------|--------|--------|
| Workflow graph builder | task, agent, tool and event state | DAG snapshot and patches |
| Session flow builder | memory-backed conversation turns and execution events | turn-by-turn graph |
| Approval overlay | approval requests and decisions | gate nodes/edges |
| Telemetry service | OpenObserve query results | chart series data |

## Integration Points

- `modules/workflows`: workflow execution state.
- `modules/sessions`: session identity/history.
- `modules/approvals`: pending and resolved human decisions.
- `core/memory`: conversation turn context.
- `core/events`: live patch triggers.
- `core/asgi`: REST/WS/SSE transport surfaces.

## Boundary

Do not use UI graph state as authoritative runtime or retrieval storage. GraphRAG ingestion may later consume stable exported operational facts, but this module first serves operational visualization.

## Phase 27 Execution Order

| Work group | Todo IDs | Dependency |
|------------|----------|------------|
| Protocol | `graph-protocol`, `graph-types` | Foundation. |
| Workflow data | `graph-workflow-builder`, `graph-session-flow`, `graph-approval-flow`, `graph-snapshot-orm` | Protocol plus session/approval persistence. |
| Telemetry | `graph-telemetry-service`, `graph-openobserve-wire` | Protocol and OpenObserve client/stream definitions. |
| Live/API | `graph-ws-stream`, `graph-sse-endpoint`, `graph-endpoints` | Builders and snapshot persistence. |
| Frontend | `graph-react-flow`, `graph-recharts`, `graph-approval-overlay`, `graph-xyflow-adoption-plan` | Stable API/stream contract and Phase 18 shell. |
| Integration | `graph-events-wire`, `graph-module-files` | Event runtime and package/router registration. |

Despite the legacy `graph-recharts` todo identifier, the required telemetry
renderer is Apache ECharts with worker-backed processing; operational DAG views
use XYFlow.
