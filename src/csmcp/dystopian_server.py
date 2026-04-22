"""Slim MCP stdio server for dystopian-crypto in mcp.json.

Runs the dystopian SDK server (5 Ed25519/Argon2id/AES-256-GCM tools)
in stdio transport mode for Claude Code integration.

Usage (mcp.json):
    uv run python -m csmcp.dystopian_server
"""
from __future__ import annotations

import asyncio
import logging
from csmcp import getLogger

logger = getLogger("csmcp.dystopian_server")


async def _run_stdio() -> None:
    from mcp.server.stdio import stdio_server
    from csmcp.dystopian import dystopian_server

    server_instance = dystopian_server["instance"]
    init_opts = server_instance.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.run(read_stream, write_stream, init_opts)


def main() -> None:
    """Entry point — run the dystopian-crypto MCP server over stdin/stdout."""
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
