# Module Relationships & Dependencies

**Status**: 🔵 Mapping  
**Updated**: 2026-05-08  
**Focus**: Cross-module data model relationships & integration points

---

## Core Data Models by Module

| Module | Models | M2M Relations | Purpose |
|--------|--------|---------------|---------|
| **tags** | Tag | Hub (connects to 6 modules) | Classification, categorization |
| **marketplace** | MarketplaceItem, MarketplaceMeta | M2M: Tag | Marketplace item registry |
| **tools** | HybridToolDefinition | M2M: Tag | Tool registry & composition |
| **core/cache** | CacheEntry, CacheStats | M2M: Tag (planned) | KV caching layer (moved to core — infrastructure) |
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
├── CacheEntry (M2M: CacheEntryTag — planned) [model lives in core/cache/]
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
├── hybrid_tool_definition_tag (TagId → HybridToolDefinitionId)
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

### 4. Marketplace ↔ Cache (core/cache)

**Relationship**: Cached marketplace metadata — `CacheEntry` ORM model lives in `core/cache/` (infrastructure)

```
CacheEntry  [core/cache/models.py]
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
- [ ] Triage → Intelligence module rename (todo: triage-rename-module)

---

## Future Connections (Phase 4+)

1. **Agents** ← Execute tools, use skills
2. **Skills** ← Reusable tool compositions
3. **Events** ← Tool execution audit trail
4. **Capabilities** ← Feature detection for tools
5. **Tasks** ← Tool execution context

---

## Phase 6 Alignment (2026-05-07)

### CQRS EventStore as integration hub

Cross-module write operations should emit immutable domain events and persist through EventStore.
Read models/projections then provide module-specific query surfaces.

### Updated relationship direction

- **Write path**: module command handler → domain event(s) → EventStore append.
- **Read path**: projection/materialized view → module API/query layer.
- **Observability**: event stream is bridged to OTEL/OpenObserve for unified traces/audit.

This reduces tight direct module-to-module coupling and makes replay/audit first-class.

---

## Planned Retrieval, Intelligence & Graph Relationships

The current plan adds a second integration cluster on top of the older module map:

| Area | Owns | Consumes | Produces |
|------|------|----------|----------|
| **`core/memory`** | turns, summaries, session state, vault | user/agent messages | context input for retrieval, session flow data |
| **`modules/triage`** | tagging, routing, confidence, quality gates | memory entries, user turns | tags, route hints, pre-filter decisions, stable graph-ingest hints |
| **`core/rag_vector`** | vector retrieval + hybrid routing/fusion | memory context, knowledge docs, future route hints | fused retrieval context for agents |
| **`core/rag_graph`** | graph ingest, graph traversal, graph retrieval | extracted entities, relationships, future graph exports | graph-side retrieval results for hybrid mode |
| **`modules/mitre`** | canonical ATT&CK data | ATT&CK imports, domain mappings | ATT&CK graph projection candidates |
| **`modules/threat_intel`** | canonical intel entities + feeds | MISP/OTX/VT-style data | graph projection candidates for actors/malware/campaigns/tools/observables |
| **`modules/graphs`** | workflow/session/approval graph snapshots + live views | events, tasks, approvals, memory turns | graph snapshots, live graph diffs, future graph exports |
| **`modules/workflows`** | executable DAG/workflow definitions | memory, approvals, agent/tool events | workflow state that can be visualized and later projected |

### Current Direction of Coupling

```text
memory -> triage -> rag_vector -> agent execution
rag_vector -> rag_graph (graph / hybrid modes)
events/tasks/approvals -> graphs
workflows -> events -> graphs
graphs/workflows -(later export)-> GraphRAG
mitre/threat_intel/triage -(projection)-> rag_graph
```

### Boundary Rules

- `modules/triage` may influence retrieval mode later, but does not own retrieval execution.
- `core/rag_vector` may consume graph projections later, but does not own workflow graph builders.
- `core/rag_graph` owns graph retrieval internals, but not workflow graph builders.
- `modules/mitre` and `modules/threat_intel` stay canonical; GraphRAG receives projections, not domain ownership.
- `modules/workflows` owns executable graph semantics; `modules/graphs` owns visualization/snapshots.
- `core/cache` and `core/prompt_cache` remain infrastructure dependencies, not domain hubs.

See [intelligence-retrieval-graph.md](./intelligence-retrieval-graph.md) for the integrated architecture graph.
