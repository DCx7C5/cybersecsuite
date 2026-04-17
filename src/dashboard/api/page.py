"""Dashboard HTML page handler."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import HTMLResponse

from dashboard._html import _DASHBOARD_HTML


async def dashboard_page(request: Request) -> HTMLResponse:
    """Serve the dashboard SPA."""
    return HTMLResponse(_DASHBOARD_HTML)
