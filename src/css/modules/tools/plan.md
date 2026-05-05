# @tools — Tool Registry & LLM Provider Builtins

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.modules.events` | → consumes | `@instrument("tool.call.{tool_name}")` — Phase 14 entry point |
| `css.modules.permissions` | → consumes | PermissionChecker.can_tool() enforced via @pre_hook (automatic) |

---

## Purpose

The `@tools` module provides:

1. **Builtin Tool Registry** — Maps all available tools from **26 LLM provider SDKs** (api_services/)
2. **Tool Execution** — Execute registered tools with parameter validation
3. **Tool Composition** — Support tool chaining and dependency management

> **MCP tools are NOT managed here.** MCP server connections, discovery, and execution are handled by the `@mcps` module. MCP tools appear in the ToolRegistry via `McpToolBridge` (mcps/bridge.py) with `ToolType.MCP` marker and `provider="mcp:{server_id}"`. From the agent layer they are indistinguishable from builtin tools.

---

## Current Implementation

### Files (Total: 1103 lines)

| File            | Lines     | Status                                                      | Purpose                                                                             |
|-----------------|-----------|-------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `base.py`       | 19        | ✅ Defined                                                   | BaseToolRegistry ABC + interface methods                                            |
| `enums.py`      | 50        | ✅ Defined                                                   | ToolStatus/ToolType/ParameterType/CompositionStrategy enums                         |
| `exceptions.py` | 49        | ✅ Defined                                                   | BaseToolException, ToolNotFoundError, ToolExecutionError, ToolConfigurationError    |
| `types.py`      | 211       | ✅ Defined                                                   | ToolSchema, HybridToolSchema, ManagedTool, parameter/return models                  |
| `registry.py`   | 482       | ✅ Implemented                                               | Builtin tool registry, provider discovery, hybrid registry + DB sync                |
| `models.py`     | 91        | ✅ Implemented                                               | HybridToolDefinition ORM + tag junction model                                       |
| `endpoints.py`  | 169       | ✅ Implemented                                               | `/api/tools*` and `/api/tools/hybrid*` REST routes                                  |
| `__init__.py`   | 32        | ✅ Implemented                                               | Public exports for tools types/enums/registry                                       |

---

## Architecture Design

### 1. **Tool Definition (from Provider SDKs)**

Each LLM provider has builtin tools:

```
@api_services/
├── openai/          → Tools: code_interpreter, file_search, retrieval
├── anthropic/       → Tools: computer_use (vision-based tool use)
├── mistral/         → Tools: (standard function calling)
├── groq/            → Tools: (via OpenAI compat)
├── google/          → Tools: (Google function calling)
└── ... (21 more providers)
```

**Registry Challenge**: Extract and normalize tools across 26 different SDK APIs

### 2. **Registry Structure (registry.py)**

```python
class ToolRegistry(BaseToolRegistry):
    """Registry for all builtin tools from all LLM providers."""
    
    def __init__(self):
        self.tools = {}  # {provider}:{tool_name} → ToolSchema
        self._load_builtin_tools()  # Load from api_services
    
    def _load_builtin_tools(self):
        """Scan all api_services/* and extract builtin tools."""
        # For each provider in api_services/:
        #   - Import provider SDK
        #   - Extract supported tools
        #   - Normalize to ToolSchema
        #   - Store in registry
    
    def get_provider_tools(self, provider: str) -> list[ToolSchema]:
        """Get all tools available for a specific provider."""
        
    def get_tool(self, tool_id: str) -> ToolSchema:
        """Get a specific tool by ID (provider:tool_name)."""
        
    def list_tools(self, filter_by_provider=None) -> list[ToolSchema]:
        """List all registered tools (optionally filtered by provider)."""
