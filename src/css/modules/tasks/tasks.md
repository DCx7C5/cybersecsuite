# @tasks — Task Management & Execution

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.events` | → consumes | `@instrument("command.{CommandName}")` — Phase 14 entry point 2 |

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Purpose

- Define task schemas and templates
- Schedule and queue tasks
- Manage task lifecycle (pending → running → completed)
- Execute tasks with proper error handling
- Collect and aggregate results

---

## Implementation Checklist

- [ ] Task definition and schema
- [ ] Task queue management
- [ ] Task execution engine
- [ ] Task lifecycle management
- [ ] Result collection and aggregation
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/tasks/__init__.py
"""Task management and execution."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .service import TaskService

__all__ = ['TaskService']
```

---

**Status**: 🔴 Priority (Critical) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/plan.md for current audit and phase status.

---

## Phase 14 — CommandBus Entry Point

CommandBus is **entry point 2 of 5** for the `@events` instrumentation system.

- Every task dispatched through `CommandBus` gets `@instrument("command.{CommandName}")`
- Example: `@instrument("command.TaskCommand")` for task dispatch
- Events fired: `command.TaskCommand.started`, `command.TaskCommand.completed`, `command.TaskCommand.failed`
- `correlation_id` ContextVar is inherited from the HTTP middleware entry point (entry point 1)

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
