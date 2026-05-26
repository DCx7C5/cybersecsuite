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

## Canonical Tagging Concept (Phase 40)

**Defined**: 2026-05-26 (db40-tagging-db-concept)

### Definition: Shared vs. Domain-Local Tags

**Canonical pattern (shared Tag ORM)**: 
- `Tag` table stores reusable classification taxonomy (independent, persistent)
- `<Entity>Tag` M2M junctions attach tags to taggable entities
- Example: `LLMModelTag` links `LLMModel` rows to `Tag` rows (N:M relationship)
- **Purpose**: Classification, filtering, search, discovery, policy metadata
- **Scope**: Shared taxonomy across multiple entity types; enables cross-domain filtering

**Domain-local pattern (JSONField or dedicated table)**:
- Tags are stored as JSON array on the entity or in a domain-specific table
- Example: `SkillDefinitionModel.tags` JSONField (unstructured list of strings)
- **Purpose**: Local classification within a single domain; doesn't need cross-entity sharing
- **Scope**: Domain-specific, often with different semantics than shared taxonomy

### Architectural Boundary (CRITICAL)

**Tags do NOT own**:
- ❌ URLs or routing paths
- ❌ Breadcrumbs or hierarchical navigation
- ❌ Sidebar placement or menu structure
- ❌ Any tree/hierarchy semantics

**Tags are ONLY classification/filter/search/policy metadata**. Navigation hierarchy is owned by:
- `MenuItem` (navigation tree, menu partitioning)
- Module-specific routers and endpoints
- Frontend URL structure

---

## Current Tagging Patterns in Codebase

### Pattern 1: Shared Tags with M2M Junctions (Canonical)

**Current implementations** (Phase 40 Lane E):
- `LLMModel` + `LLMModelTag` — Models classified by capability, provider tier
- `MarketplaceItem` + `MarketplaceItemTag` — Marketplace items discoverable by category
- `HybridToolDefinition` + `HybridToolDefinitionTag` — Tools classified by language, composition
- `SkillDefinitionModel` + `SkillDefinitionModelTag` — Skills classified by category/level (NEW in Lane E)

**Meta pattern**: All follow canonical structure in
[`tag-junction-naming-standard.md`](tag-junction-naming-standard.md).

**When to use**: 
- ✓ Entity is discoverable across multiple interfaces
- ✓ Tags should be queryable across entities ("find all items tagged with 'vision-capable'")
- ✓ Tags represent stable, domain-independent classifications
- ✓ Need cross-cutting filtering/policy behavior

---

### Pattern 2: JSON Array Tags (Domain-local, unstructured)

**Current implementations**:

| Model | Location | Reason | Status |
|-------|----------|--------|--------|
| `KnowledgeDocument` | `src/css/core/rag_vector/models.py` | RAG-specific tagging for retrieval metadata | KEEP (domain-specific semantics) |
| `SkillDefinitionModel` | `src/css/modules/skills/models.py` | Inline skill metadata (pre-Phase 40) | MIXED (has both JSONField and M2M now) |
| `Evidence` | `src/css/modules/evidence/models.py` | Incident classification (incident_type, severity) | DEFER (decision needed) |
| `ThreatIntel` | `src/css/modules/threat_intel/models.py` | Threat actor classification | DEFER (decision needed) |

**When to use**: 
- ✓ Tags are local to one entity type
- ✓ Tags have domain-specific semantics (not cross-cutting)
- ✓ Performance matters more than query flexibility
- ✓ Unstructured/evolving classification (not a stable taxonomy)

---

### Pattern 3: Domain-Specific Tag Tables

**Current implementations**:

| Model | Location | Purpose | Related To | Status |
|-------|----------|---------|------------|--------|
| `KnowledgeTag` | `src/css/core/rag_vector/models.py` | RAG knowledge base tags | `KnowledgeDocument` (1:N) | KEEP (domain-specific with retrieval semantics) |
| `EvidenceTagging` | `src/css/modules/evidence/models.py` | Evidence classification audit trail | `Evidence` (M:M via association) | KEEP (audit/evidence context) |

**When to use**:
- ✓ Tags have domain-specific structure or metadata (not just strings)
- ✓ Need audit trail, timestamps, or other context on the tagging relationship
- ✓ Domain has specialized query semantics (e.g., RAG retrieval, evidence chains)

