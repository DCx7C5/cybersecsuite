"""Database health and bootstrap tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from mcp._sdk_compat import tool
from mcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "db_healthcheck",
    "Check PostgreSQL/Tortoise health and optional table/intelligence counts.",
    {
        "check_connection": {"type": "boolean", "default": True},
        "create_db": {"type": "boolean", "default": False},
        "bootstrap_intel": {"type": "boolean", "default": False},
        "include_counts": {"type": "boolean", "default": True},
    },
)
async def db_healthcheck(args: dict[str, Any]) -> JsonDict:
    try:
        from db.bootstrap import get_database_health_async
    except ImportError:
        return sdk_error("db.bootstrap not available — ensure src/ is in PYTHONPATH")

    health = await get_database_health_async(
        create_db=args.get("create_db", False),
        bootstrap_intel=args.get("bootstrap_intel", False),
        include_counts=args.get("include_counts", True),
        check_connection=args.get("check_connection", True),
    )
    return sdk_result(health)


@tool(
    "bootstrap_intelligence",
    "Bootstrap NVD/CVE, CWE, CAPEC, MITRE families and shared feeds into PostgreSQL.",
    {
        "force": {"type": "boolean", "default": False},
        "include_feeds": {"type": "boolean", "default": True},
        "create_db": {"type": "boolean", "default": True},
    },
)
async def bootstrap_intelligence(args: dict[str, Any]) -> JsonDict:
    try:
        from db.bootstrap import (
            init_tortoise_async,
            get_database_health_async,
            bootstrap_intelligence_async,
        )
    except ImportError:
        return sdk_error("db.bootstrap not available — ensure src/ is in PYTHONPATH")

    await init_tortoise_async(create_db=args.get("create_db", True), bootstrap_intel=False)
    summary = await bootstrap_intelligence_async(
        force=args.get("force", False),
        include_feeds=args.get("include_feeds", True),
    )
    health = await get_database_health_async(
        create_db=False, bootstrap_intel=False, include_counts=True, check_connection=True,
    )
    return sdk_result({"status": "success", "bootstrap": summary, "health": health})


ALL_TOOLS = [db_healthcheck, bootstrap_intelligence]
