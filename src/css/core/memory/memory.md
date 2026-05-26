# core/memory — Working Memory & Session State

**Location**: `src/css/core/memory/`
**Status**: ✅ Canonical ownership in `core/memory/`

## Purpose

- Own working-memory structs, enums, and exceptions
- Persist memory entries and snapshots through Tortoise ORM models
- Provide context-window, session-store, and agent-memory primitives

## Files

| File | Contents |
|------|----------|
| `types.py` | `MemoryEntry`, `MemorySnapshot`, `MemoryQuery`, `MemoryListResult`, `MemoryDeleteRequest/Result`, `MemoryPolicyConfig` value types |
| `enums.py` | `MemoryTier` (HOT/WARM/COLD), `MemoryScope` (SESSION/AGENT/GLOBAL), `MemoryEntryKind` (NOTE/FACT/FINDING/PLAN/ARTIFACT/SNAPSHOT) |
| `exceptions.py` | `BaseMemoryException`, `MemoryNotFoundError`, `MemoryPersistenceError` |
| `../db/models/memory.py` | `MemoryEntryRecord`, `MemorySnapshotRecord` — canonical Tortoise ORM models with `to_struct()` |
| `contracts.py` | `MemoryStore`, `MemoryRetriever`, `MemoryPolicy` — Protocol interfaces |
| `context_window.py` | `ContextWindow` — token-budgeted rolling window with eviction tracking |
| `session_store.py` | `SessionStore` — hybrid Redis+PostgreSQL persistence |
| `agent_memory.py` | `AgentMemory` — per-agent episodic memory with checkpoint save/load |
| `service.py` | `MemoryService`, `DefaultMemoryPolicy` — service layer |
| `__init__.py` | Public exports |

## Key Classes

### AgentMemory (`agent_memory.py`)
Per-agent episodic memory combining three layers:
- **ContextWindow**: active message window with token budget
- **SessionStore**: persistent storage (Redis + PostgreSQL)
- **Episodic memory**: collection of memorable events/facts
- `add_episode(content, category, tags)` — record facts, events, insights, decisions
- `get_episodes(category, tags)` — filtered retrieval with eviction (max 100)
- `save_checkpoint(session_id)` — persist full context + episodes to store
- `load_checkpoint(session_id)` — restore previous state (Redis → PostgreSQL fallback)
- `get_summary()` — memory diagnostics (token counts, episode stats, storage status)

### SessionStore (`session_store.py`)
Hybrid session persistence:
- **Redis (hot)**: 24h TTL, fast reads/writes for active sessions
- **PostgreSQL (cold)**: Tortoise ORM `MemorySnapshotRecord` as durable fallback
- Load strategy: Redis first, auto-warm from PostgreSQL on miss
- `save_context(session_id, context)` → Redis + optional DB checkpoint
- `load_context(session_id)` → Redis → PostgreSQL fallback
- `checkpoint_to_db(session_id, context)` → durable snapshot
- `list_memory_entries(query)` → paginated, filtered memory listing
- `prune_expired_entries()` → TTL-based cleanup
- `list_active_sessions()` → enumerate Redis sessions
- `health_check()` → ping both Redis and PostgreSQL
- `refresh_session_ttl()` / `get_session_ttl()` → session lifetime management

### ContextWindow (`context_window.py`)
- Token-budgeted rolling message window
- Eviction when exceeding `max_tokens`
- Tracks evicted count for diagnostics

### MemoryService (`service.py`)
- `store(entry)` — persist entry with policy evaluation
- `retrieve(query)` — filtered memory query
- `evaluate(policy, entry)` — policy gating
- `delete(request)` — scoped deletion

### Models (`core/db/models/memory.py`)
- `MemoryEntryRecord` — ORM for individual memory entries with `to_struct()` bridge
- `MemorySnapshotRecord` — ORM for full-context snapshots

## Compatibility

Legacy module package has been fully removed.

## Integration Role

- `core/memory` is the meeting point between live conversation state and retrieval.
- `AgentMemory` bridges conversation context → persistent storage → episodic recall.
- `SessionStore` provides the Redis-first/PostgreSQL-fallback tiering that Phase 20 formalizes.
- Phase 20 `rag-context-wire` makes memory-backed `ContextAssembler` a primary caller of `core/rag_vector`.
- Phase 21 `triage-memory-tagger` attaches semantic tags to stored entries after `store()`.
- Phase 27 `graph-session-flow` reads memory-backed conversation turns to build session graphs.
- Prompt cache, retrieval cache, and Redis hot paths may accelerate memory access patterns, but `core/memory` remains the source-of-truth state layer.

Memory remains source-of-truth state; retrieval, triage, and graph views consume it but do not replace it.

## Phase 20 Execution Contract

Phase 20 formalizes memory that survives model and provider changes. Stored
entries remain provider-neutral; only context assembly converts them into an
adapter-specific request representation.

```text
agent turn
  -> retrieve scoped memory under a token budget
  -> assemble provider-neutral context plus retrieval evidence
  -> invoke selected model/provider
  -> store resulting entries
  -> asynchronously checkpoint/promote/compress as policy requires
```

### Storage and Retrieval Tiers

