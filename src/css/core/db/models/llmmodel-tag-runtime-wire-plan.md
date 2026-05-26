# Phase 40 Lane E - LLMModel Tag Runtime Wire Implementation Plan

**Tracking authority**: `.plan/session.db` | **Status**: In progress | **Date**: 2026-05-26

---

## Overview

Final Lane E todo to wire `LLMModelTag` junction table into runtime model discovery and filtering.

**Objective**: Make LLM model tags accessible and usable in runtime queries, not just schema-level.

---

## Current State

- `LLMModelTag` M2M junction exists in schema ✓
- `Tag` taxonomy table exists ✓
- `LLMModel.tags_m2m` reverse relation configured ✓
- Runtime metadata (`ModelMetadata`, `ModelRegistry`) **does NOT expose tags** ✗

---

## Implementation Steps (Ordered)

### Step 1: Extend ModelMetadata Domain Type

**File**: `src/css/core/models/models.py`

**Changes**:
```python
class ModelMetadata(msgspec.Struct, frozen=True, kw_only=True):
    # ... existing fields ...
    
    # NEW: Tag-based classification for discovery/filtering
    tags: list[str] = msgspec.field(default_factory=list)  # Tag slugs
```

**Why**: Domain value type must carry tags for runtime callers to filter/search on tags.

---

### Step 2: Update LLMModel.to_metadata() Conversion

**File**: `src/css/core/db/models/llm_models.py`

**Changes**:
- Query prefetched tags via `self.tags_m2m` relation
- Extract tag slugs (NOT junction IDs)
- Pass to `ModelMetadata(tags=[...])`

**Pseudocode**:
```python
def to_metadata(self) -> ModelMetadata:
    # Prefetch tags if not already loaded
    tags = await self.tags_m2m.all()
    tag_slugs = [tag.slug for tag in tags]
    
    return ModelMetadata(
        id=self.name,
        # ... existing fields ...
        tags=tag_slugs,  # NEW
    )
```

**Challenge**: ORM prefetching; Tortoise `prefetch_related()` async flow

**Solution**: Pass tags explicitly or use ORM manager with prefetch built-in

---

### Step 3: Add Tag Query Helpers to LLMModelManager

**File**: `src/css/core/db/models/llm_models.py`

**New methods on `LLMModelManager`**:

```python
async def by_tag(self, tag_slug: str) -> list[LLMModel]:
    """Find all LLM models with a specific tag."""
    return await LLMModel.filter(
        tags_m2m__tag__slug=tag_slug,
        deprecated=False
    ).distinct().order_by("provider", "family", "name", "id")

async def by_tags(self, tag_slugs: list[str], match_all: bool = False) -> list[LLMModel]:
    """Find models matching tag filter.
    
    Args:
        tag_slugs: List of tag slugs to match
        match_all: If True, model must have ALL tags; if False, ANY tag suffices
    
    Returns: List of models
    """
    query = LLMModel.filter(deprecated=False)
    
    if match_all:
        # Model must have every tag in the list
        for slug in tag_slugs:
            query = query.filter(tags_m2m__tag__slug=slug)
    else:
        # Model must have at least one tag in the list
        query = query.filter(tags_m2m__tag__slug__in=tag_slugs)
    
    return await query.distinct().order_by("provider", "family", "name", "id")
```

**Validation**: Test with models that have 0, 1, N tags

---

### Step 4: Wire ModelRegistry Tag Filtering

**File**: `src/css/core/models/registry.py`

**Changes to `ModelRegistry` class**:

- Add optional `tag` and `tags` parameters to `list_models()` method
- Filter via manager if tags provided
- Preserve existing provider/capability filter precedence

**Pseudocode**:
```python
class ModelRegistry:
    async def list_models(
        self,
        provider: ModelProvider | None = None,
        capability: ModelCapability | None = None,
        tag: str | None = None,          # NEW
        tags: list[str] | None = None,   # NEW (match any)
        match_all_tags: bool = False,    # NEW
    ) -> list[ModelMetadata]:
        """List models with optional tag filtering."""
        
        query_results = []
        
        # 1. Load all DB models
        manager = LLMModelManager()
        models = await manager.active()
        
        # 2. Apply tag filter if provided
        if tag:
            models = await manager.by_tag(tag)
        elif tags:
            models = await manager.by_tags(tags, match_all=match_all_tags)
        
        # 3. Apply existing filters (provider, capability)
        if provider:
            models = [m for m in models if m.provider == provider.value]
        
        if capability:
            models = [m for m in models if capability in m.capability_members]
        
        # 4. Convert to metadata
        for model in models:
            query_results.append(model.to_metadata())
        
        return query_results
```

**Note**: Registry may cache models; ensure prefetch includes tags for cache hits

---

### Step 5: Wire Endpoint Consumer

**File**: `src/css/modules/llm_proxy/endpoints.py`

**Method**: Find and update `list_models()` or equivalent endpoint

