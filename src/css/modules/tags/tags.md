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

## Canonical Tag Junction Pattern

**Reference**: See `.plan/tag-junction-naming-standard.md` for full specification.

All models that are taggable MUST create an M2M junction following this canonical pattern:

```python
from datetime import datetime
from typing import cast

import msgspec
from tortoise import fields, models

from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin


# 1. Domain value type (frozen, kw_only, immutable)
class <Entity>TagInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for <entity>/tag relation."""

    id: int
    <entity>_id: int  # Snake_case FK shadow field name
    tag_id: int
    created_at: datetime
    updated_at: datetime


# 2. ORM model with full domain conversion
class <Entity>Tag(BaseModel, TimestampMixin):
    """M2M junction table linking <Entity> to Tag."""

    # FK to entity model (always singular: model -> FK)
    <entity> = fields.ForeignKeyField(
        "models.<Entity>",
        related_name="tags_m2m",  # Always tags_m2m on entity side
    )
    # FK to Tag model
    tag = fields.ForeignKeyField(
        "models.Tag",
        related_name="<entities>",  # Plural: refers to collection of entities
    )

    def to_domain(self) -> <Entity>TagInfo:
        """Convert ORM model to domain value type."""
        <entity>_id = cast(int, getattr(self, "<entity>_id"))
        tag_id = cast(int, getattr(self, "tag_id"))
        return <Entity>TagInfo(
            id=self.id,
            <entity>_id=<entity>_id,
            tag_id=tag_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: <Entity>TagInfo) -> "<Entity>Tag":
        """Create ORM model from domain value type."""
        return cls(
            id=info.id,
            <entity>_id=info.<entity>_id,
            tag_id=info.tag_id,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "<entity>_tag"
        table_description = "M2M junction between <Entity> and Tag"
        unique_together = (
            ("<entity>_id", "tag_id"),
        )
        indexes = (
            models.Index(fields=["<entity>_id", "tag_id"]),  # Forward lookup
            models.Index(fields=["tag_id", "<entity>_id"]),  # Reverse lookup
        )
```

**Key invariants**:
- Class name: `<Entity>Tag` (singular, never plural `<Entity>Tags`)
- Value type: `<Entity>TagInfo` (frozen msgspec.Struct)
- Inheritance: Always `BaseModel + TimestampMixin` (no manual DatetimeField)
- Related name on entity: Always `tags_m2m` (uniformity across all taggable models)
- Related name on Tag: `<entities>` (plural, referring to the collection)
- Meta.table: Snake_case `<entity>_tag`
- Meta.unique_together: Tuple format, uses FK ID names
- Meta.indexes: **Always symmetric pair** for bidirectional query performance

---

**Status**: 🔴 Priority (Low) | **Last Updated**: 2026-05-26
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
