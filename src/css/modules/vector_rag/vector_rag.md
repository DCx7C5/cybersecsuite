# @vector_rag — Hybrid Retrieval / Legacy Module Staging

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Current staging area for the retrieval and knowledgebase code that is planned to become a shared core subsystem.

Long-term ownership target:
- `src/css/core/vector_rag/`

Current legacy runtime path:
- `src/css/modules/vector_rag/`

## Current State

- The package still lives under `modules/`, but planning ownership now points toward `core/`.
- The same-name markdown rule is now satisfied with `vector_rag.md`.
- Phase 20 now owns the hybrid retrieval foundation:
  - `rag-core-ownership`
  - `rag-cache-layer`
  - `rag-vector-backend`
  - `rag-graph-backend`
  - `rag-query-modes`
  - `rag-fusion-layer`
  - `rag-context-wire`
- Phase 29 `domain-knowledge` now means cybersec knowledge ingestion and usage on top of the shared retrieval core.

## Planned Architecture

- **VectorRAG**: PostgreSQL + pgvector for documents, chunks, embeddings, and semantic retrieval
- **GraphRAG**: graph-store-backed retrieval for entities, relationships, communities, and traversal-heavy queries
- **Modes**: `vector`, `graph`, `hybrid`, `auto`
- **Fusion**: merge, rerank, deduplicate, and preserve provenance across backends
- **Caching**: shared retrieval cache via `core/cache` for query results, embedding reuse, route hints, and invalidation-aware acceleration
- **Future hook**: Phase 21 intelligence/triage may later help drive `auto` mode

## Integration Points

- `core/memory` is the main caller once `rag-context-wire` lands.
- `modules/triage` can later influence `AUTO` routing, but remains separate from retrieval execution.
- `modules/workflows` and `modules/graphs` may later project workflow/session graph data into GraphRAG, without coupling live graph builders directly to retrieval.
- `core/cache` backs retrieval caching; `core/prompt_cache` remains an independent LLM caching concern.

## Local Rules

- Current ORM models still inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Treat this directory as a migration surface until `rag-core-ownership` lands
- Sync any planning or ownership changes here with `.plan/plan.md`, `.plan/architecture/rag-knowledgebase.md`, and `.plan/session.db`
