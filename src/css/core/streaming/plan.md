# @streaming — Streaming & Real-time Processing

> **MOVED TO CORE**: Originally `core/streaming/`, now at `src/css/core/streaming/`
> Reflects infrastructure nature of streaming/real-time processing.

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.modules.events` | → consumes | Stream events via @events HookRegistry (fire-and-forget) |

---

## Current State

✅ **Active** — QueryExecutor updated to use AgentExecutor → HttpProviderAdapter.
Claude SDK hardcode removed — provider-agnostic execution.

---

## Purpose

- Manage WebSocket connections for real-time updates
- Stream events and results as they occur
- Handle connection lifecycle (connect, disconnect, reconnect)
- Support backpressure and flow control
- Integrate with event system for streaming hooks

---

## Implementation Checklist

- [ ] WebSocket connection management
- [ ] Event streaming pipeline
- [ ] Backpressure handling
- [ ] Client lifecycle management
- [ ] Stream filtering and transformation
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/core/streaming/__init__.py
"""Streaming and real-time processing."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import StreamManager

__all__ = ['StreamManager']
```

---

**Status**: 🟢 Priority (Medium) | **Last Updated**: 2026-05-05
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

---

## Phase 15 — Decouple from @scopes

**Todo**: `streaming-decouple-from-scopes`

`options_manager.py` currently imports `ScopeLevel` from the `@scopes` module (which is deleted in Phase 15). It must be replaced with a local enum:

```python
# css/core/streaming/options_manager.py
class ConfigLayer(str, Enum):
    """Local replacement for ScopeLevel — streaming config granularity only."""
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"
```

- Do NOT import from `css.modules.scopes` after this change
- `ConfigLayer` lives only in `options_manager.py` — not shared/exported
- Dependency on `@scopes` module is completely removed

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