```

### 3. **ToolType.MCP — Bridge marker**

Tools registered by `McpToolBridge` (see `@mcps` module) use `ToolType.MCP`. They are stored in ToolRegistry with `provider="mcp:{server_id}"` and executed by delegating back to `McpServerRegistry.call_tool()`. Tools/ does not own MCP connection logic.

---

## Implementation Roadmap

### Phase 1: Core Registry (Week 1)

- [x] Define ToolSchema dataclass (types.py)
  - Fields: provider, name, description, parameters, returns, version
- [x] Implement ToolRegistry.register_tool()
- [x] Implement ToolRegistry.list_tools()
- [x] Implement ToolRegistry._load_builtin_tools()
  - [x] Scan @api_services/ for provider directories
  - [ ] Normalize across all providers (openai/anthropic complete, others pending)
  - [x] Handle provider-specific tool patterns

### Phase 1.5: App Startup Integration ⭐ **NEW**

**Requirement**: Initialize all tools from provider SDKs on application start

- [x] **Startup Hook** — Call ToolRegistry on ASGI app initialization
  - [x] Add ToolRegistry singleton to core startup sequence
  - [x] Load all tools before first request handled
  - [x] Cache tools for duration of app session
  
- [x] **Provider Tool Discovery** — Auto-discover provider packages
  - [x] OpenAI: code_interpreter, file_search
  - [x] Anthropic: computer_use
  - [x] Other providers discovered and registered with empty builtin set by default
  - [ ] Normalize across different SDK APIs

- [x] **Initialization Flow**:
  ```
  app.startup() 
    → core/startup.py imports ToolRegistry
    → ToolRegistry().get_instance() [singleton]
    → _load_builtin_tools() scans api_services/*/
    → Extract tool definitions from each provider
    → Normalize to ToolSchema format
    → Cache in registry for endpoint access
    → Log: "Loaded N tools from M providers"
  ```

- [ ] **Logging & Metrics**
  - [x] Log tool count at startup
  - [ ] Track startup latency (tool discovery time)
  - [ ] Report any provider tools that fail to load

- [ ] **Caching Strategy**
  - [x] Tools cached in memory for app lifetime
  - [ ] Optional: Reload endpoint for dynamic refresh
  - [ ] Consider: Redis fallback for distributed setups

### Phase 2: FastAPI Endpoints (Week 2)

- [x] Create endpoints.py with REST API:
  - `GET /api/tools` — List all tools
  - `GET /api/tools/{tool_id}` — Get specific tool details
  - `GET /api/tools/provider/{provider}` — Filter by provider
  - `POST /api/tools/execute` — Execute a tool (pending)
- [x] Parameter validation + error handling

### Phase 3: MCP Bridge Integration (moved to @mcps)

> **MOVED**: MCP Server implementation (`mcp_server.py`) is now the responsibility of `@mcps` module (Phase 22). `@tools` only needs to support `ToolType.MCP` as a registry entry type. `mcp_server.py` is NOT part of the tools/ directory.

### Phase 4: Polish (Week 4)

- [ ] Add logger initialization to __init__.py
- [ ] Tool execution metrics & tracing
- [ ] Tool composition support (chaining)
- [ ] Comprehensive testing

---

## API Services Sync Requirements

**What needs updating in `.plan/api_services/`**:

For each provider documentation (anthropic-sdk.md, openai-sdk.md, etc.), add:

```markdown
## Builtin Tools

### Available Tools
- Tool 1: `description`
- Tool 2: `description`
- ...

### Tool Schema
{
  "provider": "openai",
  "name": "code_interpreter",
  "description": "...",
  "parameters": {...}
}

### MCP Registration
Tools are auto-registered with @tools registry via:
```
tools/registry.py → loads from api_services/{provider}/tools.py
```

### How to Add Provider Tools

For new provider in api_services/{provider}/:
1. Create `tools.py` with `BUILTIN_TOOLS` dict
2. Follow ToolSchema format
3. Registry auto-discovers on startup
```

---

## Current Sync Status with API Services

| Provider   | SDK Status | Tools Status                                            | Sync Status       |
|------------|------------|---------------------------------------------------------|-------------------|
| OpenAI     | PARTIAL    | ✅ Documented (code_interpreter, retrieval, file_search) | ❌ NOT IN REGISTRY |
| Anthropic  | PARTIAL    | ✅ Documented (computer_use)                             | ❌ NOT IN REGISTRY |
| Mistral    | STUB       | ⚠️ Partially documented (function calling)              | ❌ NOT IN REGISTRY |
| Google     | STUB       | ⚠️ Partially documented (function calling)              | ❌ NOT IN REGISTRY |
| Groq       | STUB       | ⚠️ Documented (OpenAI compat)                           | ❌ NOT IN REGISTRY |
| All others | STUB       | ⚠️ Partial/incomplete                                   | ❌ NOT IN REGISTRY |

**Gap**: registry.py is **EMPTY** — no tools actually loaded from api_services

---

## 5-File Pattern Migration

**Current**: 3 files (base.py, enums.py, exceptions.py)  
**Target**: 5 files (add models.py, endpoints.py)

```
tools/
├── __init__.py           ← Add logger + exports
├── base.py               ← ✅ BaseToolRegistry
├── enums.py              ← ✅ ToolStatus, ToolType
├── exceptions.py         ← ✅ Tool exceptions
├── models.py             ← ❌ NEW: ToolSchema, ManagedTool dataclasses
├── endpoints.py          ← ❌ NEW: FastAPI routes
├── registry.py           ← ⚠️ NEEDS: Load from api_services
└── mcp_server.py         ← ❌ Optional: MCP integration
```

---

## Dependencies

- **core/types**: BaseRegistry, UniversalLLMClient
- **core/logger**: Logger setup
- **api_services**: Access to all 26 provider SDK definitions
- **FastAPI**: For REST endpoints

---

## Success Criteria

- ✅ ToolRegistry auto-loads tools from all 26 providers
- ✅ `/api/tools` endpoint returns complete tool list
- ✅ `/api/tools/{tool_id}` returns specific tool details
- ✅ MCP server discovers and exposes all tools
- ✅ Tool execution works via POST /api/tools/execute
- ✅ All tools follow normalized ToolSchema
- ✅ Zero breaking changes to existing api_services/

---

**Status**: 🔴 Priority (Medium-High) | **Implementation**: 0% (registry empty)  
**Last Updated**: 2026-05-04 | **Ready for**: Phase 4 (Module Consistency)
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

## Audit (2026-05-04)

**Status**: DB schema consistency updates synchronized
**Changes**:
- `HybridToolDefinition.composition_strategy` migrated to `CharEnumField(CompositionStrategy)`
- `HybridToolDefinitionTag.Meta.indexes` migrated to `models.Index(fields=["hybrid_tool", "tag"])`

---

## Phase 14 — ToolExecutor Entry Point

`ToolExecutor` is **entry point 5 of 5** for the `@events` instrumentation system.

- Namespace: `@instrument("tool.call.{tool_name}")` (e.g. `"tool.call.bash.execute"`)
- The `@pre_hook("tool.call.*", priority=5)` registered in `permissions/hooks.py` blocks calls if the agent has no matching `ToolGrant`
- The pre_hook raises `HookBlockedError` — the tool function itself **never runs**
- Events fired: `tool.call.started`, `tool.call.completed`, `tool.call.failed`

---

## Phase 15 — Automatic Permission Enforcement

Tool permission checking is **entirely automatic** via Phase 14 interceptors:

- Tools do NOT check permissions themselves — zero permission code in tool implementations
- `permissions/hooks.py` registers a `@pre_hook("tool.call.*", priority=5)` that calls `PermissionChecker.can_tool(agent_id, tool_pattern)`
- Any `allowed=False` ToolGrant for the agent beats all `allowed=True` grants (deny-wins)
- Elevation (`can_elevated()`) is a SEPARATE gate required for root/privileged operations

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