| Tier | Required behavior | Canonical owner |
|------|-------------------|-----------------|
| Hot | Redis-backed active-session window, TTL, token-budget eviction, resume warm-up. | `core/memory` |
| Cold | Durable PostgreSQL turns/snapshots with text search and bulk flush on lifecycle boundaries. | `core/memory` / DB models |
| Hybrid retrieval | Cross-session evidence retrieval, vector and graph search, caching, normalized fusion/rerank, and provenance preservation before model calls. | `core/rag_vector` and `core/rag_graph`, consumed by memory assembly. |

### Planned Surfaces

| Work area | Required outcome |
|-----------|------------------|
| Protocol and manager | Provider-neutral `MemoryEntry`/store contracts; manager handles warm-up, promotion, flush, eviction, and retrieval. |
| Context assembler | Convert selected memory/retrieval results for adapters while retaining source identifiers and token budgets. |
| Retrieval services | Use VectorRAG and GraphRAG for durable cross-session knowledge lookup; do not introduce an additional vault/projection planning layer. |
| Semantic/compression policy | pgvector-backed retrieval through an embedding-provider contract; compress aged conversation turns while preserving useful summaries and provenance. |
| Triage hook | Allow Phase 21 semantic tagging after memory writes without coupling memory state to triage routing state. |

### Critical Dependencies

| Dependency chain | Why it matters |
|------------------|----------------|
| Protocol -> persistence adapters -> manager/context assembler | Prevents provider-specific state from leaking into persisted memory. |
| Manager/context assembler -> agent and session lifecycle wiring | Ensures memory is retrieved/stored at stable execution boundaries. |
| Vector/graph backends -> fused retrieval -> context assembly | Makes evidence available before invocation with provenance intact. |

### Validation Requirements

- Prove a session can resume after switching providers without losing useful
  context or corrupting request formatting.
- Verify Redis loss/fallback to durable storage and lifecycle checkpointing.
- Validate retrieval evidence and compressed summaries retain provenance needed
  by reports, approvals, and audit views.

## Retrieval Package Placement Decision

The retrieval subsystems are currently present at `src/css/core/rag_vector/`
and `src/css/core/rag_graph/`. A later refactor may place them below
`src/css/core/memory/` to make the context-assembly ownership explicit.

Do not rename imports, routes, ORM registration, or docs to nonexistent nested
paths during documentation sanitization. First audit the executable dependency
surface, then perform the package move as a bounded source-code change with
tests and tracker updates.

## Executable Phase 20 Addendum (2026-05-26)

### Exact Files And Symbols

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/core/memory/types.py`, `src/css/core/memory/contracts.py` | Existing `MemoryEntry`, `MemoryQuery`, `MemoryStore`, `MemoryRetriever`, `MemoryPolicy`. |
| `src/css/core/memory/session_store.py` | Existing `SessionStore`; canonical ORM imports must resolve from `src/css/core/db/models/memory.py`. |
| `src/css/core/memory/service.py` | Existing `MemoryService`, `DefaultMemoryPolicy`; normalize model imports to the canonical DB owner when touched. |
| `src/css/core/memory/context_window.py`, `src/css/core/memory/agent_memory.py` | Existing `ContextWindow`, `AgentMemory` active-context/checkpoint behavior. |
| `src/css/core/memory/context_assembler.py` | Planned `ContextAssembler.assemble(entries, retrieval_results, token_budget)` owner for `mem-context-assembler` and `rag-context-wire`. |
| `src/css/core/rag_vector/retriever.py`, `src/css/core/rag_graph/backend.py` | Retrieval providers consumed by context assembly; GraphRAG backend remains planned. |

### Live Todo Map And Work Order

| Pending todo group | Status | Ordered contract |
|--------------------|--------|------------------|
| `mem-protocol-struct`, `mem-protocol-interface`, `mem-module-files` | pending | Reconcile existing values/protocols/exports; do not duplicate implemented contracts. |
| `mem-redis-adapter`, `mem-pg-model`, `mem-pg-adapter`, `mem-manager`, `bug-fix-sessionstore-dataloss`, `bug-fix-sessionstore-race` | pending | Fix persistence correctness before lifecycle integration. |
| `mem-context-assembler`, `memory-context-assembler-integration`, `rag-context-wire` | pending | Implement and consume `ContextAssembler.assemble()` before model calls, under token/provenance constraints. |
| `mem-agent-wire`, `mem-session-wire`, `mem-memory-tagger-hook` | pending | Integrate at stable turn/lifecycle/write boundaries after state correctness. |
| `memory-*` rollout/telemetry/tests rows | pending | Add failure policy, parity, startup, metrics, and rollout evidence after core behavior is verified. |

1. Normalize canonical memory model imports and repair storage loss/race
   behavior before adding new adapters or lifecycle wiring.
2. Implement the provider-neutral manager/context assembler and connect
   vector/graph retrieval only through the named `assemble()` boundary.
3. Add session/agent/tagging integrations and failure/telemetry/rollout tests
   after persistence and assembly are stable.
4. Validate Redis-loss fallback, concurrent writes, provider switch survival,
   retrieval provenance/token trimming, canonical imports, and dependency
   direction between memory, retrieval, triage, and agents.
