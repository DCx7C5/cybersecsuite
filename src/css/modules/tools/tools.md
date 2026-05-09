# @tools — Builtin Tool Registry and Shared Execution Surface

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly.

---

## Purpose

`@tools` owns:
- builtin tool definitions exposed by LLM providers
- hybrid tool definitions stored in the database
- the shared registry surface other modules call into

`@tools` does **not** own MCP server connections. MCP discovery and transport live in `@mcps`; MCP tools enter this registry through `McpToolBridge`.

## Current Code Reality

The module is **partially implemented** and more real than the old doc claimed.

| File | Status | Reality |
|------|--------|---------|
| `base.py` | ✅ exists | `BaseToolRegistry` contract, but still part of the singleton/ABC metaclass conflict |
| `enums.py` | ✅ exists | Tool/status/parameter/composition enums |
| `exceptions.py` | ✅ exists | Tool exception types |
| `types.py` | ✅ exists | `ToolSchema`, `HybridToolSchema`, `ManagedTool`, helper types |
| `registry.py` | ⚠️ implemented | Loads builtin provider tool metadata and DB-backed hybrid tools, but still lacks a clean generic async `call()` surface and MCP delegation |
| `models.py` | ⚠️ implemented | ORM models exist, but imports are currently broken and need cleanup before reliable runtime use |
| `endpoints.py` | ✅ exists | `/api/tools*` routes |
| `tool_call_loop.py` | ⚠️ exists | Supporting execution flow, not a complete registry entrypoint |

## What the registry does today

- hardcodes a small set of builtin provider tools
- discovers provider package names under `api_services/`
- loads hybrid tool definitions from the database
- exposes list/get helpers for builtin and hybrid tools

## Phase 9 Registry Cleanup (2026-05-09)

- Builtin tool definitions are now loaded from `builtin_catalog.py`, keeping `registry.py` focused on orchestration.
- Hybrid-tool startup loads now read through `HybridToolDefinition.manager` instead of direct ORM scans in the registry.
- Registry ownership is read/cache only; write operations stay in service/model layers.

## Architecture Note (2026-05-09)

- Shared execution runtime now lives under `src/css/core/tools/`:
  - `executor.py`
  - `tool_call_loop.py`
  - `models.py` access surface
- `src/css/modules/tools/` keeps ownership of ORM models, registry metadata, and compatibility exports for older imports.

## What is still missing

- one clear async execution method on the registry
- MCP delegation path for `ToolType.MCP`
- provider normalization beyond the current hardcoded baseline
- cleanup of the metaclass/import problems in the foundation layer

## MCP Boundary

When an MCP server is connected, `@mcps` should register tool entries like:

- `provider="mcp:splunk"`
- `tool_id="mcp:splunk:search_alerts"`
- `type=ToolType.MCP`

`@tools` should then treat them like any other callable registry entry, but the actual transport call still routes back through `@mcps`.

## Current Risks

- `ToolRegistry` is usable as a metadata registry, but not yet a complete universal execution bus.
- `models.py` currently has import cleanup debt and should not be treated as stable until Phase 9 foundation cleanup lands.
- `AgentExecutor` currently has to work around missing registry execution behavior instead of delegating through one final `ToolRegistry.call()` path.

## Immediate Planning Rule

Treat Phase 22 as an extension of this module, not a replacement:
- `@tools` keeps builtin/hybrid tool ownership
- `@mcps` owns runtime MCP connections
- the bridge between them is a first-class requirement

## Live Todo Expectations

Phase 22 planning must assume:
- `registry.py` already exists and must be **finished**, not created
- MCP routing uses server-scoped IDs
- the registry foundation fix is a prerequisite before broadening registry usage further
