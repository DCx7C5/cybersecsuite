"""Dashboard HTML page handler — serves React SPA."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse

_REACT_INDEX = Path("src/dashboard/static/react/index.html")


async def dashboard_page(request: Request) -> FileResponse:
    """Serve the React SPA index.html. React build is required."""
    return FileResponse(str(_REACT_INDEX))
