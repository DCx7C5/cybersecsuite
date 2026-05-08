# @vector_rag — Hybrid Retrieval / Legacy Module Staging

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Current staging area for retrieval code that is planned to become shared core infrastructure.

Long-term ownership target:
- `src/css/core/vector_rag/`
- `src/css/core/graph_rag/` for GraphRAG-specific code

Current legacy runtime path:
- `src/css/modules/vector_rag/`

## Current State

- The package still lives under `modules/`, but planning ownership now points toward `core/`.
- The same-name markdown rule is now satisfied with `vector_rag.md`.
- Phase 20 now owns the hybrid retrieval foundation:
  - `rag-core-ownership`
  - `rag-cache-layer`
  - `graph-rag-core-ownership`
  - `rag-vector-backend`
  - `graph-rag-backend`
  - `rag-query-modes`
  - `rag-fusion-layer`
  - `rag-context-wire`
- Phase 29 `domain-rag-ingestion` now means cybersec retrieval ingestion and usage on top of the shared retrieval core.

## Planned Architecture

- **VectorRAG**: PostgreSQL + pgvector for documents, chunks, embeddings, and semantic retrieval
- **GraphRAG**: graph-store-backed retrieval for entities, relationships, communities, and traversal-heavy queries under `src/css/core/graph_rag/`
- **Modes**: `vector`, `graph`, `hybrid`, `auto`
- **Fusion**: merge, rerank, deduplicate, and preserve provenance across backends
- **Caching**: shared retrieval cache via `core/cache` for query results, embedding reuse, route hints, and invalidation-aware acceleration
- **Future hook**: Phase 21 intelligence/triage may later help drive `auto` mode

## Integration Points

- `core/memory` is the main caller once `rag-context-wire` lands.
- `modules/triage` can later influence `AUTO` routing, but remains separate from retrieval execution.
- `core/graph_rag` will own graph retrieval code after the core split lands; `core/vector_rag` remains the hybrid coordinator.
- `modules/mitre` and `modules/threat_intel` keep canonical cybersec data and project graph-native structures into `core/graph_rag`.
- `modules/workflows` and `modules/graphs` may later project workflow/session graph data into GraphRAG, without coupling live graph builders directly to retrieval.
- `core/cache` backs retrieval caching; `core/prompt_cache` remains an independent LLM caching concern.

## Local Rules

- Current ORM models still inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Treat this directory as a migration surface until `rag-core-ownership` lands
- GraphRAG-specific implementation should move toward `src/css/core/graph_rag/`, not stay in this staging package
- Sync any planning or ownership changes here with `.plan/plan.md`, `.plan/architecture/rag-knowledgebase.md`, and `.plan/session.db`
