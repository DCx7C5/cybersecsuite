"""DB/table API handlers: db counts, investigations, models, generic table, prompts, telemetry."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_db_counts(request: Request) -> JSONResponse:
    """Per-table row counts via Tortoise ORM (no raw SQL)."""
    try:
        from db.bootstrap import get_database_health_async
        health = await get_database_health_async(check_connection=True, include_counts=True)
        return JSONResponse({
            "status": health.get("status", "ok"),
            "counts": health.get("counts", {}),
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})


async def api_investigations(request: Request) -> JSONResponse:
    """Investigation summary: findings, IOCs, risks via ORM."""
    try:
        from db.models.investigation import Finding, IOC, Risk, MITRETechnique
        findings_total = await Finding.filter(is_active=True).count()
        iocs_total = await IOC.filter(is_active=True).count()
        risks_total = await Risk.filter(is_active=True).count()
        techniques_total = await MITRETechnique.all().count()

        # Severity breakdown for findings
        severity_counts: dict[str, int] = {}
        for sev in ("critical", "high", "medium", "low", "info"):
            severity_counts[sev] = await Finding.filter(is_active=True, severity=sev).count()

    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "findings": findings_total,
        "iocs": iocs_total,
        "risks": risks_total,
        "mitre_techniques": techniques_total,
        "findings_by_severity": severity_counts,
    })


async def api_models(request: Request) -> JSONResponse:
    """List all registered DB models with table name and field count."""
    from dashboard._schema import list_models
    return JSONResponse({"models": list_models()})


async def api_table(request: Request) -> JSONResponse:
    """Generic paginated endpoint: GET /api/tables/{model}?page&limit&sort&filter_<field>=value.

    Returns {schema, rows, total, page, limit}.
    Supports all 82+ Tortoise models by name (CamelCase, snake_case, or db_table).
    """
    from dashboard._schema import resolve_model, fetch_rows

    model_name = request.path_params.get("model", "")
    info = resolve_model(model_name)
    if info is None:
        return JSONResponse(
            {"status": "error", "error": f"Unknown model: {model_name!r}. GET /api/models for list."},
            status_code=404,
        )

    params = dict(request.query_params)
    try:
        page = max(1, int(params.pop("page", 1)))
        limit = min(200, max(1, int(params.pop("limit", 50))))
    except ValueError:
        return JSONResponse({"status": "error", "error": "page and limit must be integers"}, status_code=400)

    sort = params.pop("sort", None)

    # Remaining params are treated as equality filters
    filters = {k: v for k, v in params.items() if not k.startswith("_")}

    try:
        rows, total = await fetch_rows(
            model_cls=info["model_cls"],
            scalar_fields=info["scalar_fields"],
            page=page,
            limit=limit,
            sort=sort,
            filters=filters,
        )
    except Exception as exc:
        return JSONResponse({"status": "error", "error": str(exc)}, status_code=500)

    return JSONResponse({
        "model": model_name,
        "table": info["table"],
        "schema": info["fields"],
        "total": total,
        "page": page,
        "limit": limit,
        "rows": rows,
    })


async def api_prompts(request: Request) -> JSONResponse:
    """Prompt plugins and session context."""
    try:
        templates_dir = Path(__file__).resolve().parent.parent.parent.parent / "plugins"
        if not templates_dir.exists():
            templates_dir = Path.cwd() / "plugins"

        template_data: dict[str, list[str]] = {}
        if templates_dir.exists():
            for subdir in sorted(templates_dir.iterdir()):
                if subdir.is_dir():
                    files = [f.name for f in sorted(subdir.iterdir()) if f.is_file()]
                    template_data[subdir.name] = files
                elif subdir.is_file():
                    template_data.setdefault("root", []).append(subdir.name)

        # Session context
        data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
        sessions_dir = data_dir / "sessions" if data_dir.exists() else None
        session_count = 0
        if sessions_dir and sessions_dir.exists():
            session_count = sum(1 for d in sessions_dir.iterdir() if d.is_dir())

    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "plugins": template_data,
        "total_templates": sum(len(v) for v in template_data.values()),
        "sessions": session_count,
    })


async def api_telemetry(request: Request) -> JSONResponse:
    """Live telemetry snapshot from MetricsStore + collector history."""
    try:
        from telemetry import get_snapshot
        from telemetry.collector import collector
        snap = await get_snapshot()
        history = collector.all_history()
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({"snapshot": snap, "history_len": len(history)})
