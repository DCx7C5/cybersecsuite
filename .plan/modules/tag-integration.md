# Tag Integration Across Modules

**Status**: 🔵 Planning  
**Location**: `src/css/modules/tags/` + cross-module M2M  
**Updated**: 2026-05-03  
**Total Todos**: 26

---

## Overview

Create Many-to-Many relationships between **Tag** model and 6 core entities:
- MarketplaceItem (replace JSONField)
- HybridToolDefinition (replace JSONField)  
- PermissionGrant (security classification)
- ModelMetadata (model categorization)
- CacheEntry (cache tagging)
- TeamModel (team classification)

---

## Module Tag Integration Checklist

| Module | Model | Current | Target | Status |
|--------|-------|---------|--------|--------|
| marketplace | MarketplaceItem | `tags: JSONField` | M2M | ⚠️ TODO |
| tools | HybridToolDefinition | `tags: JSONField` | M2M | ⚠️ TODO |
| permissions | PermissionGrant | None | M2M | ⚠️ TODO |
| llm_models | ModelMetadata | None | M2M | ⚠️ TODO |
| cache | CacheEntry | None | M2M | ⚠️ TODO |
| teams | TeamModel | None | M2M | ⚠️ TODO |

---

## Implementation Plan

### Phase 1: M2M Junction Tables (6 todos)
- Create MarketplaceItemTag
- Create HybridToolDefinitionTag
- Create PermissionGrantTag
- Create ModelMetadataTag
- Create CacheEntryTag
- Create TeamTag

### Phase 2: Model Updates (6 todos)
- Update each model with reverse relations
- Remove JSONField tags from marketplace & tools

### Phase 3: Data Migration (2 todos)
- Migrate MarketplaceItem JSONField → M2M
- Migrate HybridToolDefinition JSONField → M2M

### Phase 4: Endpoints (3 todos)
- CRUD endpoints
- Entity+tag filtering
- Bulk tag assignment

### Phase 5: Documentation (5 todos)
- Update 4 module plan.md files
- Create architecture guide

---

## Success Criteria

✅ All 6 entities have Tag M2M relationships  
✅ JSONField tags migrated with no data loss  
✅ Tag filtering works across all entities  
✅ Bulk operations supported  
✅ All plans documented
