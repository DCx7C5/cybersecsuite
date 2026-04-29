"""Slim MCP stdio server for Claude Code mcp.json integration.

Bridges the in-process SdkMcpServer (csmcp._sdk_compat) to the mcp package's
stdio transport so Claude Code can connect via mcp.json.

All tool logic lives in src/csmcp/cybersec/*.py decorated with @tool.
This file builds a real mcp.server.Server by reflecting over _ALL_CYBERSEC_TOOLS
and delegating call_tool() to SdkMcpServer.call_tool().

Usage (mcp.json):
    uv run python -m csmcp.cybersec.server
"""
from __future__ import annotations

import asyncio
import logging
from cssmcp import getLogger

logger = getLogger("csmcp.cybersec.server")


def _build_mcp_server():
    """Build a real mcp.server.Server backed by the SdkMcpServer shim."""
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from . import cybersec_server, _ALL_CYBERSEC_TOOLS

    app = Server("cybersec")

    # Build mcp.types.Tool list from registered tool metadata
    def _make_tool(t) -> Tool:
        schema = getattr(t, "_sdk_tool_schema", {}) or {}
        if not schema:
            # SdkMcpServer shim wraps ToolMetadata — extract from there
            meta = getattr(t, "schema", {})
            schema = meta if isinstance(meta, dict) else {}
        return Tool(
            name=getattr(t, "_sdk_tool_name", None) or getattr(t, "name", str(t)),
            description=getattr(t, "_sdk_tool_description", None) or getattr(t, "description", ""),
            inputSchema=schema if schema else {"type": "object", "properties": {}},
        )

    # For SdkMcpServer shim the tools are ToolMetadata objects in _tools dict
    if hasattr(cybersec_server, "_tools"):
        # shim path: SdkMcpServer
        tool_metas = list(cybersec_server._tools.values())
        mcp_tools = [
            Tool(
                name=m.name,
                description=m.description,
                inputSchema=m.schema if isinstance(m.schema, dict) else {"type": "object", "properties": {}},
            )
            for m in tool_metas
        ]
    else:
        # real SDK path: fall back to _ALL_CYBERSEC_TOOLS
        mcp_tools = [_make_tool(t) for t in _ALL_CYBERSEC_TOOLS]

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return mcp_tools

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = await cybersec_server.call_tool(name, arguments)
        # Normalize: result may be a dict with 'content' list or a plain dict
        contents = result.get("content", []) if isinstance(result, dict) else []
        if not contents:
            import json
            contents = [{"type": "text", "text": json.dumps(result)}]
        return [
            TextContent(type="text", text=c.get("text", "") if isinstance(c, dict) else str(c))
            for c in contents
        ]

    return app


async def _run_stdio() -> None:
    from mcp.server.stdio import stdio_server

    app = _build_mcp_server()
    init_opts = app.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, init_opts)


def main() -> None:
    """Entry point — run the cybersec MCP server over stdin/stdout."""
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