**Changes**:
- Add optional query parameter: `?tag=<slug>` or `?tags=<slug1>,<slug2>`
- Call `registry.list_models(tag=tag, tags=tags)` instead of non-tag version
- Document in response: each model includes `tags: [...]` in metadata

**Example**:
```python
@router.get("/models")
async def list_models(
    provider: str | None = Query(None),
    capability: str | None = Query(None),
    tag: str | None = Query(None),  # NEW
    tags: str | None = Query(None),  # NEW (comma-separated)
) -> dict[str, Any]:
    """List available LLM models with optional filtering.
    
    Query parameters:
    - provider: Filter by provider (openai, anthropic, etc.)
    - capability: Filter by capability (vision, code, etc.)
    - tag: Filter models with specific tag (slug)
    - tags: Filter by multiple tags (comma-separated slugs; match any)
    """
    registry = get_model_registry()
    
    tag_list = tags.split(",") if tags else None
    models = await registry.list_models(
        provider=provider,
        capability=capability,
        tag=tag,
        tags=tag_list,
    )
    
    return {"models": [m.to_dict() for m in models]}
```

---

## Validation Checklist

### Code Quality
- [ ] `ruff check src/css/core/db/models/llm_models.py`
- [ ] `ruff check src/css/core/models/models.py`
- [ ] `ruff check src/css/core/models/registry.py`
- [ ] `ruff check src/css/modules/llm_proxy/endpoints.py`
- [ ] `basedpyright --project pyrightconfig.json src/css/core/models/`
- [ ] All type annotations match `ModelMetadata` and `LLMModelManager` contracts

### Runtime Testing
- [ ] Unit test: `LLMModelManager.by_tag(slug)` returns models with that tag
- [ ] Unit test: `LLMModelManager.by_tags(slugs, match_all=True)` returns models with ALL tags
- [ ] Unit test: `LLMModelManager.by_tags(slugs, match_all=False)` returns models with ANY tag
- [ ] Integration test: Endpoint `?tag=vision` filters and returns correct models
- [ ] Integration test: Endpoint `?tags=vision,code` returns models with either tag
- [ ] Endpoint returns models with populated `tags: [...]` in response

### Smoke Test
```bash
# After implementation, run:
.venv/bin/python -c "
from css.core.db.models.llm_models import LLMModel, LLMModelManager
from css.core.models.models import ModelMetadata
from css.core.models.registry import ModelRegistry

# 1. Check manager methods exist
mgr = LLMModelManager()
assert hasattr(mgr, 'by_tag'), 'Missing by_tag method'
assert hasattr(mgr, 'by_tags'), 'Missing by_tags method'

# 2. Check ModelMetadata has tags field
md = ModelMetadata(
    id='test', provider='openai', family='gpt',
    display_name='Test', context_window=100, max_output_tokens=50,
    tags=['vision', 'code']
)
assert md.tags == ['vision', 'code'], 'Tags field not working'

# 3. Check registry has tag params
reg = ModelRegistry()
assert 'tag' in reg.list_models.__code__.co_varnames, 'Missing tag param'
assert 'tags' in reg.list_models.__code__.co_varnames, 'Missing tags param'

print('✓ All smoke tests passed')
"
```

---

## Known Challenges

### 1. ORM Prefetching
- **Issue**: Tags must be prefetched for `to_metadata()` to work without N+1 queries
- **Solution**: Use `LLMModel.prefetch_related('tags_m2m__tag')` before calling `to_metadata()`
- **Alternative**: Load all tags in batch in manager query

### 2. Cache Invalidation
- **Issue**: ModelRegistry caches metadata; tag changes won't be reflected
- **Solution**: Include tag_id in cache key or bypass cache for tag queries
- **Approach**: Accept cache miss for tag-filtered queries; cache full list only

### 3. Case Sensitivity
- **Issue**: Tag slugs may be case-sensitive; user input may vary
- **Solution**: Normalize input slugs to lowercase; store tags in lowercase in DB

### 4. Query Performance
- **Issue**: M2M join + distinct may be slow with many models/tags
- **Solution**: Add composite index on (tag_id, llm_model_id) if not present
- **Current**: Indexes already in `LLMModelTag.Meta` ✓

---

## Success Criteria

✓ Endpoint test: `GET /models?tag=vision` returns only vision-capable models with tags populated in response

✓ Manager test: `LLMModelManager.by_tag('vision')` returns deterministic list

✓ Metadata test: `model.to_metadata().tags` includes all attached tag slugs

✓ Registry test: `ModelRegistry.list_models(tag='vision')` works without errors

✓ All linting and type checks pass

✓ No performance regressions vs. non-tagged queries

---

## Next Phase Work

After this todo completes:
- Lane F todo `db40-model-meta-standardization` will standardize Meta patterns across all models
- Lane F todo `db40-pipeline-home-plan` will document pipeline ownership
- Remaining Phase 40 work will be 100% complete

---

**Implementation owner**: Next available session | **Estimated effort**: 2-3 hours | **Risk**: Medium (ORM async prefetch patterns)

