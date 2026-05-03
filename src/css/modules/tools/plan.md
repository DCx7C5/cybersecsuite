# @tools — Tool Registry & MCP Server

**Location**: `src/css/modules/tools/`  
**Status**: ⚠️ **Partial** (86 lines: 3 files + empty registry.py)  
**5-File Pattern**: ❌ 1/5 (has base.py, enums.py, exceptions.py; missing models.py, endpoints.py)

---

## Purpose

The `@tools` module provides:

1. **Builtin Tool Registry** — Maps all available tools from **26 LLM provider SDKs** (api_services/)
2. **MCP Server** — Model Context Protocol server for tool registration and discovery
3. **Tool Execution** — Execute registered tools with parameter validation
4. **Tool Composition** — Support tool chaining and dependency management

---

## Current Implementation

### Files (Total: 86 lines)

| File | Lines | Status | Purpose |
|------|-------|--------|---------|
| `base.py` | 19 | ✅ Defined | BaseToolRegistry ABC + interface methods |
| `enums.py` | 18 | ✅ Defined | ToolStatus (available/unavailable/disabled), ToolType (builtin/custom/external/mcp) |
| `exceptions.py` | 49 | ✅ Defined | BaseToolException, ToolNotFoundError, ToolExecutionError, ToolConfigurationError |
| `registry.py` | 0 | ❌ EMPTY | **Should map all provider tools** — NEEDS IMPLEMENTATION |
| `models.py` | ❌ MISSING | Need types for Tool, ToolSchema, ToolResult |
| `endpoints.py` | ❌ MISSING | Need FastAPI routes (/api/tools/list, /api/tools/{id}, etc) |
| `__init__.py` | 0 | ⚠️ Empty | Should initialize logger + exports |

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

### 3. **MCP Server Integration**

```python
# Conceptual: MCP server expose tools via Model Context Protocol
class MCPToolServer:
    """MCP server for tool discovery and execution."""
    
    def list_tools(self) -> list[MCPTool]:
        """MCP: Return all registered tools."""
        
    def call_tool(self, tool_name: str, args: dict) -> str:
        """MCP: Execute a tool through MCP protocol."""
```

---

## Implementation Roadmap

### Phase 1: Core Registry (Week 1)

- [ ] Define ToolSchema dataclass (models.py)
  - Fields: provider, name, description, parameters, returns, version
- [ ] Implement ToolRegistry.register_tool()
- [ ] Implement ToolRegistry.list_tools()
- [ ] Implement ToolRegistry._load_builtin_tools()
  - [ ] Scan @api_services/ for tool definitions
  - [ ] Normalize across 26 providers
  - [ ] Handle provider-specific tool patterns

### Phase 2: FastAPI Endpoints (Week 2)

- [ ] Create endpoints.py with REST API:
  - `GET /api/tools` — List all tools
  - `GET /api/tools/{tool_id}` — Get specific tool details
  - `GET /api/tools/provider/{provider}` — Filter by provider
  - `POST /api/tools/execute` — Execute a tool
- [ ] Parameter validation + error handling

### Phase 3: MCP Server (Week 3)

- [ ] Implement MCPToolServer
- [ ] Wire MCP into FastAPI (optional: separate process)
- [ ] Test tool discovery via MCP protocol
- [ ] Document MCP tool interface

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

| Provider | SDK Status | Tools Status | Sync Status |
|----------|-----------|--------------|------------|
| OpenAI | PARTIAL | ✅ Documented (code_interpreter, retrieval, file_search) | ❌ NOT IN REGISTRY |
| Anthropic | PARTIAL | ✅ Documented (computer_use) | ❌ NOT IN REGISTRY |
| Mistral | STUB | ⚠️ Partially documented (function calling) | ❌ NOT IN REGISTRY |
| Google | STUB | ⚠️ Partially documented (function calling) | ❌ NOT IN REGISTRY |
| Groq | STUB | ⚠️ Documented (OpenAI compat) | ❌ NOT IN REGISTRY |
| All others | STUB | ⚠️ Partial/incomplete | ❌ NOT IN REGISTRY |

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
**Last Updated**: 2026-05-03 | **Ready for**: Phase 4 (Module Consistency)
