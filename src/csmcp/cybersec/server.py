"""Slim MCP stdio server for Claude Code mcp.json integration.

Replaces mcp_server.py (1257L FastMCP duplicate). All tool logic lives in
src/csmcp/cybersec/*.py decorated with @tool. This file just runs the SDK
server created by create_sdk_mcp_server() in stdio transport mode.

Usage (mcp.json):
    uv run python -m csmcp.cybersec.server
"""
from __future__ import annotations

import asyncio
from csmcp import getLogger

logger = getLogger("csmcp.cybersec.server")


async def _run_stdio() -> None:
    from mcp.server.stdio import stdio_server
    from csmcp.cybersec import cybersec_server

    server_instance = cybersec_server["instance"]
    init_opts = server_instance.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.run(read_stream, write_stream, init_opts)


def main() -> None:
    """Entry point — run the cybersec MCP server over stdin/stdout."""
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
