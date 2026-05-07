# Tools Module: Startup Initialization Architecture

**Decision**: Initialize all tools from 26 provider SDKs on application start (before first request)

**Status**: 🎯 Planned | **Priority**: 🟠 High | **Phase**: 4

---

## Requirements

1. **Startup Timing**: Before first HTTP request is handled
2. **Scope**: Load tools from ALL 26 providers (OpenAI, Anthropic, Mistral, Groq, etc.)
3. **Durability**: Cache tools for duration of app session
4. **Observability**: Log tool count, provider count, load time, any failures

---

## Implementation Flow

```
ASGI App Startup
  ↓
core/asgi/app.py: on_startup event
  ↓
ToolRegistry.get_instance()  [singleton pattern]
  ↓
_load_builtin_tools()
  ├─ Scan src/css/api_services/*/
  ├─ For each provider:
  │  ├─ Import provider SDK
  │  ├─ Extract tool definitions
  │  ├─ Normalize to ToolSchema
  │  └─ Register in registry
  ├─ Cache tools dict in memory
  └─ Log: "Loaded 12 tools from 26 providers (345ms)"
  ↓
App Ready for First Request
  ↓
/api/tools endpoint
  ↓
Return cached tools (O(1) lookup)
```

---

## Files Involved

### Core Startup
- `src/css/core/asgi/app.py` — FastAPI app definition
  - Add `@app.on_event("startup")` hook
  - Call `ToolRegistry.get_instance()`

### Tools Module
- `src/css/modules/tools/registry.py` — ToolRegistry class
  - Implement `_load_builtin_tools()` method
  - Scan all providers
  - Normalize tools to ToolSchema

- `src/css/modules/tools/__init__.py` — Package init
  - Export ToolRegistry
  - Export get_tool_registry() helper

### Provider SDKs (api_services/)
- Each provider's service.py or tools.py
  - May need to add BUILTIN_TOOLS dict
  - Format: {tool_name: ToolSchema}

---

## Tool Discovery Logic

For each provider in `src/css/api_services/`:

1. Check if provider has `tools.py` or `BUILTIN_TOOLS` in service.py
2. Extract tool definitions
3. Normalize to canonical ToolSchema format:
   ```python
   @dataclass
   class ToolSchema:
       provider: str              # "openai"
       name: str                  # "code_interpreter"
       description: str
       parameters: list[ToolParameter]
       returns: ToolReturnType
       tags: list[str]            # ["code", "execution"]
       enabled: bool = True
       timeout_seconds: int = 30
   ```
4. Store in registry: `registry.tools[f"{provider}:{name}"] = managed_tool`

---

## Provider Tool Matrix

| Provider | Tools | Status |
|----------|-------|--------|
| OpenAI | code_interpreter, file_search, retrieval | ✅ Documented |
| Anthropic | computer_use | ✅ Documented |
| Mistral | (function calling) | ⚠️ Implicit |
| Groq | (OpenAI compat) | ⚠️ Implicit |
| Google Gemini | (function calling) | ⚠️ Implicit |
| All others (20) | (function calling) | ⚠️ Implicit |

**Action**: May need to create `tools.py` in each provider for explicit definitions.

---

## Caching Strategy

```python
class ToolRegistry:
    def __init__(self):
        self._tools = {}  # Lazy-loaded
        self._initialized = False
    
    async def _load_builtin_tools(self):
        """Load from all providers, cache in memory."""
        if self._initialized:
            return  # Already loaded
        
        # Scan all providers
        for tool_id, tool_schema in discovered_tools.items():
            self._tools[tool_id] = ManagedTool(schema=tool_schema)
        
        self._initialized = True
        logger.info(f"Loaded {len(self._tools)} tools")
    
    async def get(self, tool_id: str):
        """O(1) cached lookup."""
        if not self._initialized:
            await self._load_builtin_tools()
        return self._tools.get(tool_id)
```

---

## Logging & Metrics

On successful startup:
```
[INFO] tools.registry: Loaded 12 tools from 26 providers in 345ms
[DEBUG] tools.registry: openai: 3 tools (code_interpreter, file_search, retrieval)
[DEBUG] tools.registry: anthropic: 1 tool (computer_use)
[DEBUG] tools.registry: mistral: 0 tools (via function calling)
...
```

On any provider failure:
```
[WARN] tools.registry: Failed to load tools from gemini: {error}
[WARN] tools.registry: Continuing with 11/12 providers
```

---

## Success Criteria

- ✅ Tools loaded before first HTTP request
- ✅ All 26 providers scanned (even if 0 tools each)
- ✅ Tools cached in memory (no repeated scans)
- ✅ `/api/tools` endpoint returns cached tools (instant)
- ✅ Startup logs show tool count and load time
- ✅ Graceful handling of missing provider tools
- ✅ No breaking changes to api_services/

---

## Phase 6 Alignment (2026-05-07)

### Typed provider spec and startup scan

- Provider metadata should be loaded from `spec.yaml` files into typed
  `ProviderSpec`/related `msgspec.Struct` definitions.
- Startup scanning should prefer `entry_points`-registered provider modules
  rather than hard-coded directory walking.

### Registry loading direction

1. Discover provider entry points.
2. Load and validate provider YAML specs.
3. Build normalized tool/provider catalog once at startup.
4. Expose cached typed capability metadata to API routes.

This keeps startup deterministic and consistent with the Phase 6 plugin architecture.

## Dependencies

- ✅ ToolRegistry base class (audit-tools-registry)
- ✅ ToolSchema dataclass (audit-tools-schema)
- ✅ ASGI app setup (already exists)
- ✅ Provider SDKs (already exist)

---

**Decision Date**: 2026-05-03  
**Related Todos**: `tools-app-startup-init`, `audit-tools-registry`, `audit-tools-schema`
