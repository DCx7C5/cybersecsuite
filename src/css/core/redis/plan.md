# core/redis — Redis-backed Messaging Infrastructure

**Location**: `src/css/core/redis/`  
**Status**: ✅ Implemented (3 files) | 🟡 from __future__ + dataclass patterns need cleanup (Phase 3)

---

## Purpose

Inter-entity messaging over Redis pub/sub. Lives in `core/` — consumed by agents, skills, memory, and any module that needs async message passing.

---

## Files

| File | Class | Status |
|------|-------|--------|
| `messaging.py` | `Message` (Pydantic BaseModel) | ✅ Done |
| `dispatcher.py` | `MessageDispatcher` — pub/sub via `redis.asyncio` | ✅ Done |
| `communicator.py` | `RedisCommunicator` — implements `BaseCommunicator` | ✅ Done |

---

## Integration Points

| Consumer | What it uses |
|----------|-------------|
| `modules/agents/` | `RedisCommunicator` for agent ↔ agent messaging |
| `modules/memory/` | `MessageDispatcher` for memory event broadcasting |
| `core/cache/` | Separate Redis connection pool (not this module) |

---

## Known Debt

- All 3 files use forbidden `from __future__ import annotations` — tracked as Phase 3 cleanup
- `communicator.py` uses `@dataclass` — migrate to `msgspec.Struct` on next touch (Phase 6 P1)
- `messaging.py` uses Pydantic `BaseModel` — acceptable for message wire format only
