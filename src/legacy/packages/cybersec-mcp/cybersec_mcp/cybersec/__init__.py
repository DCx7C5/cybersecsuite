"""cybersec in-process MCP server package.

Assembles all 92+ tools into a single SdkMcpServer instance.
"""
from __future__ import annotations

from ..dystopian import _ALL_DYSTOPIAN_TOOLS as _dystopian_tools
from ..sdk_compat import create_sdk_mcp_server
from .agents_beta import ALL_TOOLS as _agents_beta_tools
from .ai_memory import ALL_TOOLS as _ai_memory_tools
from .cache import ALL_TOOLS as _cache_tools
from .canvas_tool import ALL_TOOLS as _canvas_tools
from .cases import ALL_TOOLS as _cases_tools
from .db import ALL_TOOLS as _db_tools
from .findings import ALL_TOOLS as _findings_tools
from .health import ALL_TOOLS as _health_tools
from .intelligence import ALL_TOOLS as _intelligence_tools
from .layers import ALL_TOOLS as _layers_tools
from .playwright_tool import ALL_TOOLS as _playwright_tools
from .poc import ALL_TOOLS as _poc_tools
from .proxy import ALL_TOOLS as _proxy_tools
from .qol_tools import ALL_TOOLS as _qol_tools
from .quo_pricing import ALL_TOOLS as _quo_pricing_tools
from .session import ALL_TOOLS as _session_tools
from .skill_manager import ALL_TOOLS as _skill_tools
from .structured_extract import ALL_TOOLS as _structured_tools
from .sync import ALL_TOOLS as _sync_tools
from .template import ALL_TOOLS as _template_tools
from .thinking_tool import ALL_TOOLS as _thinking_tools
from .tool_search import ALL_TOOLS as _tool_search_tools
from .tool_toggles import ALL_TOOLS as _toggle_tools
from .vault_tool import ALL_TOOLS as _vault_tools
from .web_search import ALL_TOOLS as _web_search_tools

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
