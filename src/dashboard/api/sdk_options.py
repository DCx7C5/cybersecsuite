"""SDK runtime options API endpoints."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from agent.options_manager import RuntimeOptionsManager


class OptionsUpdateRequest(BaseModel):
    """Request body for updating options."""
    mcps: Optional[dict[str, bool]] = None
    agents: Optional[dict[str, bool]] = None
    permission_mode: Optional[str] = None
    model: Optional[str] = None
    hooks: Optional[list[str]] = None


async def api_sdk_options_get(request: Request) -> JSONResponse:
    """GET /api/sdk/options - current merged options for scope."""
    scope_id = request.query_params.get("id")
    project_id = int(scope_id) if scope_id and scope_id.isdigit() else None

    manager = RuntimeOptionsManager.get_instance()
    merged = await manager.resolve(scope_id=project_id)

    return JSONResponse(merged)


async def api_sdk_options_post(request: Request) -> JSONResponse:
    """POST /api/sdk/options - update options for a scope."""
    scope = request.query_params.get("scope", "global")
    if scope not in ("global", "app", "project"):
        raise HTTPException(400, "Invalid scope")

    scope_id: int | None = None
    if scope == "project":
        id_param = request.query_params.get("id")
        if not id_param or not id_param.isdigit():
            raise HTTPException(400, "project scope requires id parameter")
        scope_id = int(id_param)

    body = await request.json()
    update_data = OptionsUpdateRequest(**body).model_dump(exclude_none=True)

    manager = RuntimeOptionsManager.get_instance()
    await manager.update(scope, scope_id, **update_data)

    merged = await manager.resolve(scope_id=scope_id)
    return JSONResponse(merged)


async def api_sdk_options_scopes_get(request: Request) -> JSONResponse:
    """GET /api/sdk/options/scopes - raw snapshot of all layers."""
    manager = RuntimeOptionsManager.get_instance()
    snapshot = await manager.get_snapshot()
    return JSONResponse(snapshot)


async def api_sdk_options_delete(request: Request) -> JSONResponse:
    """DELETE /api/sdk/options - reset a scope to defaults."""
    scope = request.query_params.get("scope", "global")
    if scope not in ("global", "app", "project"):
        raise HTTPException(400, "Invalid scope")

    scope_id: int | None = None
    if scope == "project":
        id_param = request.query_params.get("id")
        if not id_param or not id_param.isdigit():
            raise HTTPException(400, "project scope requires id parameter")
        scope_id = int(id_param)

    manager = RuntimeOptionsManager.get_instance()
    await manager.reset(scope, scope_id)

    merged = await manager.resolve(scope_id=scope_id)
    return JSONResponse(merged)


api_sdk_options = api_sdk_options_get
api_sdk_options_scopes = api_sdk_options_scopes_get