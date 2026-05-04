# Module Relationships & Dependencies

**Status**: 🔵 Mapping  
**Updated**: 2026-05-03  
**Focus**: Cross-module data model relationships & integration points

---

## Core Data Models by Module

| Module | Models | M2M Relations | Purpose |
|--------|--------|---------------|---------|
| **tags** | Tag | Hub (connects to 6 modules) | Classification, categorization |
| **marketplace** | MarketplaceItem, MarketplaceMeta | M2M: Tag | Marketplace item registry |
| **tools** | HybridToolDefinition | M2M: Tag | Tool registry & composition |
| **cache** | CacheEntry, CacheStats | M2M: Tag (planned) | Caching layer |
| **permissions** | PermissionGrant, ScopeSession | M2M: Tag | Security & access control |
| **teams** | TeamModel | M2M: Tag | Team management |
| **llm_models** | ModelMetadata, ModelPricing | M2M: Tag (planned) | LLM provider models |

---

## Data Model Graph

```
Tag (HUB)
├── MarketplaceItem (M2M: MarketplaceItemTag)
├── HybridToolDefinition (M2M: HybridToolDefinitionTag)
├── PermissionGrant (M2M: PermissionGrantTag)
├── CacheEntry (M2M: CacheEntryTag — planned)
├── ModelMetadata (M2M: ModelMetadataTag — planned)
└── TeamModel (M2M: TeamTag — planned)
```

---

## Module Integration Map

### 1. Tools ↔ Marketplace

**Relationship**: Tools can be packaged in MarketplaceItems

```
MarketplaceItem (kind=agent/skill/tool)
└── contains HybridToolDefinition references
    (via component_tools list)
```

**APIs**:
- GET `/api/marketplace?kind=tool` — List available tools
- GET `/api/tools/hybrid/{id}` — Tool details
- POST `/api/marketplace` — Register tool in marketplace

---

### 2. Tags (Hub) ↔ All Modules

**Relationship**: Unified tagging across all entities

```
Tag M2M Junction Tables:
├── marketplace_item_tag (TagId → MarketplaceItemId)
├── hybrid_tool_tag (TagId → HybridToolDefinitionId)
├── permission_grant_tag (TagId → PermissionGrantId)
├── cache_entry_tag (TagId → CacheEntryId)
├── llm_model_tag (TagId → ModelMetadataId)
└── team_tag (TagId → TeamId)
```

**Common Queries**:
- Filter by tag: `GET /api/marketplace?tags=agent,published`
- List tags: `GET /api/tags`
- Tag entity: `POST /api/tags/{entity_type}/{id}`

---

### 3. Permissions ↔ Tools/Marketplace

**Relationship**: Permission grants restrict access to tools & marketplace items

```
PermissionGrant
├── tool_permissions: [tool_ids] (JSONField)
├── Tags: Security classification (e.g., "admin-only", "sensitive")
└── Controls access to: Tools, MarketplaceItems
```

---

### 4. Marketplace ↔ Cache

**Relationship**: Cached marketplace metadata

```
CacheEntry
├── key: "marketplace:items:{kind}"
├── value: Serialized MarketplaceItem list
└── Tags: Cache classification (e.g., "hot", "cold")
```

---

### 5. Tools ↔ LLM Models

**Relationship**: Hybrid tools reference provider models

```
HybridToolDefinition
├── component_tools: ["openai:code_interpreter", "anthropic:computer_use"]
│                      ↓
├── Maps to ModelMetadata (LLM provider)
└── Tags: Categorization (e.g., "vision", "code-execution")
```

---

## Integration Workflow

### Registering a Tool in Marketplace

```
1. Create HybridToolDefinition (tools module)
   → register_hybrid_tool(schema)
   
2. Package in MarketplaceItem (marketplace module)
   → marketplace.create_item(kind=agent/tool, ...)
   
3. Tag both entities (tags module)
   → tag_marketplace_item(item_id, tag_ids)
   → tag_hybrid_tool(tool_id, tag_ids)
   
4. Add permissions (permissions module)
   → create_permission_grant(tool_ids=[...])
   
5. Cache if needed (cache module)
   → set_cache_entry("marketplace:items:tool", items)
```

---

## Data Flow Diagram

```
┌─────────────────┐
│   Tags (HUB)    │ ← Unified tagging for all entities
└────────┬────────┘
         │
    ┌────┼────┬─────────┬───────────┬──────────┐
    │    │    │         │           │          │
    v    v    v         v           v          v
  Tools M2M Cache M2M Perms M2M Marketplace M2M LLM M2M Teams M2M
    ├────────────────────────────────────────────────────┤
    │          ALL ENTITIES TAGGED & FILTERABLE         │
    └────────────────────────────────────────────────────┘
```

---

## Missing Integrations (TODO)

- [ ] Tools → Agents relationship
- [ ] Skills → Marketplace integration  
- [ ] Capabilities → Tools mapping
- [ ] Events → Tool execution tracking
- [ ] Triage → Tool/Agent selection

---

## Future Connections (Phase 4+)

1. **Agents** ← Execute tools, use skills
2. **Skills** ← Reusable tool compositions
3. **Events** ← Tool execution audit trail
4. **Capabilities** ← Feature detection for tools
5. **Tasks** ← Tool execution context
