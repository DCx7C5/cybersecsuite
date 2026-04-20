"""Template rendering MCP tools."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "render_template",
    "Render a Jinja2 template with extra variables",
    {
        "name": "string",
        "extra_vars": {"type": "object", "description": "Additional template variables"},
    },
)
async def render_template(args: dict[str, Any]) -> JsonDict:
    """Render a named template using template_engine."""
    try:
        from template_engine import render
    except ImportError:
        return sdk_error("template_engine not available")

    name = args.get("name", "")
    if not name:
        return sdk_error("name is required")

    extra_vars = args.get("extra_vars", {})
    try:
        rendered = render(name, extra_vars)
        return sdk_result({"name": name, "rendered": rendered})
    except Exception as e:
        return sdk_error(str(e))


ALL_TOOLS = [render_template]