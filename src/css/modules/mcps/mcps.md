# @mcps — MCP Runtime Layer

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document owns the executable MCP runtime specification.

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

The runtime foundation now exists; HTTP lifecycle control and complete runtime
wiring remain pending.

| File | Status | Reality |
|------|--------|---------|
| `src/css/modules/mcps/__init__.py` | present | Package exports require validation when endpoints are added. |
| `src/css/modules/mcps/enums.py` | present | `McpTransport`, `McpServerStatus`. |
| `src/css/modules/mcps/types.py` | present | `McpServerConfig`, `McpCallResult`. |
| `src/css/modules/mcps/models.py` | present | `McpServerConfigRecord` persisted configuration. |
| `src/css/modules/mcps/client.py` | present | `McpClient` transport/call runtime. |
| `src/css/modules/mcps/registry.py` | present | `McpRuntimeRegistry`, `get_mcp_registry()`. |
| `src/css/modules/mcps/endpoints.py` | planned | Lifecycle API surface for start/stop/restart and inspection. |
| `src/css/modules/mcps/bridge.py` | planned/verify | Tool registry bridge only if not already handled by retained integration. |

### Current gates

- `registry.py`, `client.py`, types, enums, and the ORM model already exist, so
  Phase 22 work must **finish and normalize them**, not recreate them.
- `McpRuntimeRegistry` must not become the package catalog. Installed package
  state remains in `core/marketplace`.
- Lifecycle routes and startup behavior must be validated against the current
  registry/client behavior before UI controls rely on them.

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

| Todo ID | Status | What it must do |
|---------|--------|-----------------|
| `mcp-async-client`, `mcp-runtime-types`, `mcp-registry-refactor`, `mcp-startup-validation` | done | Preserve and test the current client/types/registry foundation. |
| `gap-orm-mcps-models` | pending | Reconcile the existing `McpServerConfigRecord` with the canonical ORM/model registration contract rather than creating a duplicate. |
| `mcp-server-lifecycle-api` | pending | Add `src/css/modules/mcps/endpoints.py` handlers for lifecycle control/inspection. |
| `mcp-server-lifecycle-runtime-wire` | pending | Delegate route behavior into `McpRuntimeRegistry`/`McpClient`, startup restoration, and tool sync. |

## Phase 42 ACP Integration Todo Map

| Todo ID | Status in `session.db` | Contract owned here |
|---------|------------------------|---------------------|
| `acp42-spec-v1-contract` | pending | Use ACP v1 session/update/session capability contract as the runtime compatibility baseline for MCP passthrough behavior. |
| `acp42-session-method-surface` | pending | Ensure ACP session method handling maps cleanly to current MCP runtime boundaries and server-scoped tool identities. |
| `acp42-mcp-server-passthrough` | pending | Bind ACP-provided MCP server descriptors to `modules/mcps` connect/disconnect/call lifecycle without breaking `mcp:{server_id}:{tool_name}` IDs. |
| `market42-installer-runtime-hooks` | pending | Consume marketplace install/uninstall lifecycle hooks for ACP/LSP artifacts so MCP runtime config stays in sync with catalog state. |

### Numbered Execution And Validation

1. Import/test current enums, structs, ORM record, client, and registry;
   normalize only verified gaps.
2. Implement lifecycle endpoints over the existing registry and keep
   marketplace catalog state outside MCP runtime.
3. Wire ASGI startup/UI consumers only after lifecycle responses and
   server-scoped tool identity are stable.
4. Validate import cleanliness, persistence restore, transport connect/call/
   disconnect/restart, tool ID collision resistance, route authorization, and
   dependency direction to marketplace/tools/ASGI.

## Rules

- Use `msgspec.Struct` for runtime value types.
- Use `aiohttp` in our own code; third-party `fastmcp` internals are exempt.
- Keep runtime tool IDs server-scoped.
- Keep marketplace/catalog concerns out of `@mcps`.
- Do not assume the current partial registry is production-ready until the Phase 9 registry foundation fix lands.
