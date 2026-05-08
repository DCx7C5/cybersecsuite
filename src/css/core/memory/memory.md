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
| `types.py` | `MemoryEntry`, `MemorySnapshot` value types |
| `enums.py` | `MemoryTier`, `MemoryScope`, `MemoryEntryKind` |
| `exceptions.py` | Memory exception hierarchy |
| `models.py` | `MemoryEntryRecord`, `MemorySnapshotRecord` |
| `context_window.py` | Token-budgeted rolling context window |
| `session_store.py` | Redis/PostgreSQL-backed session persistence |
| `agent_memory.py` | Per-agent episodic memory helper |
| `__init__.py` | Public exports |

## Compatibility

Legacy module package has been fully removed.

## Integration Role

- `core/memory` is the meeting point between live conversation state and retrieval.
- Phase 20 `rag-context-wire` makes memory-backed `ContextAssembler` a primary caller of `core/vector_rag`.
- Phase 21 `triage-memory-tagger` attaches semantic tags to stored entries after `store()`.
- Phase 27 `graph-session-flow` reads memory-backed conversation turns to build session graphs.

Memory remains source-of-truth state; retrieval, triage, and graph views consume it but do not replace it.
