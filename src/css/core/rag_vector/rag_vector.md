# @rag_vector — Core Retrieval Subsystem Plan

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Shared vector and hybrid retrieval infrastructure for the whole platform:
- VectorRAG over PostgreSQL + pgvector
- Hybrid retrieval with caller-visible mode selection
- Retrieval caching via `core/cache`

This is planned as a **core-owned** subsystem because multiple modules are expected to depend on it.

Sibling subsystem:
- `src/css/core/rag_graph/` owns GraphRAG-specific graph ingest, graph queries, and traversal retrieval

## Package Placement

The executable package currently lives at `src/css/core/rag_vector/` and is
already referenced by endpoints, models, retrievers, and consumers. Moving it
under `src/css/core/memory/rag_vector/` is a reasonable future ownership
refactor because memory-backed context assembly is its primary caller, but it
is not a documentation-only rename. Audit imports, router registration, ORM
registration, and tests before carrying out that source move.

## Current Implementation

**Existing code** (pre-Phase 20 foundation):

| Class | File | Purpose |
|-------|------|---------|
| `KnowledgeRetriever` | `retriever.py` | Semantic + keyword hybrid document retrieval |
| `KnowledgeDocument` | `models.py` | ORM model for stored documents (content, type, source, tags, relevance_score, content_hash) |
| `KnowledgeIndex` | `models.py` | Inverted index with term frequency tracking |
| `SearchLog` | `models.py` | Query logging for analytics |
| `KnowledgeTag` | `models.py` | Tag/document associations |
| `DocumentType`, `DocumentStatus`, `SourceType`, `SearchType`, `RelevanceFeedback`, `TagCategory` | `enums.py` | Current enum definitions for document/search/tag concepts. |
| `router`, request/response structs | `endpoints.py` | Current `/api/rag_vector` document, search, tag, search-log, and feedback API. |

### Current API Surface

| Route family | Current behavior | Required follow-up |
|--------------|------------------|--------------------|
| `POST/GET/DELETE /api/rag_vector/documents...` | Organization-scoped document create/list/get/archive using `KnowledgeDocument`. | Replace authorization TODOs with confirmed auth/organization enforcement. |
| `POST /api/rag_vector/search` | Executes `keyword`, `semantic`, or `hybrid` retrieval through `KnowledgeRetriever`. | Align accepted modes and normalized result/provenance shape with `RetrievalMode`. |
| `GET/POST /api/rag_vector/tags` | Manages organization-scoped knowledge tags. | Reconcile tag enums/model fields with Phase 40 naming/meta standards. |
| `GET /api/rag_vector/search-log`, `POST /search-feedback` | Stores retrieval analytics and relevance feedback. | Route analytics into the retained telemetry/observability contract where required. |

Current `endpoints.py` symbol map:

| Surface | Implemented symbols |
|---------|---------------------|
| Payloads/results | `DocumentCreate`, `DocumentResponse`, `SearchRequest`, `SearchResult` |
| Documents | `create_document`, `list_documents`, `get_document`, `delete_document` |
| Retrieval | `search_knowledge` |
| Tags | `list_tags`, `create_tag` |
| Feedback/analytics | `get_search_log`, `record_search_feedback` |

The implemented endpoints currently carry authorization TODOs and string
request fields. Do not treat the planned hybrid retrieval backend as complete
until those boundaries and `pgvector` behavior are validated in source.

### KnowledgeRetriever (`retriever.py`)
- **Keyword search**: inverted index via `KnowledgeIndex` model, TF-weighted scoring
- **Semantic search**: pgvector placeholder — falls back to `relevance_score` ordering
- **Hybrid search**: merges keyword + semantic results with score averaging
- **Document ingestion**: content hash dedup → `KnowledgeDocument` create → term indexing (top 100 terms)
- **Search logging**: every query logged to `SearchLog` for analytics

### Planned Responsibilities

- document/chunk/embedding retrieval contracts
- retrieval cache contracts: query cache keys, embedding reuse, TTLs, invalidation
- retrieval mode routing: `vector`, `graph`, `hybrid`, `auto`
- fusion, reranking, deduplication, provenance across vector and graph results
- integration contracts with `core/rag_graph`
- context handoff into memory/context assembly and agent execution
- replacement for obsolete parallel projection planning; do not add a second
  retrieval persistence layer

## Phase Ownership

- **Phase 20**: build the shared hybrid retrieval core
- **Phase 29**: connect cybersec knowledge sources and domain usage
- **Phase 21**: optional intelligence/triage participation in `auto` routing later

## Integration Points

- `core/memory`: `ContextAssembler` and memory-backed context assembly are the primary callers.
- `modules/triage`: later intelligence features may contribute `AUTO` route
  hints and memory tags through `modules/triage` (`ClassifyStage`,
  `classify_query`, `classify`), but triage does not own retrieval execution.
- `core/rag_graph`: owns the graph retrieval backend used in `graph` and `hybrid` modes.
- `modules/mitre` + `modules/threat_intel`: project graph-native entities and relationships into `core/rag_graph` while keeping canonical domain ownership in their modules.
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

## Executable Phase 20 Contract (2026-05-26)

### Exact Files And Symbols

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/core/rag_vector/retriever.py` | Existing `KnowledgeRetriever`; semantic pgvector implementation remains pending. |
| `src/css/core/rag_vector/models.py`, `src/css/core/rag_vector/enums.py` | Existing document/index/tag/search records and enums. |
| `src/css/core/rag_vector/endpoints.py` | Existing document/search/tag/feedback handlers with authorization follow-up. |
| `src/css/core/rag_vector/backend.py` | Planned `VectorRagBackend` and normalized retrieval result contract. |
| `src/css/core/rag_vector/fusion.py` | Planned graph/vector fusion, deduplication, reranking, provenance behavior. |
| `src/css/core/memory/context_assembler.py` | Planned `ContextAssembler.assemble(entries, retrieval_results, token_budget)` consumer for `rag-context-wire`. |
| `src/css/modules/agents/base.py` | Current agent execution boundary consuming assembled context after memory wiring. |

### Live Todo Map And Work Order

| Todo IDs | Status | Required result |
|----------|--------|-----------------|
| `rag-core-ownership`, `rag-vector-backend`, `rag-cache-layer` | pending | Reconcile existing retriever/API/models and implement vector/cache contracts. |
| `graph-rag-core-ownership`, `graph-rag-backend` | pending | Provide graph backend through sibling `core/rag_graph`. |
| `rag-query-modes`, `rag-fusion-layer` | pending | Implement mode routing and provenance-preserving fusion. |
| `rag-context-wire` | pending | Call retrieval through the named `ContextAssembler.assemble()` boundary before agent/provider invocation. |

1. Normalize current vector backend/API types and implement pgvector/cache
   behavior before adding graph-mode dispatch.
2. Add graph/hybrid/auto routing plus deterministic fusion and provenance.
3. Integrate assembled retrieval evidence into memory and agent execution
   through `context_assembler.py`, preserving failure and token-budget policy.
4. Validate authorization, pgvector fixture retrieval, cache invalidation,
   each retrieval mode, fused ranking/provenance, assembler token trimming,
   provider switching, and unavailable-backend fallback.
