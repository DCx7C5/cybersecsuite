# @cache — Unified Caching Layer (L1-L4)

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

- [ ] Implement base cache interface with async/await support
- [ ] Implement L1 backend (asyncio.Cache)
- [ ] Implement L2 backend (aioredis)
- [ ] Implement L3 backend (asyncpg)
- [ ] Implement L4 backend (aiosqlite)
- [ ] Add logger initialization in `__init__.py`

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
