"""cybersec in-process MCP server package.

Assembles all 29 tools into a single SdkMcpServer instance.
Usage (SDK query):
    from mcp.cybersec import cybersec_server
    options = ClaudeAgentOptions(
        mcp_servers={"cybersec": cybersec_server},
        allowed_tools=cybersec_server.tool_names,
    )
"""
from __future__ import annotations

from mcp._sdk_compat import create_sdk_mcp_server
from mcp.cybersec.findings import ALL_TOOLS as _findings_tools
from mcp.cybersec.db import ALL_TOOLS as _db_tools
from mcp.cybersec.intelligence import ALL_TOOLS as _intelligence_tools
from mcp.cybersec.layers import ALL_TOOLS as _layers_tools
from mcp.cybersec.cache import ALL_TOOLS as _cache_tools
from mcp.cybersec.proxy import ALL_TOOLS as _proxy_tools
from mcp.cybersec.session import ALL_TOOLS as _session_tools
from mcp.cybersec.cases import ALL_TOOLS as _cases_tools

_ALL_CYBERSEC_TOOLS = (
    _findings_tools
    + _db_tools
    + _intelligence_tools
    + _layers_tools
    + _cache_tools
    + _proxy_tools
    + _session_tools
    + _cases_tools
)

cybersec_server = create_sdk_mcp_server(
    name="cybersec",
    version="1.0.0",
    tools=_ALL_CYBERSEC_TOOLS,
)

__all__ = ["cybersec_server", "_ALL_CYBERSEC_TOOLS"]
