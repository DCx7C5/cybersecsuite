# @cache — KV Caching Layer

> ⚠️ **MOVED TO `core/cache/`** — This module is infrastructure, not business logic.
> Active location: `src/css/core/cache/`
> Todo tracking: `cache-move-to-core` in session.db (Phase 3)
> Move completed. `src/css/modules/cache/` no longer exists.

---

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable cache specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.redis` | → consumes | L2 hot distributed-cache backend. |
| `css.core.prompt_cache` | ← consumed by | Prompt-response caching shares cache infrastructure without owning general policy. |
| `css.core.settings` | ← consumed by | Runtime configuration caching and invalidation. |
| `css.core.marketplace` | ← consumed by | Catalog/listing caches. |
| `css.core.memory` / retrieval owners | ← consumed by | Memory and retrieval-result cache paths where provenance-aware invalidation exists. |

---

## Current State

🟡 **Partial Implementation** (L1-L3 backends implemented; orchestration/wiring still pending)

**Files**:
- `base.py` — Base interface + L1/L2/L3 backends + decorator
- `models.py` — Runtime + ORM cache models
- `exceptions.py` — Custom cache exceptions
- `__init__.py` — Public exports

---

## Purpose

- Provide transparent caching across orchestrator processes
- Integrate with docker-compose services (Redis, PostgreSQL, Disk)
- Support deterministic key generation (Anthropic SDK pattern)
- Handle TTL-based eviction (LLM: 30d, KB: session-lifetime, tasks: phase+7d)
- Support encryption & compression (gzip)

---

## L1-L3 Architecture

```
L1 (Hot):      In-memory asyncio.Cache (<1ms) — orchestrator-local
               ↓ [miss]
L2 (Warm):     Redis (1-10ms) — shared, multi-orchestrator
               ↓ [down]
L3 (Cold):     PostgreSQL (10-50ms) — persistent, auditable
               ↓ [down]
```

---

## Implementation Checklist

- [x] Implement base cache interface with async/await support
- [x] Implement L1 backend (asyncio.Cache) — L1MemoryCache class
- [x] Implement L2 backend (`redis.asyncio`) — L2RedisCache class
- [x] Implement L3 backend (PostgreSQL) — `L3PostgresCache` via Tortoise ORM
- [x] L4 SQLite backend (`L4SQLiteCache`) removed from runtime
- [x] Add logger initialization in `__init__.py`

**Completed (Phase 2 Foundation)**:
✅ CacheBackend abstract base class
✅ L1MemoryCache with TTL support, eviction, stats
✅ L2RedisCache with lazy connection, namespace support
✅ CacheDecorator for async function result caching
✅ CacheEntry and CacheStats models
✅ Exception hierarchy (CacheNotFoundError, CacheExecutionError, CacheSerializationError)
✅ Module exports and logging

---

## Module Pattern

```python
# src/css/core/cache/__init__.py
"""Unified L1-L3 caching layer."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .base import CacheBackend
from .exceptions import CacheError

__all__ = ['CacheBackend', 'CacheError']
```

---

**Status**: 🔴 Priority (High) | **Last Updated**: 2026-05-04
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: This historical audit predates the `.plan/` whitelist; current cache ownership and remediation are tracked in this owner document and `.plan/session.db`.

## Audit (2026-05-04)

**Status**: TODO `db-fix-index-tuple-syntax` synchronized
**Changes**:
- Converted `CacheEntryModel.Meta.indexes` to `models.Index(fields=["namespace", "key"])`

---

## Prompt Caching (L5 — Provider-Native)

L5 sits above the L1-L3 cache stack and is handled at the provider SDK level, not in `@cache`.

| Provider | Caching | Implementation |
|----------|---------|----------------|
| Anthropic | Native `cache_control` param (up to 90% savings) | In `api_services/anthropic/` wrapper |
| OpenAI | Automatic server-side (no params needed) | Nothing to do |
| Gemini | Automatic server-side (no params needed) | Nothing to do |
| All others | No native caching | `@cache` semantic cache is the fallback |

- `@cache` module's role: provide semantic cache for providers WITHOUT native prompt caching
- `@cache` exposes `CacheablePrompt` type that provider wrappers can mark for semantic matching
- Semantic cache uses Redis + similarity matching (see `@semantic-token-caching` skill for strategy)

---

## 🔄 Sync Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
>
> - This file defines the implementation contract, not completion state.
> - Update tracker state as required by `.plan/rules.md`.
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
