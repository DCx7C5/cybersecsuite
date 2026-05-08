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
