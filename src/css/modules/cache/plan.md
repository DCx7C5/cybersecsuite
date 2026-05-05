# @cache — KV Caching Layer

> ⚠️ **MOVED TO `core/cache/`** — This module is infrastructure, not business logic.
> Active location: `src/css/core/cache/`
> Todo tracking: `cache-move-to-core` in session.db (Phase 3)
> This plan.md remains as a redirect until the move is complete.

---

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| *(fill in module-specific relationships)* | | |

---

## Current State

🟡 **Partial Implementation** (L1-L4 backends implemented; orchestration/wiring still pending)

**Files**:
- `base.py` — Base interface + L1/L2/L3/L4 backends + decorator
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

## L1-L4 Architecture

```
L1 (Hot):      In-memory asyncio.Cache (<1ms) — orchestrator-local
               ↓ [miss]
L2 (Warm):     Redis (1-10ms) — shared, multi-orchestrator
               ↓ [down]
L3 (Cold):     PostgreSQL (10-50ms) — persistent, auditable
               ↓ [down]
L4 (Archive):  Disk SQLite (50-500ms) — fallback when all above fail
```

---

## Implementation Checklist

- [x] Implement base cache interface with async/await support
- [x] Implement L1 backend (asyncio.Cache) — L1MemoryCache class
- [x] Implement L2 backend (aioredis) — L2RedisCache class
- [x] Implement L3 backend (PostgreSQL) — `L3PostgresCache` via Tortoise ORM
- [x] Implement L4 backend (aiosqlite) — `L4SQLiteCache` archive fallback
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
# src/css/modules/cache/__init__.py
"""Unified L1-L4 caching layer."""

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
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

## Audit (2026-05-04)

**Status**: TODO `db-fix-index-tuple-syntax` synchronized
**Changes**:
- Converted `CacheEntryModel.Meta.indexes` to `models.Index(fields=["namespace", "key"])`

---

## Prompt Caching (L5 — Provider-Native)

L5 sits above the L1-L4 cache stack and is handled at the provider SDK level, not in `@cache`.

| Provider | Caching | Implementation |
|----------|---------|----------------|
| Anthropic | Native `cache_control` param (up to 90% savings) | In `api_services/anthropic/` wrapper |
| OpenAI | Automatic server-side (no params needed) | Nothing to do |
| Gemini | Automatic server-side (no params needed) | Nothing to do |
| All others | No native caching | `@cache` L4 semantic cache is the fallback |

- `@cache` module's role: provide **L4 semantic cache** for providers WITHOUT native prompt caching
- `@cache` exposes `CacheablePrompt` type that provider wrappers can mark for semantic matching
- L4 uses Redis + semantic similarity (see `@semantic-token-caching` skill for strategy)

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
