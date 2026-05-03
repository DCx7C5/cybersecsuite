# @cache — Unified Caching Layer (L1-L4)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/cache/`

**Responsibility**: Multi-level cache fallback (Memory → Redis → PostgreSQL → Disk).

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

**Files**:
- `base.py` — Base cache interface (abstract methods)
- `exceptions.py` — Custom cache exceptions

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
- [ ] Implement L3 backend (asyncpg) — PostgreSQL backend (Phase 2.5)
- [ ] Implement L4 backend (aiosqlite) — SQLite archive (Phase 3)
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

**Status**: 🔴 Priority (High) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
