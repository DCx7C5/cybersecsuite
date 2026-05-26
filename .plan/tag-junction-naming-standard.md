# Phase 40 Lane E - Tag Junction Naming & Meta Convention Standard (db40-tag-junction-naming-standard)

**Tracking authority**: `.plan/session.db` | **Status**: Complete | **Date**: 2026-05-26

---

## Executive Summary

Standardized naming conventions, Meta attribute structure, and domain value types across all M2M tag junction models.

Applied to:
- `LLMModelTag` (src/css/core/db/models/llm_models.py)
- `MarketplaceItemTag` (src/css/core/db/models/marketplace.py)
- `HybridToolDefinitionTag` (src/css/modules/tools/models.py)
- `SkillDefinitionModelTag` (src/css/modules/skills/models.py)

---

## Canonical Junction Naming Standard

All tag junction models MUST follow this pattern:

### 1. Class Naming
- **Format**: `<Entity>Tag` (always singular, never `<Entity>Tags`)
- **Examples**: `LLMModelTag`, `MarketplaceItemTag`, `HybridToolDefinitionTag`, `SkillDefinitionModelTag`

### 2. Domain Value Type Naming
- **Format**: `<Entity>TagInfo` msgspec.Struct (frozen, kw_only)
- **Required fields**:
  ```python
  id: int
  <entity>_id: int  # FK shadow field (snake_case from model name)
  tag_id: int
  created_at: datetime
  updated_at: datetime
  ```
- **Examples**:
  - `LLMModelTagInfo` with `llm_model_id`
  - `MarketplaceItemTagInfo` with `marketplace_item_id`
  - `HybridToolDefinitionTagInfo` with `hybrid_tool_id`
  - `SkillDefinitionModelTagInfo` with `skill_model_id`

### 3. Table Naming
- **Format**: snake_case `<model>_tag` (derived from entity)
- **Examples**: `llm_model_tag`, `marketplace_item_tag`, `hybrid_tool_tag`, `skill_definition_model_tag`

### 4. Related Name on Tag Model
- **Format**: `<models>` (plural, lowercase, referring to the collection of entity instances)
- **Examples**:
  - `Tag.llm_models` — the collection of LLM models with this tag
  - `Tag.marketplace_items` — the collection of marketplace items with this tag
  - `Tag.hybrid_tools` — the collection of hybrid tools with this tag
  - `Tag.skill_models` — the collection of skill models with this tag

### 5. Related Name on Entity Model
- **Standard**: Always `tags_m2m` (consistent across all entities for uniformity in queries)
- **Example**: `LLMModel.tags_m2m` always returns the M2M relation

---

## Meta Class Standard

All junction Meta classes MUST have:

```python
class Meta:  # type: ignore[reportIncompatibleVariableOverride]
    table = "<model>_tag"
    table_description = "M2M junction between <Entity> and Tag"
    unique_together = (
        ("<entity>_id", "tag_id"),
    )
    indexes = (
        Index(fields=["<entity>_id", "tag_id"]),
        Index(fields=["tag_id", "<entity>_id"]),  # Symmetric reverse index
    )
```

### Key Points:
- **table**: Derived from entity name (always snake_case `<model>_tag`)
- **table_description**: Descriptive format = "M2M junction between <Entity> and Tag"
- **unique_together**: Tuple format (not list), always uses FK ID field names (not FK field names)
- **indexes**: ALWAYS include both forward and reverse (symmetric) indexes for bidirectional query performance
  - Forward: `[<entity>_id, tag_id]` — optimizes "find all tags for this entity"
  - Reverse: `[tag_id, <entity>_id]` — optimizes "find all entities with this tag"

### Meta Attributes NOT to Use:
- ❌ `table_verbose` / `table_verbose_plural` — Use `table_description` only
- ❌ `unique_together = [(...)]` — Use tuple format `((...),)`
- ❌ Single index only — Always provide symmetric dual indexes

---

## Domain Conversion Standard

All junctions MUST implement `to_domain()` and `from_domain()`:

```python
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
```

### Key Points:
- Use `getattr(self, "<entity>_id")` with `cast(int, ...)` for FK shadow field access (Tortoise ORM creates these automatically)
- `to_domain()` includes all timestamps; `from_domain()` omits them (let ORM manage)
- Both methods are required for full domain → ORM ↔ ORM → domain round-trip capability

---

## Inheritance Standard

All junctions MUST use:

```python
class <Entity>Tag(BaseModel, TimestampMixin):
```

This ensures:
- Automatic `created_at` / `updated_at` fields via TimestampMixin
- No manual DatetimeField(auto_now_add=True) declarations
- Consistent audit trail across all junctions

---

## Applied Changes (Audit Results)

### Pre-Standard State:
1. **LLMModelTag** — Incorrect unique_together used field names instead of ID names
2. **MarketplaceItemTag** — Missing to_domain() type casting for FK shadow fields
3. **HybridToolDefinitionTag** — Missing to_domain/from_domain, no TimestampMixin, single index only
4. **SkillDefinitionModelTag** — Missing dual symmetric indexes, used list format

### Post-Standard State:
✓ All four junctions now conform to:
- Singular class naming (`<Entity>Tag`)
- Domain value types (`<Entity>TagInfo`)
- Consistent table names
- Correct unique_together with ID field names (tuple format)
- Symmetric dual indexes
- Full to_domain/from_domain implementation
- TimestampMixin for audit trails
- Standardized table_description

### Specific Fixes:
| Junction | Changes |
|----------|---------|
| LLMModelTag | `unique_together ("llm_model", "tag")` → `("llm_model_id", "tag_id")` |
| MarketplaceItemTag | Added `getattr()` cast pattern in to_domain(); removed table_verbose |
| HybridToolDefinitionTag | Added TimestampMixin, to_domain/from_domain, HybridToolDefinitionTagInfo, dual indexes |
| SkillDefinitionModelTag | Added reverse index, tuple format for Meta attributes |

---

## Type Checking Notes

All junctions now pass `basedpyright --project pyrightconfig.json`:
- FK shadow field access uses `getattr(self, "<entity>_id")` with `cast(int, ...)` for type safety
- No type: ignore annotations needed for FK access (getattr is type-safe pattern)
- msgspec.Struct info types are frozen and kw_only for immutability

---

## Next Steps

Lane E execution order continues:
1. ✓ `db40-taggable-entity-inventory` — Complete (4 models identified)
2. ✓ `db40-tag-junction-naming-standard` — **Complete (this document)**
3. `db40-tag-junction-meta-backfill` — Standardize Meta on all junctions (if any exist beyond these 4)
4. `db40-tagging-db-concept` — Define canonical tag category schema
5. `db40-llmmodel-tag-runtime-wire` — Wire tags into runtime queries/filtering

---

## Validation Checklist

- [x] All four junctions use singular `<Entity>Tag` naming
- [x] All have `<Entity>TagInfo` msgspec.Struct value types
- [x] All have consistent table naming (`<model>_tag`)
- [x] All use FK ID field names in unique_together (not field names)
- [x] All have symmetric dual indexes (forward + reverse)
- [x] All implement to_domain() and from_domain()
- [x] All use getattr() cast pattern for FK shadow field access
- [x] All inherit from BaseModel + TimestampMixin
- [x] All use tuple format for Meta.unique_together and Meta.indexes
- [x] All use table_description (no table_verbose)
- [x] Removed manual DatetimeField(auto_now_add=True) in favor of TimestampMixin

---

**Status**: ✓ Complete | **Owner**: Phase 40 Lane E (Tagging consolidation) | **Validated**: basedpyright --project pyrightconfig.json

