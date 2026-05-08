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
- `core/vector_rag`: workflow steps may request hybrid retrieval context, but retrieval remains a separate subsystem
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

## Related Docs

- `.plan/architecture/intelligence-retrieval-graph.md`
- `.plan/architecture/rag-knowledgebase.md`
- `.plan/architecture/system-overview.md`
