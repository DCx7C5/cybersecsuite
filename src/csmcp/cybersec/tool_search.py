"""Tool search — searchable index for CyberSecSuite's 70+ MCP tools.

Based on the Anthropic SDK examples/tools_runner_search_tool.py pattern.
Allows Claude to find relevant tools by keyword without loading all 71 at once.
Uses the `tool-search-tool-2025-10-19` beta feature when tool_runner is used.
"""
from __future__ import annotations

import json
from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error

# ── Lazy tool index ──────────────────────────────────────────────────────────

_TOOL_INDEX: list[dict[str, str]] | None = None


def _build_tool_index() -> list[dict[str, str]]:
    """Build a searchable index of all registered MCP tools."""
    global _TOOL_INDEX
    if _TOOL_INDEX is not None:
        return _TOOL_INDEX

    try:
        from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
        from csmcp.dystopian import ALL_TOOLS as _DYSTOPIAN_TOOLS
        all_tools = list(_ALL_CYBERSEC_TOOLS) + list(_DYSTOPIAN_TOOLS)
    except ImportError:
        try:
            from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
            all_tools = list(_ALL_CYBERSEC_TOOLS)
        except ImportError:
            return []

    index: list[dict[str, str]] = []
    for t in all_tools:
        name = getattr(t, "_sdk_tool_name", None) or getattr(t, "name", str(t))
        desc = getattr(t, "_sdk_description", None) or getattr(t, "description", "")
        if name:
            index.append({"name": name, "description": str(desc)})

    _TOOL_INDEX = index
    return index


def _search_tools(keyword: str) -> list[str]:
    """Return tool names matching the keyword (case-insensitive substring)."""
    keyword_lower = keyword.lower()
    index = _build_tool_index()
    return [
        entry["name"]
        for entry in index
        if keyword_lower in entry["name"].lower() or keyword_lower in entry["description"].lower()
    ]


# ── Tool implementations ──────────────────────────────────────────────────────


@tool(
    "search_tools",
    (
        "Search through all available CyberSecSuite MCP tools by keyword. "
        "Returns matching tool names and descriptions. Use this to discover "
        "which tool to call before invoking it directly."
    ),
    {
        "keyword": {
            "type": "string",
            "description": "Keyword to search for in tool names and descriptions",
        },
        "limit": {
            "type": "integer",
            "description": "Max results to return (default 20)",
            "default": 20,
        },
    },
)
async def search_tools(args: dict[str, Any]) -> JsonDict:
    keyword = str(args.get("keyword", "")).strip()
    if not keyword:
        return sdk_error("keyword is required")

    limit = max(1, min(int(args.get("limit", 20)), 100))
    index = _build_tool_index()

    keyword_lower = keyword.lower()
    matches: list[dict[str, str]] = [
        entry for entry in index
        if keyword_lower in entry["name"].lower() or keyword_lower in entry["description"].lower()
    ][:limit]

    return sdk_result({
        "keyword": keyword,
        "total_tools": len(index),
        "matches": len(matches),
        "tools": matches,
    })


@tool(
    "list_tool_categories",
    "List all CyberSecSuite tool categories with tool counts and representative names.",
    {},
)
async def list_tool_categories(args: dict[str, Any]) -> JsonDict:
    index = _build_tool_index()

    # Group by prefix (first word before underscore)
    categories: dict[str, list[str]] = {}
    for entry in index:
        name = entry["name"]
        prefix = name.split("_")[0] if "_" in name else name
        categories.setdefault(prefix, []).append(name)

    summary = [
        {"category": cat, "count": len(tools), "examples": tools[:3]}
        for cat, tools in sorted(categories.items())
    ]

    return sdk_result({
        "total_tools": len(index),
        "categories": len(summary),
        "breakdown": summary,
    })


@tool(
    "describe_tool",
    "Get the full description and parameter schema for a specific tool by name.",
    {
        "tool_name": {"type": "string", "description": "Exact name of the tool to describe"},
    },
)
async def describe_tool(args: dict[str, Any]) -> JsonDict:
    tool_name = str(args.get("tool_name", "")).strip()
    if not tool_name:
        return sdk_error("tool_name is required")

    try:
        from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
        all_tools = list(_ALL_CYBERSEC_TOOLS)
    except ImportError:
        return sdk_error("Could not load tool registry")

    for t in all_tools:
        name = getattr(t, "_sdk_tool_name", None) or getattr(t, "name", "")
        if name == tool_name:
            desc = getattr(t, "_sdk_description", "")
            schema = getattr(t, "_sdk_input_schema", {})
            return sdk_result({
                "name": name,
                "description": desc,
                "input_schema": json.loads(json.dumps(schema, default=str)),
            })

    # Fuzzy fallback
    matches = _search_tools(tool_name)
    if matches:
        return sdk_error(
            f"Tool '{tool_name}' not found. Did you mean: {', '.join(matches[:5])}?"
        )
    return sdk_error(f"Tool '{tool_name}' not found")


ALL_TOOLS = [search_tools, list_tool_categories, describe_tool]
