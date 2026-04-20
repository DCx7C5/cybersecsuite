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


# ── Cases CRUD ────────────────────────────────────────────────────────────────

async def api_cases_create(request: Request) -> JSONResponse:
    """POST /api/cases — create a new case intake."""
    try:
        from db.models.case_intake import CaseIntake
        body = await request.json()
        title = (body.get("title") or "").strip()
        problem = (body.get("problem_statement") or "").strip()
        if not title or not problem:
            return JSONResponse({"error": "title and problem_statement are required"}, status_code=400)
        case = await CaseIntake.create(
            title=title,
            problem_statement=problem,
            attack_hypothesis=body.get("attack_hypothesis", ""),
            known_facts=body.get("known_facts", []),
            suspected_iocs=body.get("suspected_iocs", []),
            affected_assets=body.get("affected_assets", []),
            timeline_hints=body.get("timeline_hints", []),
            scope_in=body.get("scope_in", []),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": case.id}, status_code=201)


async def api_cases_update(request: Request) -> JSONResponse:
    """PATCH /api/cases/{id} — update a case intake."""
    try:
        from db.models.case_intake import CaseIntake
        case_id = int(request.path_params["id"])
        case = await CaseIntake.get_or_none(id=case_id)
        if case is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("title", "problem_statement", "attack_hypothesis", "known_facts",
                      "suspected_iocs", "affected_assets", "timeline_hints", "scope_in"):
            if field in body:
                setattr(case, field, body[field])
        await case.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": case_id})


async def api_cases_delete(request: Request) -> JSONResponse:
    """DELETE /api/cases/{id} — delete a case intake."""
    try:
        from db.models.case_intake import CaseIntake
        case_id = int(request.path_params["id"])
        deleted = await CaseIntake.filter(id=case_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


# ── A2A Tasks CRUD ────────────────────────────────────────────────────────────

async def api_tasks_list(request: Request) -> JSONResponse:
    """GET /api/tasks — list A2A tasks."""
    try:
        from db.models.a2a_task import A2ATask
        tasks = await A2ATask.all().order_by("-updated_at").limit(100).values()
        rows = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in tasks
        ]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"tasks": rows, "total": len(rows)})


async def api_tasks_create(request: Request) -> JSONResponse:
    """POST /api/tasks — create a manual A2A task."""
    try:
        import uuid
        from db.models.a2a_task import A2ATask
        body = await request.json()
        task = await A2ATask.create(
            id=str(uuid.uuid4()),
            session_id=body.get("session_id"),
            state=body.get("state", "submitted"),
            history=body.get("history", []),
            artifacts=body.get("artifacts", []),
            metadata=body.get("metadata", {}),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": task.id}, status_code=201)


async def api_tasks_update(request: Request) -> JSONResponse:
    """PATCH /api/tasks/{id} — update a task state/metadata."""
    try:
        from db.models.a2a_task import A2ATask
        task_id = request.path_params["id"]
        task = await A2ATask.get_or_none(id=task_id)
        if task is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("state", "history", "artifacts", "metadata", "session_id"):
            if field in body:
                setattr(task, field, body[field])
        await task.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": task_id})


async def api_tasks_delete(request: Request) -> JSONResponse:
    """DELETE /api/tasks/{id} — delete a task."""
    try:
        from db.models.a2a_task import A2ATask
        task_id = request.path_params["id"]
        deleted = await A2ATask.filter(id=task_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


# ── PoC CRUD ──────────────────────────────────────────────────────────────────

async def api_pocs_create(request: Request) -> JSONResponse:
    """POST /api/pocs — create a new PoC record."""
    try:
        from db.models.poc import ProofOfConcept
        body = await request.json()
        poc = await ProofOfConcept.create(
            title=body.get("title", ""),
            description=body.get("description", ""),
            poc_url=body.get("poc_url", ""),
            source=body.get("source", ""),
            language=body.get("language", ""),
            status=body.get("status", "unverified"),
            severity=body.get("severity"),
            reliability_score=body.get("reliability_score"),
            is_weaponized=body.get("is_weaponized", False),
            requires_auth=body.get("requires_auth", False),
            requires_interaction=body.get("requires_interaction", False),
            affected_versions=body.get("affected_versions", []),
            tags=body.get("tags", []),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": poc.id}, status_code=201)


async def api_pocs_update(request: Request) -> JSONResponse:
    """PATCH /api/pocs/{id} — update a PoC record."""
    try:
        from db.models.poc import ProofOfConcept
        poc_id = int(request.path_params["id"])
        poc = await ProofOfConcept.get_or_none(id=poc_id)
        if poc is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("title", "description", "poc_url", "source", "language", "status",
                      "severity", "reliability_score", "is_weaponized", "requires_auth",
                      "requires_interaction", "affected_versions", "tags"):
            if field in body:
                setattr(poc, field, body[field])
        await poc.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": poc_id})


async def api_pocs_delete(request: Request) -> JSONResponse:
    """DELETE /api/pocs/{id} — delete a PoC."""
    try:
        from db.models.poc import ProofOfConcept
        poc_id = int(request.path_params["id"])
        deleted = await ProofOfConcept.filter(id=poc_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})
