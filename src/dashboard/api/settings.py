"""Settings API: read and patch .claude/settings.json."""

from __future__ import annotations

import json
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

_SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / ".claude" / "settings.json"

_EDITABLE_KEYS = frozenset({"env", "agent", "proxy", "asgi", "cache", "security", "hooks_dir"})
_READONLY_KEYS = frozenset({"hooks", "crypto", "signing", "keys", "version", "enabledPlugins"})


def _load() -> dict:
    if not _SETTINGS_PATH.exists():
        return {}
    return json.loads(_SETTINGS_PATH.read_text())


def _dump(data: dict) -> None:
    _SETTINGS_PATH.write_text(json.dumps(data, indent=2) + "\n")


async def api_settings_get(request: Request) -> JSONResponse:
    """Return current settings (editable + readonly sections separated)."""
    try:
        data = _load()
        return JSONResponse({
            "settings": data,
            "editable_keys": sorted(_EDITABLE_KEYS),
            "readonly_keys": sorted(_READONLY_KEYS),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_settings_patch(request: Request) -> JSONResponse:
    """Apply partial update — only editable sections allowed."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    forbidden = set(body.keys()) & _READONLY_KEYS
    if forbidden:
        return JSONResponse(
            {"error": f"Cannot modify read-only keys: {sorted(forbidden)}"},
            status_code=400,
        )
    unknown = set(body.keys()) - _EDITABLE_KEYS
    if unknown:
        return JSONResponse(
            {"error": f"Unknown settings keys: {sorted(unknown)}"},
            status_code=400,
        )

    try:
        data = _load()
        for key, value in body.items():
            data[key] = value
        _dump(data)
        return JSONResponse({"ok": True, "updated": sorted(body.keys())})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
