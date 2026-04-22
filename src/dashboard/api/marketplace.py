"""Marketplace REST endpoints — browse, install, and manage marketplace items.

Routes:
    GET    /api/marketplace                   → list items (kind, provider, tags, status, q)
    GET    /api/marketplace/installed         → list installed items
    GET    /api/marketplace/{item_id}         → get single item
    POST   /api/marketplace/{item_id}/install → install item
    DELETE /api/marketplace/{item_id}/install → uninstall item
    POST   /api/marketplace/generate-agent    → stub: Agent Factory generation

Referenz:
    plan.md T034 — Dashboard API: marketplace endpoints
    plan.md T038 — Agent Factory stub endpoint
    src/marketplace/registry.py — get_registry
    src/dashboard/api/qol.py — route-handler pattern
"""
from __future__ import annotations

import logging

from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("marketplace.api")


def _reg():
    """Lazy import to keep startup cost low."""
    from marketplace.registry import get_registry
    return get_registry()


async def api_marketplace_list(request: Request) -> JSONResponse:
    """GET /api/marketplace — list marketplace items with optional filters.

    Query params:
        kind:     agent | skill | combo | template
        provider: claude | copilot | cursor | openai | gemini | grok | universal
        tags:     comma-separated list of tag strings
        status:   available | installed | update_available | deprecated
        q:        free-text search query (substring match)
    """
    params = request.query_params
    kind = params.get("kind") or None
    provider = params.get("provider") or None
    tags_raw = params.get("tags") or None
    status_raw = params.get("status") or None
    query = params.get("q") or None

    tags: list[str] | None = (
        [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else None
    )

    try:
        from marketplace.models import MarketplaceItemStatus

        status = MarketplaceItemStatus(status_raw) if status_raw else None
    except ValueError:
        return JSONResponse(
            {"error": f"Invalid status value: {status_raw!r}"},
            status_code=400,
        )

    try:
        reg = _reg()
        if query:
            items = reg.search(query)
            # Apply additional filters on top of search results.
            if kind:
                items = [i for i in items if i.kind == kind]
            if provider:
                items = [i for i in items if i.provider == provider]
            if tags:
                items = [i for i in items if all(t in i.tags for t in tags)]
            if status:
                items = [i for i in items if i.status == status]
        else:
            items = reg.list_items(kind=kind, provider=provider, tags=tags, status=status)

        return JSONResponse(
            {
                "items": [i.model_dump(mode="json") for i in items],
                "count": len(items),
            }
        )
    except Exception as exc:
        logger.exception("Error listing marketplace items")
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_marketplace_installed(request: Request) -> JSONResponse:
    """GET /api/marketplace/installed — list all installed marketplace items."""
    try:
        items = _reg().list_installed()
        return JSONResponse(
            {
                "items": [i.model_dump(mode="json") for i in items],
                "count": len(items),
            }
        )
    except Exception as exc:
        logger.exception("Error listing installed marketplace items")
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_marketplace_get(request: Request) -> JSONResponse:
    """GET /api/marketplace/{item_id} — retrieve a single item by ID."""
    item_id: str = request.path_params.get("item_id", "").strip()
    if not item_id:
        return JSONResponse({"error": "item_id path parameter is required"}, status_code=400)
    try:
        item = _reg().get_item(item_id)
        if item is None:
            return JSONResponse(
                {"error": f"Marketplace item not found: {item_id!r}"},
                status_code=404,
            )
        return JSONResponse(item.model_dump(mode="json"))
    except Exception as exc:
        logger.exception("Error fetching marketplace item %s", item_id)
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_marketplace_install(request: Request) -> JSONResponse:
    """POST /api/marketplace/{item_id}/install — install a marketplace item."""
    item_id: str = request.path_params.get("item_id", "").strip()
    if not item_id:
        return JSONResponse({"error": "item_id path parameter is required"}, status_code=400)
    try:
        item = _reg().install(item_id)
        return JSONResponse({"ok": True, "item": item.model_dump(mode="json")}, status_code=200)
    except KeyError as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)
    except Exception as exc:
        logger.exception("Error installing marketplace item %s", item_id)
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_marketplace_uninstall(request: Request) -> JSONResponse:
    """DELETE /api/marketplace/{item_id}/install — uninstall a marketplace item."""
    item_id: str = request.path_params.get("item_id", "").strip()
    if not item_id:
        return JSONResponse({"error": "item_id path parameter is required"}, status_code=400)
    try:
        removed = _reg().uninstall(item_id)
        if not removed:
            return JSONResponse(
                {"error": f"Item {item_id!r} is not currently installed"},
                status_code=404,
            )
        return JSONResponse({"ok": True, "item_id": item_id})
    except Exception as exc:
        logger.exception("Error uninstalling marketplace item %s", item_id)
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_marketplace_generate_agent(request: Request) -> JSONResponse:
    """POST /api/marketplace/generate-agent — stub: Agent Factory generation.

    Full generation requires the agent-factory skill to be installed.
    """
    return JSONResponse(
        {
            "status": "not_implemented",
            "message": (
                "Agent Factory generation requires the agent-factory skill"
            ),
        },
        status_code=501,
    )
