# Database Architecture

## Overview

`docker-compose.yml` currently runs the platform's **storage and observability infrastructure only**. The ASGI app, frontend dev server, and Ollama run outside Docker.

## Storage Map

| Service | Role | Port(s) | Persistence | Primary Consumers |
|---------|------|---------|-------------|-------------------|
| `cybersec-postgres` | Primary relational database + planned pgvector host + durable cache tier | `5432` | `pg_data`, `pg_socket` | core models, memory, vector retrieval after pgvector install, cache L3 |
| `cybersec-redis` | Shared hot cache / coordination store | `6379` | `redis_data`, `redis_socket` | `core/cache`, prompt cache, session state, workers |
| `cybersec-neo4j` | Graph database for GraphRAG and future graph projections | `7474`, `7687` | `neo_data`, `neo_logs`, `neo_import`, `neo_plugins` | `core/rag_graph`, `core/rag_vector` hybrid mode, MITRE/threat-intel projections, future workflow graph exports |
| `cybersec-openobserve` | Telemetry, audit, and time-series observability store | `5080` | `oo_data` | events, metrics, cost telemetry, dashboards |

## Architecture Graph

```mermaid
flowchart LR
    App["App Runtime\n(outside Docker)"]
    Memory["core/memory"]
    Cache["core/cache + core/prompt_cache"]
    RAG["core/rag_vector"]
    GraphRag["core/rag_graph"]
    Graphs["modules/graphs / workflows"]

    PG["PostgreSQL\n(pgvector planned)"]
    Redis["Redis"]
    Neo["Neo4j"]
    OO["OpenObserve"]

    App --> Memory
    App --> Cache
    App --> RAG
    App --> GraphRag
    App --> Graphs

    Memory --> PG
    Cache <--> Redis
    Cache <--> PG
    RAG <--> PG
    RAG <--> GraphRag
    GraphRag <--> Neo
    Graphs -.events / telemetry.-> OO
    Graphs -.later export.-> Neo
    App -.metrics / audit.-> OO
```

## Boundaries

- **PostgreSQL** is the main system of record for transactional data and state management. It becomes the VectorRAG storage layer only after the custom image actually ships `pgvector`.
- **Redis** accelerates runtime behavior; it does not replace durable memory or relational state.
- **Neo4j** is reserved for `core/rag_graph` retrieval and later graph projections from MITRE, threat-intel, stable intelligence outputs, and workflow exports. It is not the primary source of truth for workflow execution state.
- **OpenObserve** is observability storage only, not application state storage.

## Compose Reality

- Compose is **infra-only** right now.
- App runtime depends on these services over the internal `cybersec` network.
- Neo4j is now a first-class infra service, which matches the GraphRAG plan.
- The current `cybersec-postgres` image is a custom `postgres:18-alpine` build, but it still does **not** install `pgvector`. Phase 20 `mem-pgvector-setup` must add the extension package and initialization path before vector retrieval can run.
