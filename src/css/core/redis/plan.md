# core/redis — Redis-backed Messaging Infrastructure

**Location**: `src/css/core/redis/`
**Status**: ✅ Implemented (3 files) | ✅ Phase 3 cleanup applied (`__future__` removed, dataclass migrated)

---

## Purpose

Inter-entity messaging over Redis pub/sub. Lives in `core/` — consumed by agents, skills, memory, and any module that needs async message passing.

---

## Files

| File | Class | Status |
|------|-------|--------|
| `messaging.py` | `Message` (`msgspec.Struct`) | ✅ Done |
| `dispatcher.py` | `MessageDispatcher` — pub/sub via `redis.asyncio` | ✅ Done |
| `communicator.py` | `RedisCommunicator` — implements `BaseCommunicator` | ✅ Done |

---

## Integration Points

| Consumer | What it uses |
|----------|-------------|
| `modules/agents/` | `RedisCommunicator` for agent ↔ agent messaging |
| `css.core.memory` | `MessageDispatcher` for memory event broadcasting |
| `core/cache/` | Separate Redis connection pool (not this module) |

---

## Type Boundary

- `messaging.py` encodes and decodes the wire message through
  `msgspec.Struct` and `msgspec.msgpack`; it does not define Pydantic models.

## Validation Contract

- Verify publish/subscribe round trips and clean cancellation on shutdown.
- Verify Redis outage errors are typed and do not silently drop required
  persisted state from memory/cache callers.
- Keep KV cache policy in `core/cache`; this package owns messaging transport.
