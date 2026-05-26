# @tags — Tag Management & Classification

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable tag-management specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.marketplace` | ← consumed by | Marketplace item classification/filtering junctions. |
| `css.core.models` | ← consumed by | Model metadata tag filtering when runtime wiring is complete. |
| `css.modules.skills` / `css.core.tools` | ← consumed by | Skill/tool classification and discovery. |
| `css.core.rag_vector` | ← consumed by | Retrieval metadata filtering; tags are classification, not hierarchy. |

---

## Current State

🟡 **Partial Implementation** (5-file pattern complete; manager + endpoints wired)

---

## Purpose

- Define tag classification categories and metadata facets
- Assign tags to resources (tasks, findings, projects)
- Support tag-based searching and filtering
- Manage tag autocomplete and suggestions
- Handle tag normalization and conflicts

---

## Implementation Checklist

- [x] Tag classification schema (non-navigation)
- [x] Tag assignment storage
- [x] Tag search and filtering
- [x] Tag suggestions and autocomplete
- [x] Tag conflict resolution
- [x] Add logger initialization in `__init__.py`
- [x] Marketplace tag relations resolve item identity via `MarketplaceItem.slug`
- [x] Tag manager is ORM-backed (no in-memory tag dict cache)
- [x] Tag manager/model imports use lazy-safe structure to avoid circular init failures

---

## Phase 40 Lane E Scope Freeze (`db40-lane-tagging`)

Tagging is a **classification/filter/search/policy metadata** surface.
It is **not** a menu, tree, or navigation hierarchy owner.

Execution order for Lane E child todos:
1. `db40-taggable-entity-inventory`
2. `db40-tag-junction-naming-standard`
3. `db40-tag-junction-meta-backfill`
4. `db40-tagging-db-concept`
5. `db40-llmmodel-tag-runtime-wire`

Owned write surface for this lane:
- `src/css/modules/tags/*`
- `src/css/core/db/models/llm_models.py`
- `src/css/core/db/models/marketplace.py`
- `src/css/modules/tools/models.py`
- `src/css/core/tools/models.py`

Out-of-scope for Lane E: menu/tree/navigation modeling and unrelated model cleanup.

---

## Module Pattern

```python
# src/css/modules/tags/__init__.py
"""Tag management and classification."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import TagManager

__all__ = ['TagManager']
```

---

**Status**: 🔴 Priority (Low) | **Last Updated**: 2026-05-09
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain tag implementation detail in this local document.

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
