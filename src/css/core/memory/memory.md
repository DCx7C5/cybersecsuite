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
