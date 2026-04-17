"""MCP package — exposes all in-process SDK MCP servers.

Usage:
    from mcp import all_servers, allowed_tools
    options = ClaudeAgentOptions(
        mcp_servers=all_servers(),
        allowed_tools=allowed_tools(),
    )
"""
from __future__ import annotations

from typing import Any


def all_servers() -> dict[str, Any]:
    """Return all configured SDK MCP server instances keyed by server name."""
    from mcp.cybersec import cybersec_server
    from mcp.dystopian import dystopian_server

    return {
        "cybersec": cybersec_server,
        "dystopian": dystopian_server,
    }


def allowed_tools() -> list[str]:
    """Return all allowed tool names across all registered SDK MCP servers."""
    servers = all_servers()
    tools: list[str] = []
    for server in servers.values():
        tools.extend(server.tool_names)
    return tools
