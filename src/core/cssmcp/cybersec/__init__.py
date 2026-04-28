"""cybersec in-process MCP server package.

Assembles all 87 tools into a single SdkMcpServer instance.
Usage (SDK query):
    from core.cssmcp.cybersec import cybersec_server
    options = ClaudeAgentOptions(
        mcp_servers={"cybersec": cybersec_server},
        allowed_tools=cybersec_server.tool_names,
    )
"""
from __future__ import annotations

from core.cssmcp.sdk_compat import create_sdk_mcp_server
from core.cssmcp.cybersec.findings import ALL_TOOLS as _findings_tools
from core.cssmcp.cybersec.db import ALL_TOOLS as _db_tools
from core.cssmcp.cybersec.intelligence import ALL_TOOLS as _intelligence_tools
from core.cssmcp.cybersec.layers import ALL_TOOLS as _layers_tools
from core.cssmcp.cybersec.cache import ALL_TOOLS as _cache_tools
from core.cssmcp.cybersec.proxy import ALL_TOOLS as _proxy_tools
from core.cssmcp.cybersec.session import ALL_TOOLS as _session_tools
from core.cssmcp.cybersec.cases import ALL_TOOLS as _cases_tools
from core.cssmcp.cybersec.poc import ALL_TOOLS as _poc_tools
from core.cssmcp.cybersec.quo_pricing import ALL_TOOLS as _quo_pricing_tools
from core.cssmcp.cybersec.ai_memory import ALL_TOOLS as _ai_memory_tools
from core.cssmcp.cybersec.web_search import ALL_TOOLS as _web_search_tools
from core.cssmcp.cybersec.sync import ALL_TOOLS as _sync_tools
from core.cssmcp.cybersec.health import ALL_TOOLS as _health_tools
from core.cssmcp.cybersec.template import ALL_TOOLS as _template_tools
from core.cssmcp.cybersec.skill_manager import ALL_TOOLS as _skill_tools
from core.cssmcp.cybersec.vault_tool import ALL_TOOLS as _vault_tools
from core.cssmcp.cybersec.canvas_tool import ALL_TOOLS as _canvas_tools
from core.cssmcp.cybersec.tool_toggles import ALL_TOOLS as _toggle_tools
from core.cssmcp.cybersec.structured_extract import ALL_TOOLS as _structured_tools
from core.cssmcp.cybersec.thinking_tool import ALL_TOOLS as _thinking_tools
from core.cssmcp.cybersec.tool_search import ALL_TOOLS as _tool_search_tools
from core.cssmcp.cybersec.agents_beta import ALL_TOOLS as _agents_beta_tools
from core.cssmcp.cybersec.qol_tools import ALL_TOOLS as _qol_tools
from core.cssmcp.cybersec.playwright_tool import ALL_TOOLS as _playwright_tools
from core.cssmcp.dystopian import _ALL_DYSTOPIAN_TOOLS as _dystopian_tools

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
    + _qol_tools
    + _playwright_tools
    + _dystopian_tools
)

cybersec_server = create_sdk_mcp_server(
    name="cybersec",
    version="0.1.0",
    tools=_ALL_CYBERSEC_TOOLS,
)

__all__ = ["cybersec_server", "_ALL_CYBERSEC_TOOLS"]
