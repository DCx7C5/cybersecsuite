# @mcps — MCP Protocol Layer

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## Purpose

The `@mcps` module manages **MCP (Model Context Protocol) servers** — connecting to them, discovering their tools, and executing tool calls. It is **distinct from `@tools`**:

| `@tools` | `@mcps` |
|----------|---------|
| LLM provider builtin tools (code_interpreter, computer_use, …) | MCP server management (connect/discover/call) |
| Static definitions from api_services/ | Dynamic server connections |
| ToolSchema registry | McpServerRegistry |
| Provider-scoped | Server-scoped (any MCP-compatible server) |

**Key capability**: `@mcps` bridges both worlds — when a MCP server is connected, its tools are automatically registered into `@tools`'s `ToolRegistry` with `ToolType.MCP`, making them indistinguishable from builtin tools to the agent layer.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.modules.tools` | → pushes into | McpToolBridge registers MCP tools as `ToolType.MCP` in ToolRegistry |
| `css.core.types.entities.tool` | → uses | `Tool.fn_path` is dotted path for PYTHON_DIRECT dispatch |
| `css.core.db` | → persists to | McpServerConfigRecord Tortoise ORM |
| `css.core.events` | → emits into | `@instrument("mcp.call.{server}.{tool}")` — Phase 14 |
| ASGI startup | → initialized by | load_from_db() + auto_connect on app start |
| `fastmcp` (v3.1.0+) | → wraps | All transport logic delegated to fastmcp.Client |

---

## Transport Architecture

Three transport types. All use the same `fastmcp.Client` API — only the argument differs:

### 1. PYTHON_DIRECT — In-process (zero HTTP, zero subprocess)

```python
from fastmcp import Client
from importlib import import_module

module, attr = config.module_path.rsplit(":", 1)
factory = getattr(import_module(module), attr)
server = factory()  # returns FastMCP instance

async with Client(server) as client:          # FastMCPTransport — no subprocess, no HTTP
    tools = await client.list_tools()
    result = await client.call_tool("name", args)
```

**When to use**: Trusted in-process MCP servers (e.g. `cssmcp` cybersec tools, any FastMCP server in the same Python process). ~10× faster than stdio, no serialization overhead for large results.

**`module_path` format**: `"css.modules.mcps.servers.cybersec:create_server"` (importable path + colon + callable name)

### 2. STDIO — Subprocess (most common for external MCPs)

```python
from fastmcp.client.transports import PythonStdioTransport, UvStdioTransport

# Python subprocess
async with Client(PythonStdioTransport(config.command, env=config.env)) as client:
    ...

# Or: uv run (preferred for our stack)
async with Client(UvStdioTransport(config.command, env=config.env)) as client:
    ...
```

**When to use**: Any MCP server not in our Python process — filesystem tools, git tools, external services.

### 3. SSE / StreamableHTTP — Remote (standard MCP over HTTP)

```python
from fastmcp.client.transports import SSETransport, StreamableHttpTransport

async with Client(SSETransport(config.url)) as client:      # legacy SSE
    ...
async with Client(StreamableHttpTransport(config.url)) as client:  # MCP 2025-03 spec
    ...
```

**When to use**: Remote MCP servers, hosted services, multi-tenant deployments.

---

## Module Files (Target)

```
mcps/
├── __init__.py        ← exports McpClient, McpServerRegistry, get_mcp_registry
├── enums.py           ← McpTransportType, McpServerStatus
├── exceptions.py      ← McpConnectionError, McpCallError, McpNotFoundError, McpProtocolError
├── types.py           ← McpServerConfig, McpToolDef, McpCallResult (msgspec.Struct, frozen)
├── client.py          ← McpClient — wraps fastmcp.Client, handles all 3 transports
├── registry.py        ← McpServerRegistry singleton — multi-server management
├── bridge.py          ← McpToolBridge — MCP tools → ToolRegistry as ToolType.MCP
├── models.py          ← Tortoise ORM: McpServerConfigRecord (persistence)
├── endpoints.py       ← FastAPI: /api/mcps/* (server CRUD + tool proxy)
└── plan.md            ← this file
```

