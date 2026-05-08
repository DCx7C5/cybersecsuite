# Intelligence, Retrieval & Workflow Graph Architecture

## Decision

CyberSecSuite will treat **local intelligence, memory, hybrid retrieval, and workflow graphs** as one coordinated architecture with clear ownership boundaries.

- `src/css/core/memory/` owns conversation turns, summaries, session state, canvas, and vault persistence
- `src/css/modules/triage/` owns lightweight local intelligence: tagging, complexity/routing, confidence, and future retrieval hints
- `src/css/core/vector_rag/` owns vector retrieval plus hybrid routing, fusion, and context handoff
- `src/css/core/graph_rag/` owns graph ingestion, graph queries, and GraphRAG retrieval
- `src/css/modules/graphs/` owns workflow/session/approval graph building, snapshots, and live graph APIs
- `src/css/modules/workflows/` owns executable workflow definitions and graph-backed workflow authoring later
- `src/css/core/cache/` and `src/css/core/prompt_cache/` provide cache infrastructure, not business logic

## Core Principles

- Keep **two graph domains** separate:
  - **knowledge graph** for GraphRAG retrieval
  - **operational workflow graph** for workflow execution, approvals, and live visualization
- `auto` retrieval starts with simple policy logic; Phase 21 intelligence may later supply route hints.
- `core/memory` is the handoff point between conversation history and retrieval.
- Workflow/session graphs may later be **projected** into GraphRAG, but GraphRAG must not depend on live UI graph builders.
- Keep cache responsibilities split:
  - `core/cache/` for generic KV + retrieval caching
  - `core/prompt_cache/` for LLM prompt/response reuse

## Architecture Graph

```mermaid
flowchart TB
    subgraph Inputs["Inputs"]
        User["User turns / agent requests"]
        Docs["Docs / CVEs / playbooks / feeds"]
        Mitre["MITRE ATT&CK data"]
        Intel["Threat-intel entities / feeds"]
        Events["Task / tool / approval / LLM events"]
    end

    subgraph Intelligence["modules/triage (later intelligence)"]
        Pre["PreFilter / complexity routing"]
        Tagger["MessageTagger + MemoryTagger"]
        Conf["Confidence / drift / quality gates"]
        Hint["Future retrieval route hints"]
    end

    subgraph Memory["core/memory"]
        MM["MemoryManager"]
        CW["ContextAssembler / context window"]
        Vault["Vault / summaries / memory entries"]
    end

    subgraph Retrieval["core/vector_rag"]
        HRS["HybridRetrievalService"]
        Router{"Mode Router\nvector | graph | hybrid | auto"}
        Cache["Retrieval cache\nvia core/cache"]
        Vec["VectorRagBackend"]
        Fuse["Fusion layer"]
    end

    subgraph GraphRag["core/graph_rag"]
        Graph["GraphRagBackend"]
        GraphIngest["Graph ingest / entity projection"]
    end

    subgraph Graphs["modules/graphs + modules/workflows"]
        Flow["WorkflowGraphBuilder"]
        Session["SessionFlowBuilder"]
        Approval["ApprovalFlowBuilder"]
        Snap["GraphSnapshot store"]
        Export["Workflow graph export\nlater GraphRAG input"]
    end

    subgraph LLM["LLM + Execution"]
        Agent["AgentExecutor"]
        ULLM["UnifiedLLMClient"]
        Prompt["core/prompt_cache"]
    end

    subgraph Stores["Storage"]
        PG["PostgreSQL + pgvector"]
        Neo["Neo4j / graph adapter"]
        Redis["Redis"]
        OO["OpenObserve / event streams"]
    end

    User --> MM
    User --> Pre
    Docs --> Vec
    Docs --> Graph
    Docs --> GraphIngest
    Mitre --> Graph
    Mitre --> GraphIngest
    Intel --> Graph
    Intel --> GraphIngest
    Events --> Flow
    Events --> Session
    Events --> Approval
    Events --> OO

    MM --> Tagger
    Tagger --> Vault
    MM --> CW
    Pre -.later.-> Hint
    Hint -.auto only.-> Router
    Conf -.quality gates.-> Agent

    CW --> HRS
    HRS --> Router
    HRS <--> Cache
    Router --> Vec
    Router --> Graph
    Vec <--> PG
    Graph <--> Neo
    GraphIngest <--> Neo
    Vec --> Fuse
    Graph --> Fuse
    Fuse --> CW
    CW --> Agent

    Agent --> ULLM
    ULLM <--> Prompt

    Flow --> Snap
    Session --> Snap
    Approval --> Snap
    Snap -.later.-> Export
    Export -.projected input.-> Graph

    Cache <--> Redis
    Prompt <--> Redis
    Snap <--> PG

    classDef group fill:#eef4ff,stroke:#4a6fa5,color:#10233f;
    classDef core fill:#ecfff3,stroke:#2f7d57,color:#123524;
    classDef store fill:#fff6e8,stroke:#b7791f,color:#4a2b00;

    class Inputs,Intelligence,Graphs,LLM group;
    class Memory,Retrieval,Prompt,MM,CW,Vault,HRS,Router,Cache,Vec,Graph,Fuse core;
    class Stores,PG,Neo,Redis,OO,Snap store;
```

## End-to-End Runtime Loop

1. A user turn is stored in `core/memory`.
2. Phase 21 intelligence can tag the turn, score confidence, and later provide route hints.
3. Stable intelligence outputs can also emit extracted entities, ATT&CK hints, and confidence-scored relationships into the graph ingest path.
4. `ContextAssembler` asks `core/vector_rag` for supporting context.
5. `HybridRetrievalService` chooses `vector`, `graph`, `hybrid`, or `auto`.
6. Results are fused, deduplicated, and returned to the agent context.
7. The agent calls the LLM through `UnifiedLLMClient`, with prompt caching handled separately.
8. Execution events feed workflow/session/approval graph builders for live and historical graph views.

## Boundary Rules

- `modules/triage/` does not own retrieval or graph persistence.
- `core/vector_rag/` does not own workflow authoring, graph persistence, or graph UI.
- `core/graph_rag/` owns graph retrieval internals, not workflow authoring or graph UI.
- `modules/graphs/` does not decide retrieval mode.
- `modules/workflows/` owns executable DAG logic; `modules/graphs/` owns rendering/snapshots.
- Workflow graphs may enrich GraphRAG only through explicit projection/export.
- MITRE and threat-intel remain canonically owned by their domain modules; graph ingest is a projection layer.
- Only stable intelligence outputs belong in graph ingest; ephemeral routing or quality-gate state does not.

## Phase Mapping

- **Phase 20**: memory expansion + hybrid retrieval core
- **Phase 21**: local intelligence features, memory tagging, pre-filtering, future `auto` retrieval hints
- **Phase 27**: workflow/session/approval graph builders and telemetry graphs
- **Phase 29**: cybersec retrieval ingestion on top of `core/vector_rag/` + `core/graph_rag/`
- **Phase 30**: workflow engine + IPC on top of memory, events, approvals, and graph infrastructure

## Related Docs

- [rag-knowledgebase.md](./rag-knowledgebase.md)
- [caching-architecture.md](./caching-architecture.md)
- [system-overview.md](./system-overview.md)
- [module-relationships.md](./module-relationships.md)
