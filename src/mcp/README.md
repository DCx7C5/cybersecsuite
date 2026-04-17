# MCP Package

> ⚠️ **Phase A — In Progress.** This package is currently a stub. The 29 MCP tool implementations live in `mcp_server.py` at the repo root. Migration to this package is planned for Phase A.

## Planned Structure

```
src/mcp/
├── __init__.py       # all_servers() → list of MCPServer, allowed_tools() → list[str]
├── cybersec.py       # 29 cybersec tools (migrated from mcp_server.py)
└── dystopian.py      # crypto/dystopian tools (from mcps/dystopian-crypto-mcp/)
```

## Current State

`src/mcp/__init__.py` is empty. All tool implementations are in `mcp_server.py` (root).

Use `make mcp` to run the current standalone MCP server:

```bash
make mcp
# → uv run python mcp_server.py
```

## Planned API (Phase A)

```python
from mcp import all_servers, allowed_tools

# Get all in-process MCP servers for agent_sdk.py
servers = all_servers()       # → {"cybersec": MCPServer, "dystopian": MCPServer}
tools = allowed_tools()       # → ["mcp__cybersec__*", "mcp__dystopian__*"]

# Use with Agent SDK
from a2a.agent_sdk import run_agent_query, build_agent_options
options = build_agent_options(mcp_servers=servers, allowed_tools=tools)
result = await run_agent_query("investigate this IOC", options=options)
```

## Tool Categories (29 tools in `mcp_server.py`)

| Category        | Tools                                                                                                                                                                                              | Count |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Scope           | `set_scope`, `get_scope`, `reset_scope`, `scope_summary`                                                                                                                                           | 4     |
| Cases           | `case_open`, `case_status`, `case_close`                                                                                                                                                           | 3     |
| Findings + IOCs | `add_finding`, `add_ioc`, `query_findings`, `update_risk_register`, `get_project_memory`                                                                                                           | 5     |
| Intelligence    | `db_healthcheck`, `bootstrap_intelligence`, `suggest_mitre`, `share_to_layers`, `get_layer_value`                                                                                                  | 5     |
| AI Proxy        | `proxy_chat`, `proxy_providers`, `proxy_models`, `proxy_usage`, `proxy_cost`, `simulate_route`, `set_budget_guard`, `get_circuit_breakers`, `explain_route`, `routing_strategies`, `best_provider` | 11    |
| Cache           | `cache_lookup`, `cache_store`, `cache_analytics`, `cache_invalidate`                                                                                                                               | 4     |
| Agents          | `session_snapshot`, `agent_registry`                                                                                                                                                               | 2     |

Total: 39 tools across `mcp_server.py` (some counted above differ from the exposed 29 — exact count in `docs/mcp-tools.md`).

See [docs/mcp-tools.md](../../docs/mcp-tools.md) for the full tools reference.