---

## Key Types

### McpServerConfig (msgspec.Struct, frozen)

```python
class McpServerConfig(msgspec.Struct, frozen=True):
    server_id: str
    transport: McpTransportType
    # STDIO
    command: list[str] | None = None
    env: dict[str, str] = {}
    # SSE / StreamableHTTP
    url: str | None = None
    # PYTHON_DIRECT
    module_path: str | None = None   # e.g. "css.modules.mcps.servers.cybersec:create_server"
    # Common
    timeout: int = 30
    auto_connect: bool = True
```

### McpToolDef (msgspec.Struct, frozen)

```python
class McpToolDef(msgspec.Struct, frozen=True):
    server_id: str
    name: str
    description: str
    input_schema: dict    # JSON Schema for args
```

### McpCallResult (msgspec.Struct, frozen)

```python
class McpCallResult(msgspec.Struct, frozen=True):
    server_id: str
    tool_name: str
    content: str
    is_error: bool = False
```

---

## McpServerRegistry API

```python
registry = get_mcp_registry()

# Register a PYTHON_DIRECT server
await registry.register(McpServerConfig(
    server_id="cybersec",
    transport=McpTransportType.PYTHON_DIRECT,
    module_path="css.modules.mcps.servers.cybersec:create_server",
))

# Register a stdio server (e.g. mcp-server-filesystem)
await registry.register(McpServerConfig(
    server_id="filesystem",
    transport=McpTransportType.STDIO,
    command=["uvx", "mcp-server-filesystem", "/workspace"],
))

# Connect and list tools
await registry.connect("cybersec")
tools = await registry.list_tools("cybersec")

# Call a tool
result = await registry.call_tool("cybersec", "vault_scaffold", {"name": "test"})

# Bridge tools into ToolRegistry
McpToolBridge().sync_server("cybersec", get_tool_registry())
```

---

## ToolBridge — How MCP tools appear in @tools

After `McpToolBridge().sync_server(server_id, tool_registry)`:

- Each `McpToolDef` becomes a `ToolSchema(provider="mcp:cybersec", name="vault_scaffold", ...)`
- Tagged with `["mcp", "cybersec"]`
- `ToolType.MCP` marker
- Execution: `tool_registry.call("mcp:cybersec:vault_scaffold", args)` → delegates to `mcp_registry.call_tool("cybersec", "vault_scaffold", args)`
- From the agent layer: **indistinguishable from builtin tools**

---

## Phase 22 Todos

| Todo ID | Description | Task |
|---------|-------------|------|
| `mcp-enums` | McpTransportType + McpServerStatus | T22.1-foundation |
| `mcp-exceptions` | Connection/call/protocol exceptions | T22.1-foundation |
| `mcp-types-struct` | McpServerConfig + McpToolDef + McpCallResult | T22.1-foundation |
| `mcp-client` | McpClient wrapping fastmcp.Client | T22.2-client |
| `mcp-python-direct` | PYTHON_DIRECT in-process bypass | T22.2-client |
| `mcp-server-registry` | McpServerRegistry singleton | T22.3-registry |
| `mcp-tool-bridge` | MCP tools → ToolRegistry bridge | T22.3-registry |
| `mcp-models` | Tortoise ORM McpServerConfigRecord | T22.4-persistence |
| `mcp-endpoints` | FastAPI /api/mcps/* | T22.5-api |
| `mcp-startup-wire` | ASGI startup integration | T22.6-integration |
| `mcp-builtin-servers` | Built-in PYTHON_DIRECT (cssmcp) | T22.6-integration |

---

## Rules

- HTTP client for SSE: `aiohttp` not `httpx` (but fastmcp.Client handles this internally via httpx — this is acceptable since we don't write the HTTP code, fastmcp does)
- All async: `async def`, `asyncio.gather` for parallel server connects
- msgspec.Struct for all value types (not dataclass)
- `Protocol` for McpTransport ABC (not ABC class)
- Loader.py auto-discovers `endpoints.py` and `models.py`

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.  
> Phase 22 — MCP Protocol Layer | 14 todos | All pending as of 2026-05-04
