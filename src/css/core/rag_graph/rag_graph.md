# @rag_graph — Core Graph Retrieval Subsystem Plan
The current implementation destination is `src/css/core/rag_graph/`. Any
future nesting with vector retrieval requires an explicit import/router
migration; it is not an implementation prerequisite.
⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Dedicated GraphRAG infrastructure for the whole platform:
- graph ingest and entity projection
- Neo4j-backed entity, relationship, and community retrieval
- traversal and path-based retrieval for graph-heavy queries
- graph-side retrieval results consumed by `core/rag_vector` in `graph` and `hybrid` modes
- graph projections from MITRE ATT&CK, threat-intel, and stable intelligence outputs

This is planned as a **core-owned** subsystem because graph retrieval is a shared capability, not a feature-module concern.

## Package Placement

The planned package currently exists at `src/css/core/rag_graph/`. A future
source refactor may nest it under `src/css/core/memory/rag_graph/` alongside
vector retrieval, but implementers must use the current location until imports,
router/loader behavior, and graph backend wiring are intentionally migrated.
The GraphRAG plan replaces obsolete vault/projection planning rather than
depending on it.

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
- `modules/triage`: may emit stable extracted entities, ATT&CK candidate
  mappings, and confidence-scored links into graph ingest via module-owned
  triage entrypoints (`ClassifyStage`, `classify_query`, `classify`).
- `modules/workflows` + `modules/graphs`: operational graphs remain separate, but later graph exports may feed GraphRAG.
- `core/cache`: graph retrieval caching must use the shared retrieval cache layer; no ad-hoc storage is allowed.

See `.plan/architecture/rag-knowledgebase.md` and `.plan/architecture/intelligence-retrieval-graph.md` for the combined system concept.

## Initial Todos

- `graph-rag-core-ownership`
- `graph-rag-backend`
- `rag-query-modes`
- `rag-fusion-layer`
- `rag-context-wire`

## Executable Owner Contract

### Current And Planned File Map

| Path | Reality / planned symbols |
|------|----------------------------|
| `src/css/core/rag_graph/__init__.py` | Current empty export stub; future canonical GraphRAG exports belong here. |
| `src/css/core/rag_graph/rag_graph.md` | Current ownership and implementation contract. |
| `src/css/core/rag_graph/types.py` | Planned graph ingest/query/result/provenance value types. |
| `src/css/core/rag_graph/backend.py` | Planned `GraphRagBackend` and Neo4j adapter boundary. |
| `src/css/core/rag_vector/retriever.py` | Caller-facing retrieval implementation extended for graph/hybrid modes. |
| `src/css/core/memory/context_window.py` and `src/css/core/memory/service.py` | Existing memory context surfaces to inspect for `rag-context-wire`; do not invent a second context owner. |
| `src/css/modules/mitre/` and `src/css/modules/threat_intel/` | Canonical relational sources for graph projections. |

### Live Todo Map

| Todo ID | Status | Owner contract |
|---------|--------|----------------|
| `graph-rag-core-ownership` | pending | Establish exports/types in the current package path without a documentation-only move. |
| `graph-rag-backend` | pending | Implement provider-neutral graph ingest/traversal and provenance-aware retrieval. |
| `rag-query-modes`, `rag-fusion-layer` | pending | `core/rag_vector` exposes vector/graph/hybrid/auto routing and deterministic fusion. |
| `rag-context-wire` | pending | Integrate ranked hybrid evidence through the existing memory context and agent boundary. |
| `graph-rag-mitre-projection`, `graph-rag-threat-intel-projection` | pending | Project stable domain records while their modules remain authoritative. |

### Numbered Work Order And Validation

1. Define GraphRAG protocol/result/entity/edge types and exports in the
   existing `core/rag_graph` package, then implement a backend behind them.
2. Add graph/hybrid dispatch and fusion through `core/rag_vector`; preserve
   provenance and shared retrieval-cache behavior.
3. Wire retrieval into the confirmed `core/memory` context assembler surface
   after inspecting its concrete method, then add domain projections.
4. Validate imports, graph fixture ingest/query/traversal, hybrid fallback and
   ranking, context token budgeting, idempotent projection, and dependency
   direction between domain modules and the core retrieval packages.
