# @workflows — Workflow Engine & Graph-backed Execution Plan

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track TODO/TASK/PHASE state in `.plan/session.db`. Keep this file aligned with current planning, but use `session.db` as the actual progress tracker.

## Purpose

`modules/workflows/` is planned to own executable workflow definitions, DAG orchestration, and later graph-backed workflow authoring.

## Planned Responsibilities

- define executable workflow/DAG models
- coordinate workflow steps with agents, tools, approvals, and IPC
- persist workflow state transitions
- emit workflow/task events for graph builders and audit trails
- support future graph-backed workflow creation and editing

## Integration Points

- `core/memory`: workflow runs consume session context, summaries, and memory-backed state
- `modules/triage`: local intelligence can classify incoming requests and influence which workflow path to trigger
- `core/rag_vector`: workflow steps may request hybrid retrieval context, but retrieval remains a separate subsystem
- `modules/graphs`: workflow state is projected into workflow/session/approval graph snapshots and live graph streams
- `modules/ipc`: workflow execution coordinates across orchestrators, teams, and subprocesses

## Graph Boundary

Workflow graphs are an **operational graph domain**:

- they model tasks, agents, tools, approvals, and execution edges
- they are distinct from GraphRAG knowledge graphs
- they may later be exported or projected into GraphRAG as an additional graph source
- live UI graph state must not become the direct source of truth for retrieval

## Phase Alignment

- **Phase 27**: graph builders, graph snapshots, and live workflow graph streaming
- **Phase 30**: workflow engine, DAG execution, IPC integration, and planner coordination
- **Future**: graph-backed workflow authoring on top of the operational graph model

## Implementation Contract

- Persist workflow definitions and run transitions independently from
  GraphRAG projection.
- Gate destructive workflow actions through `modules/approvals` and
  `core/permissions`.
- Emit workflow lifecycle events through `core/events`; IPC coordinates work
  but does not become persistence.

## Validation

- Test DAG ordering, failed-step behavior, approval blocking, resume/retry,
  and event projection without relying on live graph UI state.

## Related Docs

- `.plan/architecture/intelligence-retrieval-graph.md`
- `.plan/architecture/rag-knowledgebase.md`
- `.plan/architecture/system-overview.md`

## Executable Owner Contract

### Exact File And Symbol Map

| Path | Reality / planned symbols |
|------|----------------------------|
| `src/css/modules/workflows/__init__.py` | Existing empty export stub; no runtime engine is implemented yet. |
| `src/css/modules/workflows/models.py` | Planned `WorkflowDefinition`, step/edge/run-state value types and persistence boundary. |
| `src/css/modules/workflows/runner.py` | Planned `WorkflowRunner` DAG scheduling, suspend/resume/retry/cancel behavior. |
| `src/css/modules/workflows/endpoints.py` | Planned CRUD, execute, status, pause, resume, and cancel handlers. |
| `src/css/modules/planner-dev/planner.py` | Existing `PlannerOrchestrator`, `PlannerWorkingDirs`; extend via `planner-agent`. |
| `src/css/modules/planner-dev/models.py` | Existing `PlannerSession`, `PlanStep`. |
| `src/css/modules/planner-dev/analyzer.py` and `src/css/modules/planner-dev/store.py` | Existing analysis/persistence helpers; do not create a replacement planner module. |
| `src/css/modules/a2a_internal/dispatcher.py` | Existing messaging surface to compare before any separate `modules/ipc` package is introduced. |

### Live Todo Map

| Todo ID | Status | Required result |
|---------|--------|-----------------|
| `workflow-definition` | pending | Typed DAG definition plus persisted run transition state. |
| `workflow-runner` | pending | Asynchronous execution using approvals, IPC, and events without outsourcing persistence. |
| `workflow-endpoints` | pending | Authorized HTTP surface over definitions and runner state. |
| `ipc-message-bus` | pending | Resolve overlap with existing `a2a_internal` before creating a new IPC package. |
| `planner-agent` | pending | Extend `planner-dev` for decomposition and workflow dispatch. |

### Numbered Work Order And Validation

1. Implement and validate workflow definition/state contracts, including DAG
   cycle and missing-edge rejection.
2. Implement the runner over persisted transition state; pause destructive
   steps through approvals and coordinate only transient messages through IPC.
3. Resolve IPC versus `a2a_internal`, then wire planner decomposition and API
   handlers to the retained workflow owner.
4. Validate ordering, failure/retry/cancel/resume, approval blocking, event
   projection, API authorization, and independence from GraphRAG/UI graphs.
