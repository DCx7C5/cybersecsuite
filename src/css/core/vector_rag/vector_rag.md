# @vector_rag — Core Retrieval Subsystem Plan

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Shared vector and hybrid retrieval infrastructure for the whole platform:
- VectorRAG over PostgreSQL + pgvector
- Hybrid retrieval with caller-visible mode selection
- Retrieval caching via `core/cache`

This is planned as a **core-owned** subsystem because multiple modules are expected to depend on it.

Sibling subsystem:
- `src/css/core/graph_rag/` owns GraphRAG-specific graph ingest, graph queries, and traversal retrieval

## Planned Responsibilities

- document/chunk/embedding retrieval contracts
- retrieval cache contracts: query cache keys, embedding reuse, TTLs, invalidation
- retrieval mode routing: `vector`, `graph`, `hybrid`, `auto`
- fusion, reranking, deduplication, provenance across vector and graph results
- integration contracts with `core/graph_rag`
- context handoff into memory/context assembly and agent execution

## Phase Ownership

- **Phase 20**: build the shared hybrid retrieval core
- **Phase 29**: connect cybersec knowledge sources and domain usage
- **Phase 21**: optional intelligence/triage participation in `auto` routing later

## Integration Points

- `core/memory`: `ContextAssembler` and memory-backed context assembly are the primary callers.
- `modules/triage`: later intelligence features may contribute `AUTO` route hints and memory tags, but do not own retrieval execution.
- `core/graph_rag`: owns the graph retrieval backend used in `graph` and `hybrid` modes.
- `modules/mitre` + `modules/threat_intel`: project graph-native entities and relationships into `core/graph_rag` while keeping canonical domain ownership in their modules.
- `modules/workflows` + `modules/graphs`: workflow/session/approval graphs stay separate from GraphRAG at first; later graph exports may become additional graph retrieval input.
- `core/cache`: owns the retrieval cache substrate for embeddings, results, TTLs, and invalidation.
- `core/prompt_cache`: separate concern for LLM prompt/response reuse only.

See `.plan/architecture/intelligence-retrieval-graph.md` for the combined system concept.

## Initial Todos

- `rag-core-ownership`
- `rag-cache-layer`
- `graph-rag-core-ownership`
- `rag-vector-backend`
- `graph-rag-backend`
- `rag-query-modes`
- `rag-fusion-layer`
- `rag-context-wire`
