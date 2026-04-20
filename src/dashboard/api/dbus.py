"""DBus notification API handlers."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from dbus.notifier import get_notifier


async def api_dbus_notify(request: Request) -> JSONResponse:
    """Send desktop notification."""
    try:
        data = await request.json()
        title = data.get("title", "CyberSecSuite")
        body = data.get("body", "")
        icon = data.get("icon", "dialog-information")
        urgency = data.get("urgency", 1)

        notifier = get_notifier()
        result = await notifier.notify(title, body, icon, urgency)
        return JSONResponse({"ok": result >= 0, "id": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def api_dbus_signal(request: Request) -> JSONResponse:
    """Emit custom DBus signal."""
    try:
        data = await request.json()
        signal_name = data.get("signal", "TaskComplete")
        args = data.get("args", [])

        notifier = get_notifier()
        await notifier.emit_signal(signal_name, args)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def api_dbus_status(request: Request) -> JSONResponse:
    """Check DBus availability."""
    try:
        notifier = get_notifier()
        available = await notifier.is_available()
        return JSONResponse({"available": available})
    except Exception as e:
        return JSONResponse({"available": False, "error": str(e)})