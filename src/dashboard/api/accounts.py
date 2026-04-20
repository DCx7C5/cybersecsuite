"""Accounts REST API handlers."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from accounts.manager import get_manager as get_account_manager
from accounts.registry import get_registry


async def api_accounts_list(request: Request) -> JSONResponse:
    """List all accounts."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"accounts": [], "error": "not initialized"})

    accounts = await mgr.list_all()
    return JSONResponse({
        "accounts": [
            {
                "vault_key": a.vault_key,
                "provider_id": a.provider_id,
                "label": a.label,
                "active": a.active,
                "test_status": a.test_status,
                "last_tested_at": a.last_tested_at.isoformat() if a.last_tested_at else None,
            }
            for a in accounts
        ]
    })


async def api_accounts_create(request: Request) -> JSONResponse:
    """Create a new account."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"error": "not initialized"}, status_code=500)

    try:
        data = await request.json()
        entry = await mgr.add(
            provider_id=data["provider_id"],
            api_key=data["api_key"],
            label=data.get("label"),
        )
        return JSONResponse({
            "vault_key": entry.vault_key,
            "provider_id": entry.provider_id,
            "label": entry.label,
            "active": entry.active,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def api_accounts_get(request: Request, vault_key: str) -> JSONResponse:
    """Get a single account."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"error": "not initialized"}, status_code=500)

    from accounts.registry import get_registry

    entry = get_registry().get(vault_key)
    if entry is None:
        return JSONResponse({"error": "not found"}, status_code=404)

    return JSONResponse({
        "vault_key": entry.vault_key,
        "provider_id": entry.provider_id,
        "label": entry.label,
        "active": entry.active,
        "test_status": entry.test_status,
    })


async def api_accounts_update(request: Request, vault_key: str) -> JSONResponse:
    """Update an account (set active, rotate key)."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"error": "not initialized"}, status_code=500)

    data = await request.json()
    action = data.get("action")

    if action == "set_active":
        entry = await mgr.set_active(vault_key)
        if entry is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        return JSONResponse({"ok": True, "active": entry.active})

    if action == "rotate":
        new_key = data.get("api_key")
        if not new_key:
            return JSONResponse({"error": "api_key required"}, status_code=400)
        entry = await mgr.rotate(vault_key, new_key)
        if entry is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        return JSONResponse({"ok": True})

    if action == "test":
        result = await mgr.test(vault_key)
        return JSONResponse({"ok": result})

    return JSONResponse({"error": "unknown action"}, status_code=400)


async def api_accounts_delete(request: Request, vault_key: str) -> JSONResponse:
    """Delete an account."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"error": "not initialized"}, status_code=500)

    result = await mgr.delete(vault_key)
    if not result:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({"ok": True})


async def api_accounts_resolve(request: Request) -> JSONResponse:
    """Resolve API key for a provider."""
    mgr = get_account_manager()
    if mgr is None:
        return JSONResponse({"error": "not initialized"}, status_code=500)

    provider_id = request.query_params.get("provider_id")
    if not provider_id:
        return JSONResponse({"error": "provider_id required"}, status_code=400)

    key = await mgr.resolve(provider_id)
    if key is None:
        return JSONResponse({"error": "no key found"}, status_code=404)

    return JSONResponse({"provider_id": provider_id, "has_key": True})