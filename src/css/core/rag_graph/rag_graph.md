# @rag_graph — Core Graph Retrieval Subsystem Plan

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Dedicated GraphRAG infrastructure for the whole platform:
- graph ingest and entity projection
- Neo4j-backed entity, relationship, and community retrieval
- traversal and path-based retrieval for graph-heavy queries
- graph-side retrieval results consumed by `core/rag_vector` in `graph` and `hybrid` modes
- graph projections from MITRE ATT&CK, threat-intel, and stable intelligence outputs

This is planned as a **core-owned** subsystem because graph retrieval is a shared capability, not a feature-module concern.

## Planned Responsibilities

- graph entity and relationship retrieval contracts
- graph ingest / entity projection contracts
- graph traversal, neighborhood, and path/community query contracts
- Neo4j adapter boundaries and graph schema ownership
- retrieval cache participation through `core/cache`
- integration with `core/rag_vector` for `graph` and `hybrid` modes

## Phase Ownership

- **Phase 20**: establish `core/rag_graph/` and build the GraphRAG backend
- **Phase 29**: connect cybersec entities, relationships, and retrieval-ingestion projections
- **Phase 21**: optional intelligence/triage participation in `AUTO` route choice through `core/rag_vector`

## Integration Points

- `core/rag_vector`: owns the hybrid retrieval entry point and calls into `core/rag_graph` for graph/hybrid retrieval.
- `core/memory`: graph retrieval results flow back into memory-backed context assembly through `rag-context-wire`.
- `modules/mitre` + `modules/threat_intel`: canonical relational owners that project graph-native entities and relationships into GraphRAG.
- `modules/triage`: may emit stable extracted entities, ATT&CK candidate mappings, and confidence-scored links into graph ingest.
- `modules/workflows` + `modules/graphs`: operational graphs remain separate, but later graph exports may feed GraphRAG.
- `core/cache`: graph retrieval caching must use the shared retrieval cache layer; no ad-hoc storage is allowed.

See `.plan/architecture/rag-knowledgebase.md` and `.plan/architecture/intelligence-retrieval-graph.md` for the combined system concept.

## Initial Todos

- `graph-rag-core-ownership`
- `graph-rag-backend`
- `rag-query-modes`
- `rag-fusion-layer`
- `rag-context-wire`
