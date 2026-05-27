# @skills — Skill Registry & Execution

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable skill-registry specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.marketplace` | → integrates | Publish/install skill marketplace items through the bridge surface. |
| `css.core.tools` | → consumes | Skill execution invokes registered tool contracts. |
| `css.modules.agents` | ← consumed by | Agents select and execute installed skills. |
| `css.core.events` | → emits | Skill installation/execution lifecycle events when wired. |

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Marketplace Integration Surface

- `marketplace_bridge.py` maps `Skill` objects to marketplace items (`MarketplaceItemType.skill`) and keeps marketplace cache entries in sync after create/update.
- Bridge helpers:
  - `skill_to_marketplace_item(skill)`
  - `get_skill_marketplace_item(skill_id)`
- Current skill source stores structured definitions and has no Markdown file
  loader that injects content into an LLM context. SecureMD prompt-ingestion
  work must not invent a skill execution path; record a separate todo if a
  Markdown-backed skill loader is later introduced.

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

**Note**: `SkillRegistry` (in `registry.py`) uses `AsyncSafeSingletonMeta` for async-safe singleton pattern.

```python
# src/css/modules/skills/__init__.py
"""Skill registry and execution."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .registry import SkillRegistry

__all__ = ['SkillRegistry']
```

**Registry Classes Using AsyncSafeSingletonMeta**:
- `BaseRegistry` (`core/types/base_registry.py`) - metaclass=AsyncSafeSingletonMeta`
- `ModelRegistry` (`core/models/registry.py`) - inherits BaseRegistry`
- `MarketplaceItemRegistry` (`core/marketplace/registry.py`) - inherits BaseRegistry`
- `BaseToolRegistry` (`core/tools/base.py`) - metaclass=AsyncSafeSingletonMeta`
- `ToolRegistry` (`modules/tools/registry.py`) - inherits BaseToolRegistry`
- `ProviderRegistry` (`api_services/registry.py`) - metaclass=AsyncSafeSingletonMeta`
- `SkillRegistry` (`modules/skills/registry.py`) - metaclass=AsyncSafeSingletonMeta`
- `McpRuntimeRegistry` (`modules/mcps/registry.py`) - metaclass=AsyncSafeSingletonMeta`

---

**Status**: 🔴 Priority (Medium) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain skill implementation detail in this local document.

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
