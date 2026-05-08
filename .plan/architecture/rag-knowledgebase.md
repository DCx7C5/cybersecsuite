# RAG & Knowledgebase

## Decision

`vector_rag` is planned as a **core-owned retrieval subsystem**, not a long-term business module.

Target ownership:
- Runtime home: `src/css/core/vector_rag/`
- Current legacy path until migration: `src/css/modules/vector_rag/`
- Domain integrations stay in feature phases, but shared retrieval logic lives in `core/`

## Goal

Build a **hybrid retrieval stack** with:
- **VectorRAG** on PostgreSQL + pgvector for fast semantic/document retrieval
- **GraphRAG** on a graph store (Neo4j first) for entity/relationship/community traversal
- **Mode selection** so callers can force `vector`, `graph`, `hybrid`, or `auto`
- **Fusion layer** that merges, reranks, deduplicates, and preserves provenance
- **Cache layer** on top of `core/cache` for query results, embedding reuse, route hints, and invalidation-aware retrieval acceleration

`auto` mode may later delegate backend choice to the intelligence/triage model, but the first design must work without that dependency.

## Architecture Graph

```mermaid
flowchart TB
    subgraph Callers["Callers"]
        API["REST / internal callers"]
        Ctx["ContextAssembler"]
        Agent["AgentExecutor"]
    end

    subgraph Core["core/vector_rag"]
        HRS["HybridRetrievalService"]
        Router{"RetrievalMode Router\nvector | graph | hybrid | auto"}
        Policy["Auto Routing Policy"]
        Future["Future Phase 21\nintelligence / triage hook"]
        Cache["Retrieval Cache Layer\nvia core/cache"]
        Vec["VectorRagBackend"]
        Graph["GraphRagBackend"]
        Fusion["Result Fusion Layer\nmerge + rerank + dedupe + provenance"]
    end

    subgraph Storage["Storage"]
        PG["PostgreSQL + pgvector\nDocuments / chunks / embeddings / metadata"]
        Neo["Neo4j or graph adapter\nEntities / relationships / communities"]
        Redis["Redis\nHot cache / route hints / embedding reuse"]
        CachePG["core/cache L3\nPostgreSQL cache entries"]
    end

    subgraph Sources["Knowledge Sources"]
        Docs["CVE feeds / PDFs / playbooks / runbooks"]
        Entities["Extracted entities + relationships"]
        Workflow["Future workflow graph exports"]
    end

    subgraph Outputs["Downstream Use"]
        Prompt["Retrieved context payload"]
        Answer["Agent response generation"]
    end

    API --> HRS
    Ctx --> HRS
    Agent --> HRS

    HRS --> Router
    HRS <--> Cache

    Router -->|vector| Vec
    Router -->|graph| Graph
    Router -->|hybrid| Vec
    Router -->|hybrid| Graph
    Router -->|auto| Policy

    Policy --> Vec
    Policy --> Graph
    Future -.later.-> Policy

    Docs --> Vec
    Docs --> Graph
    Entities --> Graph
    Workflow -.later.-> Graph

    Vec <--> Cache
    Graph <--> Cache
    Vec <--> PG
    Graph <--> Neo
    Cache <--> Redis
    Cache <--> CachePG

    Vec --> Fusion
    Graph --> Fusion
    Fusion --> Prompt
    Prompt --> Answer

    classDef caller fill:#eef4ff,stroke:#4a6fa5,color:#10233f;
    classDef core fill:#ecfff3,stroke:#2f7d57,color:#123524;
    classDef store fill:#fff6e8,stroke:#b7791f,color:#4a2b00;
    classDef source fill:#f7efff,stroke:#7a4da3,color:#331a4d;
    classDef output fill:#ffeef1,stroke:#b83250,color:#4a1020;

    class API,Ctx,Agent caller;
    class HRS,Router,Policy,Future,Cache,Vec,Graph,Fusion core;
    class PG,Neo,Redis,CachePG store;
    class Docs,Entities,Workflow source;
    class Prompt,Answer output;
```

## Retrieval Flow

```text
Caller
  -> HybridRetrievalService
  -> router decides vector / graph / hybrid / auto
  -> selected backend(s) execute
  -> fusion layer merges and reranks
  -> context payload returns to agent/context assembly
```

## Storage Roles

- PostgreSQL + pgvector: documents, chunks, embeddings, metadata, semantic search
- Neo4j / graph adapter: entities, relationships, communities, traversal queries
- `core/cache`: retrieval cache facade with L1 memory, L2 Redis, and optional L3 PostgreSQL cache entries
- Redis: hot cache, embedding reuse, route hints, and short-lived hybrid retrieval state

## Core Components

- `VectorRagBackend`: document/chunk ingestion, pgvector search, metadata filtering
- `GraphRagBackend`: entity extraction pipeline, graph ingest/query, path/community retrieval
- `RetrievalCacheLayer`: query-result caching, embedding reuse, route hints, and invalidation rules via `core/cache`
- `HybridRetrievalService`: single entry point for callers
- `QueryRouter`: mode resolution for `VECTOR`, `GRAPH`, `HYBRID`, `AUTO`
- `FusionLayer`: score normalization, provenance, deduplication, reranking
- `RetrievalMode`: explicit caller-visible mode enum

## Mode Policy

- `vector`: prefer speed and broad recall
- `graph`: prefer entity-heavy or relationship-heavy reasoning
- `hybrid`: execute both paths and fuse results
- `auto`: start with a routing policy; later it may call Phase 21 intelligence/triage

Future hook:
- Phase 21 intelligence can classify retrieval complexity and help choose backend(s) in `auto`

## GraphRAG Scope

GraphRAG is not only for workflow graphs.

Primary graph inputs:
- extracted entities from cybersec documents
- relationships between CVEs, malware, tools, actors, campaigns, mitigations, incidents
- future workflow / execution graph exports where useful

Important boundary:
- Phase 27 graphs are mainly visualization and live graph UX
- GraphRAG uses graph data for retrieval and reasoning
- The systems may share graph data later, but should not be hard-coupled at first implementation

## Phase Mapping

- **Phase 20**: core hybrid retrieval foundation (`rag-*` todos)
- **Phase 29**: cybersec knowledge ingestion and domain-facing usage on top of `core/vector_rag/`
- **Phase 21**: optional intelligence/triage participation in `AUTO` route choice
- **Future workflow graph DB work**: may later feed GraphRAG as an additional graph source

## System Integration

`core/vector_rag` sits between memory/intelligence on the input side and agent execution on the output side.

- `core/memory`: `ContextAssembler` and memory-backed session state are the main retrieval callers.
- `modules/triage/`: Phase 21 can tag memory, pre-filter trivial requests, and later provide `AUTO` route hints.
- `modules/graphs/` + `modules/workflows/`: operational workflow graphs stay separate from the knowledge graph, but later workflow graph exports may become an additional GraphRAG source.
- `core/cache/`: retrieval caching is required from day one for embeddings, query results, and route hints.
- `core/prompt_cache/`: prompt caching remains separate and applies to LLM calls, not retrieval result storage.

See [intelligence-retrieval-graph.md](./intelligence-retrieval-graph.md) for the combined system view.

## Immediate Planning Consequences

- `domain-knowledge` is no longer a standalone `modules/knowledge/` concept
- the shared retrieval substrate is planned under `core/vector_rag/`
- the old `modules/vector_rag/` package is now legacy migration surface until the core move lands
- caching is part of the retrieval design from day one; it is not a later optimization pass
