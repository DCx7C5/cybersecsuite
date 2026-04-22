"""Projects API — CRUD for Project model (db.models.scope.Project)."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from db.models.scope import Project


async def api_projects_list(request: Request) -> JSONResponse:
    """GET /api/projects — list all active projects."""
    try:
        projects = await Project.filter(deleted_at=None).order_by("-updated_at").values(
            "id", "name", "description", "path", "is_active", "created_at", "updated_at"
        )
        return JSONResponse({"projects": projects})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_project_create(request: Request) -> JSONResponse:
    """POST /api/projects — create a new project."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    path = (body.get("path") or "").strip()
    description = (body.get("description") or "").strip()
    create_dir = body.get("create_dir", False)

    try:
        project = await Project.create(
            name=name,
            description=description,
            path=path,
            is_active=True,
        )
    except Exception as e:
        return JSONResponse({"error": f"DB error: {e}"}, status_code=500)

    if create_dir and path:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            (Path(path) / ".claude").mkdir(exist_ok=True)
        except Exception as e:
            return JSONResponse({
                "ok": True,
                "project": {"id": project.id, "name": project.name, "path": project.path},
                "warning": f"Project created but dir setup failed: {e}",
            })

    return JSONResponse({
        "ok": True,
        "project": {"id": project.id, "name": project.name, "path": project.path},
    }, status_code=201)


async def api_project_get(request: Request) -> JSONResponse:
    """GET /api/projects/{id} — get a single project."""
    try:
        project_id = int(request.path_params["id"])
        project = await Project.get_or_none(id=project_id, deleted_at=None)
        if not project:
            return JSONResponse({"error": "not found"}, status_code=404)
        return JSONResponse({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "path": project.path,
            "is_active": project.is_active,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_project_update(request: Request) -> JSONResponse:
    """PATCH /api/projects/{id} — update a project."""
    try:
        project_id = int(request.path_params["id"])
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid request"}, status_code=400)

    project = await Project.get_or_none(id=project_id, deleted_at=None)
    if not project:
        return JSONResponse({"error": "not found"}, status_code=404)

    allowed = {"name", "description", "path", "is_active"}
    for key, value in body.items():
        if key in allowed:
            setattr(project, key, value)

    try:
        await project.save()
        return JSONResponse({"ok": True, "id": project.id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_project_delete(request: Request) -> JSONResponse:
    """DELETE /api/projects/{id} — soft-delete a project, optionally remove dir."""
    try:
        project_id = int(request.path_params["id"])
    except Exception:
        return JSONResponse({"error": "invalid id"}, status_code=400)

    project = await Project.get_or_none(id=project_id, deleted_at=None)
    if not project:
        return JSONResponse({"error": "not found"}, status_code=404)

    from datetime import datetime, timezone
    project.deleted_at = datetime.now(timezone.utc)
    project.is_active = False

    try:
        await project.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    body: dict = {}
    try:
        body = await request.json()
    except Exception:
        pass

    warning = None
    if body.get("remove_dir") and project.path:
        import shutil
        try:
            shutil.rmtree(project.path)
        except Exception as e:
            warning = f"Soft-deleted but dir removal failed: {e}"

    result: dict = {"ok": True, "deleted_id": project_id}
    if warning:
        result["warning"] = warning
    return JSONResponse(result)
