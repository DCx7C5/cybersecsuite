# @skills — Skill Registry & Execution

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

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Purpose

- Define and register skills (reusable task templates)
- Manage skill versions and dependencies
- Execute skills with parameter binding
- Support skill composition and chaining
- Handle skill result processing

---

## Implementation Checklist

- [ ] Skill definition and schema
- [ ] Skill registry
- [ ] Skill execution engine
- [ ] Parameter binding and validation
- [ ] Skill composition support
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/skills/__init__.py
"""Skill registry and execution."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .registry import SkillRegistry

__all__ = ['SkillRegistry']
```

---

**Status**: 🔴 Priority (Medium) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

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
