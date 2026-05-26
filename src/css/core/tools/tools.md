# core/tools - Shared Tool Execution Runtime

**Location**: `src/css/core/tools/`  
**Status**: Existing shared runtime; metadata/registry ownership remains split with `src/css/modules/tools/`.

## Purpose

`core/tools` contains shared execution contracts used by agents and chat flows:

- registry access contract
- execution and tool-call loop surfaces
- shared hybrid-tool model access
- core tool exception hierarchy

`modules/tools` remains the module-facing registry and API owner. `modules/mcps` owns MCP server transport; MCP tools enter the tool registry through a bridge.

## Current Code Reality

| File | Responsibility |
|------|----------------|
| `base.py` | `BaseToolRegistry` contract and registry lookup |
| `executor.py` | `AgentToolExecutor`, instrumentation and hybrid execution |
| `tool_call_loop.py` | repeated assistant/tool execution flow |
| `models.py` | shared hybrid tool model surface |
| `exceptions.py` | typed tool runtime failures |
| `__init__.py` | exported shared execution API |

## Required Boundaries

- Provider builtin tools are registered by the SDK/tools bridge.
- MCP connections and remote calls stay in `modules/mcps`.
- Permission and approval checks must execute before destructive tool calls once those layers are wired.
- Tool lifecycle events must use `core/events` instrumentation.

## Related Local Plans

- `src/css/modules/tools/tools.md` - registry/API and MCP bridge boundary
- `src/css/modules/mcps/mcps.md` - MCP runtime and server-scoped IDs
- `src/css/modules/agents/agents.md` - agent-side execution caller
