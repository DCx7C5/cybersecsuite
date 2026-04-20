"""Intel Feed Sources CRUD API."""
from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_intel_sources_list(request: Request) -> JSONResponse:
    """GET /api/intel-sources — list all intel feed sources."""
    try:
        from db.models.intel_feed_source import IntelFeedSource
        rows = await IntelFeedSource.all().order_by("name").values()
        data = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in rows
        ]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"sources": data, "total": len(data)})


async def api_intel_sources_create(request: Request) -> JSONResponse:
    """POST /api/intel-sources — add a new intel feed source."""
    try:
        from db.models.intel_feed_source import IntelFeedSource
        body = await request.json()
        name = (body.get("name") or "").strip()
        url = (body.get("url") or "").strip()
        if not name or not url:
            return JSONResponse({"error": "name and url are required"}, status_code=400)
        source = await IntelFeedSource.create(
            name=name,
            url=url,
            feed_type=body.get("feed_type", "rss"),
            description=body.get("description", ""),
            tags=body.get("tags", []),
            is_active=body.get("is_active", True),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": source.id}, status_code=201)


async def api_intel_sources_update(request: Request) -> JSONResponse:
    """PATCH /api/intel-sources/{id} — update an intel feed source."""
    try:
        from db.models.intel_feed_source import IntelFeedSource
        source_id = int(request.path_params["id"])
        source = await IntelFeedSource.get_or_none(id=source_id)
        if source is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("name", "url", "feed_type", "description", "tags", "is_active"):
            if field in body:
                setattr(source, field, body[field])
        await source.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": source_id})


async def api_intel_sources_delete(request: Request) -> JSONResponse:
    """DELETE /api/intel-sources/{id} — delete an intel feed source."""
    try:
        from db.models.intel_feed_source import IntelFeedSource
        source_id = int(request.path_params["id"])
        deleted = await IntelFeedSource.filter(id=source_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


async def api_intel_sources_seed(request: Request) -> JSONResponse:
    """POST /api/intel-sources/seed — seed the default curated feed sources."""
    try:
        from db.seeds.intel_feed_sources import seed_intel_feed_sources
        count = await seed_intel_feed_sources()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "seeded": count})
