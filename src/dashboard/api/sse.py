"""SSE (Server-Sent Events) streaming handlers: cases, tasks, health, telemetry."""
from __future__ import annotations

import asyncio
import json
import time

from starlette.requests import Request
from starlette.responses import StreamingResponse

from ai_proxy.providers.registry import (
    get_enabled_providers,
    get_free_providers,
)
from dashboard.api.core import _APP_START


async def sse_cases(request: Request) -> StreamingResponse:
    """Server-Sent Events stream for case intake updates."""
    async def event_generator():
        try:
            while True:
                from db.models.case_intake import CaseIntake
                cases = await CaseIntake.all().order_by("-created_at").limit(20)
                total = await CaseIntake.all().count()
                open_cases = await CaseIntake.filter(closed_at__isnull=True).count()

                case_list = [
                    {
                        "id": c.id,
                        "title": c.title,
                        "problem_statement": c.problem_statement[:200],
                        "priority": c.priority.value if hasattr(c.priority, "value") else c.priority,
                        "mode": c.mode.value if hasattr(c.mode, "value") else c.mode,
                        "facts_count": len(c.known_facts or []),
                        "iocs_count": len(c.suspected_iocs or []),
                        "assets_count": len(c.affected_assets or []),
                        "mitre_count": len(c.mitre_hypotheses or []),
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                        "closed_at": c.closed_at.isoformat() if c.closed_at else None,
                    }
                    for c in cases
                ]

                data = {
                    "total": total,
                    "open": open_cases,
                    "closed": total - open_cases,
                    "cases": case_list,
                }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


async def sse_tasks(request: Request) -> StreamingResponse:
    """Server-Sent Events stream for task management updates."""
    async def event_generator():
        try:
            while True:
                from db.models.a2a_task import A2ATask
                tasks = await A2ATask.all().order_by("-updated_at").limit(50)
                total = await A2ATask.all().count()
                by_state: dict[str, int] = {}
                for state in ("submitted", "working", "completed", "failed", "canceled"):
                    by_state[state] = await A2ATask.filter(state=state).count()

                task_list = [
                    {
                        "id": t.id,
                        "state": t.state,
                        "agent": getattr(t, "agent_id", None) or getattr(t, "agent", None),
                        "created_at": t.created_at.isoformat() if t.created_at else None,
                        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                    }
                    for t in tasks
                ]

                data = {
                    "total": total,
                    "by_state": by_state,
                    "tasks": task_list,
                }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


async def sse_health(request: Request) -> StreamingResponse:
    """Server-Sent Events stream for health monitoring."""
    async def event_generator():
        try:
            while True:
                from db.bootstrap import get_database_health_async
                db_health = await get_database_health_async(check_connection=True, include_counts=False)
                enabled = get_enabled_providers()

                data = {
                    "database": db_health,
                    "proxy": {
                        "providers_enabled": len(enabled),
                        "providers_free": len(get_free_providers()),
                        "uptime_seconds": round(time.monotonic() - _APP_START, 1),
                    },
                }
                yield f"data: {json.dumps(data, default=str)}\n\n"
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            return
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


async def sse_telemetry(request: Request) -> StreamingResponse:
    """SSE stream of telemetry snapshots every 5 s."""
    async def event_generator():
        try:
            from telemetry import get_snapshot
            while True:
                snap = await get_snapshot()
                yield f"event: telemetry_update\ndata: {json.dumps(snap, default=str)}\n\n"
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