---

## Entity-to-Strategy Decision Table

| Entity | Current Pattern | Proposed Pattern | Rationale | Priority |
|--------|-----------------|------------------|-----------|----------|
| **LLMModel** | Canonical (M2M) | ✓ Keep canonical | Cross-cutting discovery, runtime queries | ✓ Done (Phase 40) |
| **MarketplaceItem** | Canonical (M2M) | ✓ Keep canonical | Marketplace filtering, user discovery | ✓ Done (Phase 40) |
| **HybridToolDefinition** | Canonical (M2M) | ✓ Keep canonical | Tool composition, runtime selection | ✓ Done (Phase 40) |
| **SkillDefinitionModel** | JSON array + M2M | Migrate to M2M only (remove JSONField) | Align with tools; enable skill discovery/filtering | 🟡 Phase 40 Lane E |
| **KnowledgeDocument** | JSON array | ✓ Keep JSON (RAG context) | RAG retrieval semantics differ from general tags; no cross-entity querying needed | Phase 42+ |
| **Evidence** | JSON array | Candidate for canonical M2M | Incident classification is cross-cutting policy concern; could benefit from shared taxonomy | 🟡 Defer to Phase 42 |
| **ThreatIntel** | JSON array | Keep JSON or create domain table | Threat intelligence has specialized semantics; evaluate in security/intel lane | 🟡 Defer to Phase 42+ |

---

## Canonical Schema Reference

**Shared Tag Taxonomy** (`Tag` table):
- Single authority for classification taxonomy (names, descriptions, colors, hierarchy)
- Owned by `src/css/modules/tags/models.py`
- Imported and referenced by all taggable entity junctions

**M2M Junction pattern** (for `<Entity>Tag`):
- **Requirements**: `BaseModel + TimestampMixin`, `to_domain/from_domain`, symmetric indexes
- **Reference**: [`tag-junction-naming-standard.md`](tag-junction-naming-standard.md)
  (canonical pattern template in this owner directory)
- **Foreign keys**: One to entity, one to `Tag`
- **Related names**: `tags_m2m` (on entity), `<entities>` (on Tag)

**Domain-local alternatives**:
- JSONField for unstructured, non-queryable tags (cache, UI state, transient data)
- Domain-specific tables for tags with audit/context (KnowledgeTag, EvidenceTagging)
- Never mix canonical M2M with JSONField on the same entity (choose one pattern)

---

## Implementation Guidance

### For New Taggable Entities

1. **Assess if shared tags apply**:
   - Will this entity be queried/filtered across domains?
   - Is the classification stable and reusable?
   - Does the entity appear in multiple discovery interfaces?
   - If **ANY yes**: Use canonical M2M pattern

2. **Follow canonical junction pattern**:
   - Copy template from `src/css/modules/tags/tags.md`
   - Name class `<Entity>Tag`, value type `<Entity>TagInfo`
   - Inherit from `BaseModel + TimestampMixin`
   - Implement `to_domain/from_domain`
   - Add symmetric dual indexes

3. **If domain-local tags**:
   - Document **why** shared tags don't apply
   - Use JSONField only if truly unstructured/non-queryable
   - Consider domain-specific table if audit/context needed

### For Existing Entities with JSON Tags

- **SkillDefinitionModel**: Remove `tags` JSONField once M2M junction is wired (Phase 40 Lane E)
- **Evidence**: Migrate to canonical M2M in Phase 42 security lane (candidate for shared incident taxonomy)
- **ThreatIntel**: Evaluate in Phase 42+ (may keep domain-local or create specialized threat taxonomy)
- **KnowledgeDocument**: Keep JSON tags (RAG-specific retrieval semantics incompatible with general taxonomy)

---

## Boundary Enforcement

**Tags are NOT**:
- Navigation hierarchy (that's MenuItem)
- Organizational structure (that's Scope/Account/Team)
- URL routing or page structure
- Breadcrumb generation or menu placement

**When documentation or code mixes tags with menu/tree concerns**:
- Explicitly separate the concepts in code
- Use `MenuItem` for navigation, `Tag` for filtering
- File an issue if a design conflates the two



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

**Reference**: See
[`tag-junction-naming-standard.md`](tag-junction-naming-standard.md) for the
full specification.

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
