# @mcps — MCP Runtime Layer

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly.

---

## Purpose

`@mcps` owns the **runtime side** of MCP:
- server configuration
- transport selection
- connect/disconnect lifecycle
- tool discovery
- tool invocation
- bridging discovered tools into `@tools`

It is distinct from:
- `core/marketplace` = catalog/install metadata
- `@tools` = provider builtin tools + shared tool registry surface

## Runtime Identity Contract

Use **server-scoped runtime IDs**. Do not use bare `mcp:{tool_name}` IDs.

| Thing | Format | Meaning |
|------|--------|---------|
| Marketplace/server slug | `mcp:{server_id}` | Installed/configured MCP server package or config entry |
| Tool provider string | `mcp:{server_id}` | Provider namespace stored on `ToolSchema` |
| Runtime tool ID | `mcp:{server_id}:{tool_name}` | Exact callable tool target |

Example:
- server: `mcp:splunk`
- provider: `mcp:splunk`
- tool call: `mcp:splunk:search_alerts`

This avoids collisions when two servers expose the same tool name.

## Current Code Reality

The module is **planned but not import-clean yet**.

| File | Status | Reality |
|------|--------|---------|
| `__init__.py` | ⚠️ present | Exports names that do not all exist yet |
| `registry.py` | ⚠️ partial | `McpRuntimeRegistry` exists, but depends on missing types/models and needs Phase 9 registry foundation cleanup |
| `enums.py` | ❌ empty | still to implement |
| `types.py` | ❌ empty | still to implement |
| `models.py` | ❌ empty | still to implement |
| `exceptions.py` | ❌ missing | still to implement |
| `client.py` | ❌ missing | still to implement |
| `bridge.py` | ❌ missing | still to implement |
| `endpoints.py` | ❌ missing | still to implement |

### Current blockers

- `BaseRegistry` / `BaseToolRegistry` still mix `ABC` with `AsyncSafeSingletonMeta`, which currently causes import-time metaclass conflicts in dependent registries.
- `registry.py` already exists, so Phase 22 should **finish and normalize it**, not recreate it from scratch.
- `McpRuntimeRegistry` must not become the package catalog. Installed package state remains in `core/marketplace`.

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.marketplace` | ← configured by | Installed/enabled MCP server packages feed runtime config |
| `css.modules.tools` | → bridges into | MCP tools become `ToolType.MCP` entries in `ToolRegistry` |
| `css.core.db` | → persists to | `McpServerConfigRecord` stores runtime config |
| `css.core.asgi` | → started by | ASGI lifespan restores server configs and auto-connects enabled servers |
| `fastmcp` | → wraps | Transport client for PYTHON_DIRECT, STDIO, SSE, Streamable HTTP |

## Transport Contract

### `PYTHON_DIRECT`
- trusted in-process FastMCP server factory
- zero subprocess
- zero HTTP
- canonical local-first path for built-in cybersec MCP servers

### `STDIO`
- subprocess-based MCP servers
- preferred external local tool/server path

### `SSE` / `STREAMABLE_HTTP`
- remote MCP servers when needed
- still optional in a local-first deployment

## Planned Runtime Flow

```text
Marketplace item/config (`mcp:{server_id}`)
        ↓
McpRuntimeRegistry restores enabled servers from DB
        ↓
McpClient connects using transport-specific adapter
        ↓
McpToolBridge registers discovered tools into ToolRegistry
        ↓
Agents / SIEM / future proxy call `mcp:{server_id}:{tool_name}`
```

## Phase 22 Todo Map

| Todo ID | What it must do |
|---------|-----------------|
| `mcp-enums` | Define transport/status enums used by every MCP runtime type |
| `mcp-exceptions` | Define module-specific connection/call/protocol errors |
| `mcp-types-struct` | Create frozen runtime structs: config, tool definition, call result |
| `mcp-client` | Wrap `fastmcp.Client` behind one async client API |
| `mcp-python-direct` | Implement the trusted in-process FastMCP path |
| `mcp-server-registry` | Finish the existing `registry.py` so it manages configs, status, connections, and tool lookup cleanly |
| `mcp-tool-bridge` | Register discovered MCP tools into `ToolRegistry` as `ToolType.MCP` |
| `mcp-models` | Persist server configs and enable ASGI restore-on-start |
| `mcp-endpoints` | Expose server CRUD, connect/disconnect, tool discovery, and call proxy endpoints |
| `mcp-startup-wire` | Load configs on startup, auto-connect enabled servers, sync tools |
| `mcp-builtin-servers` | Register local built-in cybersec MCP servers via `PYTHON_DIRECT` |

## Rules

- Use `msgspec.Struct` for runtime value types.
- Use `aiohttp` in our own code; third-party `fastmcp` internals are exempt.
- Keep runtime tool IDs server-scoped.
- Keep marketplace/catalog concerns out of `@mcps`.
- Do not assume the current partial registry is production-ready until the Phase 9 registry foundation fix lands.
