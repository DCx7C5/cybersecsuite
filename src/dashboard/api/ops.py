"""Operational API handlers: cases, tasks, task lifecycle, PoCs."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_cases(request: Request) -> JSONResponse:
    """Phase 0 case intake list."""
    try:
        from db.models.case_intake import CaseIntake
        cases = await CaseIntake.all().order_by("-created_at").limit(20)
        case_list = [
            {
                "id": c.id,
                "title": c.title,
                "problem_statement": c.problem_statement[:200],
                "attack_hypothesis": c.attack_hypothesis[:200],
                "priority": c.priority.value if hasattr(c.priority, "value") else c.priority,
                "mode": c.mode.value if hasattr(c.mode, "value") else c.mode,
                "known_facts": c.known_facts,
                "suspected_iocs": c.suspected_iocs,
                "affected_assets": c.affected_assets,
                "mitre_hypotheses": c.mitre_hypotheses,
                "tags": c.tags,
                "opened_by": c.opened_by,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "closed_at": c.closed_at.isoformat() if c.closed_at else None,
            }
            for c in cases
        ]
        total = await CaseIntake.all().count()
        open_cases = await CaseIntake.filter(closed_at__isnull=True).count()
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total": total,
        "open": open_cases,
        "closed": total - open_cases,
        "cases": case_list,
    })


async def api_tasks(request: Request) -> JSONResponse:
    """A2A task management list (recent 50)."""
    try:
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
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e), "tasks": [], "total": 0, "by_state": {}})

    return JSONResponse({
        "total": total,
        "by_state": by_state,
        "tasks": task_list,
    })


async def api_task_cancel(request: Request) -> JSONResponse:
    """Cancel a task by ID."""
    try:
        from db.models.a2a_task import A2ATask
        task_id = request.path_params.get("task_id")
        task = await A2ATask.get_or_none(id=task_id)
        if not task:
            return JSONResponse({"status": "error", "error": "Task not found"}, status_code=404)
        if task.state in ("completed", "failed", "canceled"):
            return JSONResponse({"status": "error", "error": f"Task already in terminal state: {task.state}"}, status_code=400)
        task.state = "canceled"
        await task.save()
        return JSONResponse({"status": "success", "task_id": task_id, "state": "canceled"})
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


async def api_task_create(request: Request) -> JSONResponse:
    """Submit a new A2A task — body: {agent, message, session_id?, metadata?}."""
    try:
        import uuid
        body = await request.json()
        agent: str = body.get("agent", "cybersec-agent")
        message: str = body.get("message", "")
        session_id: str = body.get("session_id") or str(uuid.uuid4())
        metadata: dict = body.get("metadata") or {}

        if not message:
            return JSONResponse({"status": "error", "error": "message is required"}, status_code=400)

        from db.models.a2a_task import A2ATask
        task_id = str(uuid.uuid4())
        task = await A2ATask.create(
            id=task_id,
            session_id=session_id,
            state="submitted",
            history=[{"role": "user", "content": message}],
            artifacts=[],
            metadata={"agent": agent, **metadata},
        )
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)
    return JSONResponse({"task_id": task.id, "status": task.state}, status_code=201)


async def api_task_get(request: Request) -> JSONResponse:
    """Get a single A2A task by ID."""
    try:
        task_id = request.path_params["task_id"]
        from db.models.a2a_task import A2ATask
        task = await A2ATask.get_or_none(id=task_id)
        if task is None:
            return JSONResponse({"status": "error", "error": "task not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)
    return JSONResponse({
        "id": task.id,
        "state": task.state,
        "session_id": task.session_id,
        "agent": (task.metadata or {}).get("agent"),
        "history_count": len(task.history or []),
        "artifacts_count": len(task.artifacts or []),
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    })


async def api_pocs(request: Request) -> JSONResponse:
    """PoC exploit records — totals by status/severity + recent 50."""
    try:
        from db.models.poc import ProofOfConcept

        total = await ProofOfConcept.all().count()
        weaponized = await ProofOfConcept.filter(is_weaponized=True).count()

        by_status: dict[str, int] = {}
        for st in ("unverified", "verified", "weaponized", "patched", "disputed"):
            by_status[st] = await ProofOfConcept.filter(status=st).count()

        by_severity: dict[str, int] = {}
        for sev in ("critical", "high", "medium", "low", "info"):
            by_severity[sev] = await ProofOfConcept.filter(severity=sev).count()

        recent = await ProofOfConcept.all().order_by("-created_at").limit(50)
        recent_list = [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status if isinstance(p.status, str) else p.status.value,
                "severity": p.severity if isinstance(p.severity, str) else (p.severity.value if p.severity else None),
                "poc_url": p.poc_url,
                "source": p.source,
                "language": p.language,
                "is_weaponized": p.is_weaponized,
                "reliability_score": p.reliability_score,
                "tags": p.tags,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total": total,
        "weaponized": weaponized,
        "by_status": by_status,
        "by_severity": by_severity,
        "recent": recent_list,
    })
