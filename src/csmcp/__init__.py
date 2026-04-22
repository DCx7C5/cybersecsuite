"""csmcp — cybersec in-process SDK MCP server.

Usage:
    from csmcp import all_servers, allowed_tools, getLogger
    options = ClaudeAgentOptions(
        mcp_servers=all_servers(),
        allowed_tools=allowed_tools()
    )
"""
from __future__ import annotations

from logger import getLogger  # noqa: F401

from typing import Any


def all_servers() -> dict[str, Any]:
    """Return all configured SDK MCP server instances keyed by server name."""
    from csmcp.cybersec import cybersec_server
    return {"cybersec": cybersec_server}


def allowed_tools() -> list[str]:
    """Return all allowed tool names across all registered SDK MCP servers."""
    from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
    return [
        f"mcp__cybersec__{t._sdk_tool_name}"
        for t in _ALL_CYBERSEC_TOOLS
        if getattr(t, "_sdk_tool_name", None)
    ]
