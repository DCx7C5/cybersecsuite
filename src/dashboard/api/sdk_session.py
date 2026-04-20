"""SDK session API - last session, scope activation."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_sdk_session_last(request: Request) -> JSONResponse:
    """GET /api/sdk/session/last — get last session info."""
    from cybersecsuite.sdk import CyberSecSuiteSDK

    try:
        sdk = CyberSecSuiteSDK()
        last = sdk.last_session()
        if last:
            return JSONResponse({
                "name": last.name,
                "path": last.path,
                "suspended_at": last.suspended_at,
            })
        return JSONResponse({"error": "No last session"})
    except Exception as e:
        return JSONResponse({"error": str(e)})


async def api_sdk_session_resume(request: Request) -> JSONResponse:
    """POST /api/sdk/session/resume — resume last session."""
    from cybersecsuite.sdk import CyberSecSuiteSDK, NoLastSessionError

    try:
        sdk = CyberSecSuiteSDK()
        last = sdk.last_session()
        if not last:
            return JSONResponse({"error": "No session to resume"}, status=404)
        return JSONResponse({
            "resumed": last.name,
            "path": last.path,
        })
    except NoLastSessionError:
        return JSONResponse({"error": "No session to resume"}, status=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status=500)