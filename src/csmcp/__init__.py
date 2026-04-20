"""csmcp — cybersec in-process SDK MCP servers.

Usage:
    from csmcp import all_servers, allowed_tools, getLogger
    options = ClaudeAgentOptions(
        mcp_servers=all_servers(),
        allowed_tools=allowed_tools()
    )
"""
from __future__ import annotations

from logger import getLogger

from typing import Any


def all_servers() -> dict[str, Any]:
    """Return all configured SDK MCP server instances keyed by server name.

    Returns McpSdkServerConfig dicts when claude_agent_sdk is available,
    or SdkMcpServer shim objects otherwise.
    """
    from csmcp.cybersec import cybersec_server
    from csmcp.dystopian import dystopian_server

    return {
        "cybersec": cybersec_server,
        "dystopian": dystopian_server,
    }


def allowed_tools() -> list[str]:
    """Return all allowed tool names across all registered SDK MCP servers."""
    from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
    from csmcp.dystopian import _ALL_DYSTOPIAN_TOOLS

    tools: list[str] = []
    # SdkMcpTool (real SDK) has .name; shim ToolMetadata also has .name
    for t in _ALL_CYBERSEC_TOOLS:
        name = getattr(t, "name", None)
        if name:
            tools.append(f"mcp__cybersec__{name}")
    for t in _ALL_DYSTOPIAN_TOOLS:
        name = getattr(t, "name", None)
        if name:
            tools.append(f"mcp__dystopian__{name}")
    return tools
