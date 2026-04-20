"""Prompts CRUD API."""
from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_prompts_list(request: Request) -> JSONResponse:
    """GET /api/prompts — list all prompts."""
    try:
        from db.models.prompt import Prompt
        rows = await Prompt.all().order_by("name").values()
        data = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in rows
        ]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"prompts": data, "total": len(data)})


async def api_prompts_create(request: Request) -> JSONResponse:
    """POST /api/prompts — create a new prompt."""
    try:
        from db.models.prompt import Prompt
        body = await request.json()
        name = (body.get("name") or "").strip()
        content = (body.get("content") or "").strip()
        if not name or not content:
            return JSONResponse({"error": "name and content are required"}, status_code=400)
        prompt = await Prompt.create(
            name=name,
            content=content,
            category=body.get("category", "general"),
            tags=body.get("tags", []),
            is_active=body.get("is_active", True),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": prompt.id}, status_code=201)


async def api_prompts_update(request: Request) -> JSONResponse:
    """PATCH /api/prompts/{id} — update a prompt."""
    try:
        from db.models.prompt import Prompt
        prompt_id = int(request.path_params["id"])
        prompt = await Prompt.get_or_none(id=prompt_id)
        if prompt is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("name", "content", "category", "tags", "is_active"):
            if field in body:
                setattr(prompt, field, body[field])
        await prompt.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": prompt_id})


async def api_prompts_delete(request: Request) -> JSONResponse:
    """DELETE /api/prompts/{id} — delete a prompt."""
    try:
        from db.models.prompt import Prompt
        prompt_id = int(request.path_params["id"])
        deleted = await Prompt.filter(id=prompt_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})
