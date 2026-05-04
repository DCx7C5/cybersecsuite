# Hybrid Model Support for Tools Registry

**Status**: 🔵 Planning  
**Location**: `src/css/modules/tools/`  
**Working DB**: `.plan/session.db`  
**Todos**: 23 pending  
**Updated**: 2026-05-03

---

## Problem Statement

Tools registry manages individual LLM provider tools but lacks **hybrid model** support — composite tool definitions blending capabilities across providers. Example: combine OpenAI code execution + Anthropic vision for multi-modal reasoning.

---

## Architecture Design

### 1. Hybrid Tool Definition

**HybridToolSchema** (dataclass):
- `name` — Hybrid identifier
- `description` — What it does
- `component_tools` — list[tool_id]
- `composition_strategy` — sequential|parallel|conditional|fallback|load_balanced
- `fallback_provider` — Optional fallback on failure
- `requires_coordination` — Sequential execution needed?

**CompositionStrategy** (enum):
- **Sequential**: Execute in order
- **Parallel**: Run concurrently, merge results
- **Conditional**: Route based on type/capability
- **Fallback**: Try primary, fall back to secondary
- **Load-balanced**: Distribute by availability/cost

### 2. Registry Enhancement

```python
class ToolRegistry:
    def __init__(self):
        self.hybrid_tools = {}  # {id} → ManagedTool(HybridToolSchema)
        self._load_hybrid_tools()
    
    def register_hybrid_tool(self, schema: HybridToolSchema) → None
    def get_hybrid_tool(self, tool_id: str) → HybridToolSchema
    def list_hybrid_tools(self, filter_by_strategy: Optional[str]) → list[HybridToolSchema]
    def resolve_tool(self, tool_id: str) → Union[ToolSchema, HybridToolSchema]
```

### 3. Database Persistence

**HybridToolDefinition** (Tortoise ORM):
- `id` — BigIntField
- `name` — CharField (unique)
- `description` — TextField
- `component_tools` — JSONField (list of tool_ids)
- `composition_strategy` — CharField (enum)
- `fallback_provider` — CharField (nullable)
- `requires_coordination` — BooleanField
- `metadata` — JSONField
- `created_at` / `updated_at` — DatetimeField
- `created_by` — CharField (nullable)

---

## Implementation Phases

### ✅ Phase 1: Data Models (COMPLETE)
- [x] Add HybridToolSchema dataclass to types.py
- [x] Add CompositionStrategy enum to enums.py
- [x] Validation logic (component_tools exist, strategy supported)

### ✅ Phase 2: ORM Model (COMPLETE)
- [x] Create HybridToolDefinition Tortoise model
- [x] Add serialization helpers (to_dict, from_dict)

### ✅ Phase 3: Registry Enhancement (COMPLETE)
- [x] Add hybrid_tools storage to __init__
- [x] Implement registration methods with validation
- [x] Implement retrieval methods (get, list)
- [x] Implement resolve_tool() smart resolver

### ✅ Phase 4: Database Persistence (COMPLETE)
- [x] Create migration for HybridToolModel table
- [x] Implement _load_hybrid_tools_from_db()
- [x] Implement save_hybrid_tool()

### ✅ Phase 5: REST Endpoints (COMPLETE)
- [x] GET /api/tools/hybrid — List all
- [x] GET /api/tools/hybrid/{id} — Get specific
- [x] POST /api/tools/hybrid — Create
- [x] PUT /api/tools/hybrid/{id} — Update
- [x] DELETE /api/tools/hybrid/{id} — Delete
- [x] GET /api/tools/resolve/{id} — Smart resolver

### 🔵 Phase 6: Testing (PENDING)
- [ ] Schema validation tests
- [ ] Registry operation tests
- [ ] Database persistence tests
- [ ] Endpoint tests
- [ ] Resolver behavior tests

---

## Success Criteria

✅ HybridToolSchema represents composite tools  
✅ ToolRegistry stores/retrieves hybrid tools  
✅ Hybrid tools persist to database  
✅ 5 composition strategies defined & validated  
✅ resolve_tool() returns Union[ToolSchema, HybridToolSchema]  
✅ CRUD endpoints for hybrid tools  
✅ No breaking changes to existing ToolSchema  
✅ Component tool validation before registration  

---

## Dependencies

- `types.py` — ToolSchema, ManagedTool exist
- `registry.py` — ToolRegistry fully implemented
- `enums.py` — Extend with CompositionStrategy
- Tortoise ORM — Database layer
- FastAPI — REST endpoints

---

## Pattern Reference

Follows **cache module** hybrid approach:
- Tortoise ORM model for persistence
- Dataclass for runtime representation
- ManagedTool wrapper for both regular & hybrid tools
