"""Dashboard HTML page handler — serves React SPA."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse

_REACT_INDEX = Path("src/dashboard/static/react/index.html")


async def dashboard_page(request: Request) -> FileResponse | HTMLResponse:
    """Serve the React SPA index.html, fall back to legacy if not built yet."""
    if _REACT_INDEX.exists():
        return FileResponse(str(_REACT_INDEX))
    from dashboard._html import _DASHBOARD_HTML
    return HTMLResponse(_DASHBOARD_HTML)
