"""Bootstrap API — check and trigger first-run database seeding."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from starlette.requests import Request
from starlette.responses import JSONResponse

# Module-level task handle so we can report progress
_bootstrap_task: asyncio.Task | None = None
_bootstrap_log: list[str] = []
_bootstrap_error: str | None = None


async def _is_bootstrapped() -> tuple[bool, dict]:
    """Check global_settings for 'db_bootstrapped' flag and row counts."""
    try:
        from db.models.settings import GlobalSettings

        record = await GlobalSettings.get_or_none(key="db_bootstrapped")
        if record and record.value.get("done"):
            return True, record.value

        # Also check if there's meaningful data already (NIST CSF seeded etc.)
        from db.models.nist_csf import NistCsfControl
        from db.models.nist_ai_rmf import NistAiRmfControl

        csf_count = await NistCsfControl.all().count()
        rmf_count = await NistAiRmfControl.all().count()
        if csf_count > 0 or rmf_count > 0:
            # Data exists but flag wasn't set — write the flag now
            await GlobalSettings.update_or_create(
                defaults={"value": {"done": True, "at": datetime.now(timezone.utc).isoformat(), "auto_detected": True}},
                key="db_bootstrapped",
            )
            return True, {"done": True, "csf_count": csf_count, "rmf_count": rmf_count}

        return False, {}
    except Exception as exc:
        return False, {"error": str(exc)}


async def api_bootstrap_status(request: Request) -> JSONResponse:
    """GET /api/bootstrap/status — check if DB has been bootstrapped."""
    global _bootstrap_task

    done, meta = await _is_bootstrapped()

    running = _bootstrap_task is not None and not _bootstrap_task.done()

    return JSONResponse({
        "done": done,
        "running": running,
        "meta": meta,
        "log": list(_bootstrap_log[-50:]),  # last 50 lines
        "error": _bootstrap_error,
    })


async def _do_bootstrap() -> None:
    """Background coroutine: run bootstrap and mark completion."""
    global _bootstrap_log, _bootstrap_error

    _bootstrap_log.clear()
    _bootstrap_error = None

    def _log(msg: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        _bootstrap_log.append(f"[{ts}] {msg}")

    try:
        _log("Starting database bootstrap…")

        from db.bootstrap import bootstrap_intelligence_async
        _log("Loading NIST CSF 2.0…")
        await bootstrap_intelligence_async(force=False, include_feeds=False)
        _log("Intelligence data loaded ✓")

        from db.models.settings import GlobalSettings
        await GlobalSettings.update_or_create(
            defaults={"value": {"done": True, "at": datetime.now(timezone.utc).isoformat()}},
            key="db_bootstrapped",
        )
        _log("Bootstrap complete ✓")

    except Exception as exc:
        _bootstrap_error = str(exc)
        _bootstrap_log.append(f"[ERROR] {exc}")


async def api_bootstrap_run(request: Request) -> JSONResponse:
    """POST /api/bootstrap/run — start bootstrap in background."""
    global _bootstrap_task

    if _bootstrap_task is not None and not _bootstrap_task.done():
        return JSONResponse({"started": False, "reason": "already running"}, status_code=409)

    done, _ = await _is_bootstrapped()
    if done:
        return JSONResponse({"started": False, "reason": "already done"})

    _bootstrap_task = asyncio.create_task(_do_bootstrap())
    return JSONResponse({"started": True})


async def api_bootstrap_skip(request: Request) -> JSONResponse:
    """POST /api/bootstrap/skip — mark bootstrapped without running (skip prompt)."""
    from db.models.settings import GlobalSettings
    await GlobalSettings.update_or_create(
        defaults={"value": {"done": True, "at": datetime.now(timezone.utc).isoformat(), "skipped": True}},
        key="db_bootstrapped",
    )
    return JSONResponse({"skipped": True})
