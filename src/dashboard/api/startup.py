"""Startup status API handlers."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from startup.first_run import first_run_setup, get_marketplace, is_first_run


async def api_startup_status(request: Request) -> JSONResponse:
    """Return startup status including first-run info and marketplace."""
    result = await first_run_setup()
    return JSONResponse(result)