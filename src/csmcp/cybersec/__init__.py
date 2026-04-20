"""cybersec in-process MCP server package.

Assembles all 52 tools into a single SdkMcpServer instance.
Usage (SDK query):
    from csmcp.cybersec import cybersec_server
    options = ClaudeAgentOptions(
        mcp_servers={"cybersec": cybersec_server},
        allowed_tools=cybersec_server.tool_names,
    )
"""
from __future__ import annotations

from csmcp._sdk_compat import create_sdk_mcp_server
from csmcp.cybersec.findings import ALL_TOOLS as _findings_tools
from csmcp.cybersec.db import ALL_TOOLS as _db_tools
from csmcp.cybersec.intelligence import ALL_TOOLS as _intelligence_tools
from csmcp.cybersec.layers import ALL_TOOLS as _layers_tools
from csmcp.cybersec.cache import ALL_TOOLS as _cache_tools
from csmcp.cybersec.proxy import ALL_TOOLS as _proxy_tools
from csmcp.cybersec.session import ALL_TOOLS as _session_tools
from csmcp.cybersec.cases import ALL_TOOLS as _cases_tools
from csmcp.cybersec.poc import ALL_TOOLS as _poc_tools
from csmcp.cybersec.routing import ALL_TOOLS as _routing_tools
from csmcp.cybersec.quo_pricing import ALL_TOOLS as _quo_pricing_tools
from csmcp.cybersec.ai_memory import ALL_TOOLS as _ai_memory_tools
from csmcp.cybersec.web_search import ALL_TOOLS as _web_search_tools
from csmcp.cybersec.sync import ALL_TOOLS as _sync_tools
from csmcp.cybersec.health import ALL_TOOLS as _health_tools
from csmcp.cybersec.template import ALL_TOOLS as _template_tools
from csmcp.cybersec.skill_manager import ALL_TOOLS as _skill_tools
from csmcp.cybersec.vault_tool import ALL_TOOLS as _vault_tools
from csmcp.cybersec.canvas_tool import ALL_TOOLS as _canvas_tools
from csmcp.cybersec.tool_toggles import ALL_TOOLS as _toggle_tools
from csmcp.cybersec.structured_extract import ALL_TOOLS as _structured_tools
from csmcp.cybersec.thinking_tool import ALL_TOOLS as _thinking_tools
from csmcp.cybersec.tool_search import ALL_TOOLS as _tool_search_tools
from csmcp.cybersec.agents_beta import ALL_TOOLS as _agents_beta_tools

_ALL_CYBERSEC_TOOLS = (
    _findings_tools
    + _db_tools
    + _intelligence_tools
    + _layers_tools
    + _cache_tools
    + _proxy_tools
    + _session_tools
    + _cases_tools
    + _poc_tools
    + _routing_tools
    + _quo_pricing_tools
    + _ai_memory_tools
    + _web_search_tools
    + _sync_tools
    + _health_tools
    + _template_tools
    + _skill_tools
    + _vault_tools
    + _canvas_tools
    + _toggle_tools
    + _structured_tools
    + _thinking_tools
    + _tool_search_tools
    + _agents_beta_tools
)

cybersec_server = create_sdk_mcp_server(
    name="cybersec",
    version="1.0.0",
    tools=_ALL_CYBERSEC_TOOLS,
)

__all__ = ["cybersec_server", "_ALL_CYBERSEC_TOOLS"]
