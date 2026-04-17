"""
Dashboard — Starlette routes serving a self-contained HTML dashboard.

Inspired by OmniRoute's Next.js dashboard but rendered server-side
with Jinja2 + HTMX for zero JS-build-step simplicity.

Integrates: db (ORM health/counts), crypto (artifact stats), a2a (task stats).
Mount at /dashboard in the ASGI app.
"""
from __future__ import annotations

import time
from pathlib import Path

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, StreamingResponse
from starlette.routing import Route, Router

from ai_proxy.providers.registry import (
    get_all_providers,
    get_enabled_providers,
    get_free_providers,
    get_browser_providers,
    list_all_models,
    AuthType,
)
from ai_proxy.routing.combo import (
    Strategy,
    RoutingTier,
    budget_guard,
    get_circuit_breaker_status,
    get_usage_counts,
)
from ai_proxy.services.rate_limiter import rate_limiter
from ai_proxy.services.usage_tracker import usage_tracker


# ── Dashboard API (JSON) ─────────────────────────────────────────────────────

async def api_overview(request: Request) -> JSONResponse:
    """Dashboard overview data."""
    all_p = get_all_providers()
    enabled = get_enabled_providers()
    free = get_free_providers()
    browser = get_browser_providers()
    models = list_all_models()
    summary = usage_tracker.get_summary()

    # Classify providers by tier
    tier_counts: dict[str, int] = {"free": 0, "budget": 0, "standard": 0, "premium": 0}
    for p in all_p.values():
        if p.is_free or p.auth_type in (AuthType.NONE, AuthType.BROWSER):
            tier_counts["free"] += 1
        elif p.models:
            avg = sum((m.cost.input + m.cost.output) / 2 for m in p.models) / len(p.models)
            if avg < 1.0:
                tier_counts["budget"] += 1
            elif avg <= 5.0:
                tier_counts["standard"] += 1
            else:
                tier_counts["premium"] += 1

    # Circuit breaker status
    cb_status = get_circuit_breaker_status()
    open_circuits = sum(1 for cb in cb_status if cb["state"] == "open")

    return JSONResponse({
        "providers": {"total": len(all_p), "enabled": len(enabled), "free": len(free), "browser": len(browser)},
        "models": {"total": len(models)},
        "tiers": tier_counts,
        "usage": summary,
        "budget": budget_guard.get_all(),
        "circuits": {"total": len(cb_status), "open": open_circuits},
        "strategies": [s.value for s in Strategy],
        "uptime_seconds": time.monotonic(),
    })


async def api_providers(request: Request) -> JSONResponse:
    """All providers with status, models, rate limits."""
    result = []
    for p in get_all_providers().values():
        status = "available" if p.is_available else "no_credentials"
        if not p.enabled:
            status = "disabled"

        rl = rate_limiter.get_status(p.id) if p.is_available else {}

        result.append({
            "id": p.id,
            "name": p.name,
            "status": status,
            "auth_type": p.auth_type.value,
            "api_format": p.api_format.value,
            "is_free": p.is_free,
            "base_url": p.base_url,
            "models": [
                {"id": m.id, "name": m.name, "context": m.context_window,
                 "cost_in": m.cost.input, "cost_out": m.cost.output,
                 "tools": m.supports_tools, "vision": m.supports_vision}
                for m in p.models if not m.deprecated
            ],
            "rate_limit": rl,
            "usage": get_usage_counts().get(p.id, 0),
        })
    return JSONResponse(result)


async def api_usage(request: Request) -> JSONResponse:
    """Usage history and cost analytics."""
    return JSONResponse({
        "summary": usage_tracker.get_summary(),
        "recent": usage_tracker.get_recent(limit=50),
        "rate_limits": rate_limiter.get_all_status(),
        "budget": budget_guard.get_all(),
    })


async def api_health(request: Request) -> JSONResponse:
    """Combined health: DB + proxy + providers."""
    try:
        from db.bootstrap import get_database_health_async
        db_health = await get_database_health_async(check_connection=True, include_counts=False)
    except Exception as e:
        db_health = {"status": "error", "error": str(e)}

    enabled = get_enabled_providers()
    return JSONResponse({
        "database": db_health,
        "proxy": {
            "providers_enabled": len(enabled),
            "providers_free": len(get_free_providers()),
            "uptime_seconds": round(time.monotonic(), 1),
        },
    })


async def api_crypto(request: Request) -> JSONResponse:
    """Crypto/artifact signing stats via Tortoise ORM."""
    try:
        from db.models.artifact import Artifact, ArtifactSignatureLog
        total_artifacts = await Artifact.all().count()
        valid_artifacts = await Artifact.filter(signature_valid=True).count()
        invalid_artifacts = await Artifact.filter(signature_valid=False).count()
        recent_sigs = await ArtifactSignatureLog.all().order_by(
            "-created_at"
        ).limit(10).prefetch_related("artifact")
        recent_logs = [
            {
                "artifact_id": log.artifact.id if log.artifact else None,
                "action": log.action,
                "status": log.verification_status,
                "key_id": log.key_id,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in recent_sigs
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total_artifacts": total_artifacts,
        "valid": valid_artifacts,
        "invalid": invalid_artifacts,
        "recent_signature_logs": recent_logs,
    })


async def api_a2a(request: Request) -> JSONResponse:
    """A2A task stats via Tortoise ORM."""
    try:
        from db.models.a2a_task import A2ATask
        total = await A2ATask.all().count()
        by_state: dict[str, int] = {}
        for state in ("submitted", "working", "completed", "failed", "canceled"):
            by_state[state] = await A2ATask.filter(state=state).count()
        recent = await A2ATask.all().order_by("-updated_at").limit(10)
        recent_tasks = [
            {
                "id": t.id,
                "session_id": t.session_id,
                "state": t.state,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total_tasks": total,
        "by_state": by_state,
        "recent_tasks": recent_tasks,
    })


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


async def api_agents(request: Request) -> JSONResponse:
    """Agent registry: all registered A2A agents with skills and metadata."""
    try:
        from a2a.registry import AgentRegistry
        from a2a.agent_loader import load_cybersecsuite_agents

        registry = AgentRegistry()
        load_cybersecsuite_agents(registry)
        agents = registry.summary()

        # Also load from AI/agents if available
        ai_agents_dir = Path(__file__).resolve().parent.parent.parent.parent / "AI" / "agents"
        if not ai_agents_dir.exists():
            ai_agents_dir = Path.home() / "Projects" / "AI" / "agents"
        if ai_agents_dir.exists():
            from a2a.agent_loader import load_agents_from_dir
            load_agents_from_dir(ai_agents_dir, registry, recurse=True)
            agents = registry.summary()

        orchestrators = [a for a in agents if a.get("claude_metadata", {}).get("role") == "orchestrator"]
        specialists = [a for a in agents if a.get("claude_metadata", {}).get("role") != "orchestrator"]

    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total": len(agents),
        "orchestrators": len(orchestrators),
        "specialists": len(specialists),
        "agents": agents,
    })


async def api_routing(request: Request) -> JSONResponse:
    """Routing engine status: strategies, circuit breakers, combos."""
    try:
        strategies = [s.value for s in Strategy]
        tiers = [t.value for t in RoutingTier]

        # Circuit breaker status
        cb_status = get_circuit_breaker_status()

        # Usage counts per provider
        usage = get_usage_counts()

        # Budget guard state
        budgets = budget_guard.get_all()

    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "strategies": strategies,
        "tiers": tiers,
        "circuit_breakers": cb_status,
        "open_circuits": sum(1 for cb in cb_status if cb["state"] == "open"),
        "usage_counts": usage,
        "budgets": budgets,
    })


async def api_agent_factory(request: Request) -> JSONResponse:
    """Agent factory metadata: available templates, capabilities."""
    try:
        factory_path = Path(__file__).resolve().parent.parent.parent / ".claude" / "agents" / "AGENT_FACTORY.md"
        if not factory_path.exists():
            # Try project root
            for candidate in (Path.cwd(), Path(__file__).resolve().parent.parent.parent.parent):
                p = candidate / ".claude" / "agents" / "AGENT_FACTORY.md"
                if p.exists():
                    factory_path = p
                    break

        factory_exists = factory_path.exists()
        factory_size = factory_path.stat().st_size if factory_exists else 0

        # Count agent files
        agents_dir = factory_path.parent if factory_exists else None
        agent_files = []
        if agents_dir and agents_dir.exists():
            for md in sorted(agents_dir.glob("*.md")):
                if md.name.startswith(("AGENT_", "CLAUDE_", "COPILOT_")):
                    continue
                agent_files.append({
                    "name": md.stem,
                    "size": md.stat().st_size,
                    "lines": sum(1 for _ in md.open()),
                })

        # Teams
        teams_dir = agents_dir / "teams" if agents_dir else None
        team_files = []
        if teams_dir and teams_dir.exists():
            for md in sorted(teams_dir.glob("*.md")):
                team_files.append({"name": md.stem, "size": md.stat().st_size})

    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "factory_available": factory_exists,
        "factory_size_bytes": factory_size,
        "templates": ["orchestrator", "specialist"],
        "archetypes": ["orchestrator", "specialist", "team-mode"],
        "tools": ["Read", "Write", "Glob", "WebFetch"],
        "agents": agent_files,
        "teams": team_files,
        "total_agents": len(agent_files),
        "total_teams": len(team_files),
    })


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



# ── SSE Streaming Endpoints ──────────────────────────────────────────────────────

async def sse_cases(request: Request) -> StreamingResponse:
    """Server-Sent Events stream for case intake updates."""
    async def event_generator():
        try:
            import json
            import asyncio
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
                await asyncio.sleep(5)  # Update every 5 seconds
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
            import json
            import asyncio
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
                await asyncio.sleep(5)  # Update every 5 seconds
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
            import json
            import asyncio
            while True:
                from db.bootstrap import get_database_health_async
                db_health = await get_database_health_async(check_connection=True, include_counts=False)
                enabled = get_enabled_providers()

                data = {
                    "database": db_health,
                    "proxy": {
                        "providers_enabled": len(enabled),
                        "providers_free": len(get_free_providers()),
                        "uptime_seconds": round(time.monotonic(), 1),
                    },
                }
                yield f"data: {json.dumps(data, default=str)}\n\n"
                await asyncio.sleep(10)  # Update every 10 seconds
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


async def api_prompts(request: Request) -> JSONResponse:
    """Prompt templates and session context."""
    try:
        templates_dir = Path(__file__).resolve().parent.parent.parent.parent / "templates"
        if not templates_dir.exists():
            templates_dir = Path.cwd() / "templates"

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
        "templates": template_data,
        "total_templates": sum(len(v) for v in template_data.values()),
        "sessions": session_count,
    })


async def api_findings(request: Request) -> JSONResponse:
    """Security findings summary — totals by severity/status + recent 20."""
    try:
        from db.models.investigation import Finding
        total = await Finding.all().count()
        by_severity: dict[str, int] = {}
        for sev in ("critical", "high", "medium", "low", "info"):
            by_severity[sev] = await Finding.filter(severity=sev).count()
        by_status: dict[str, int] = {}
        for st in ("open", "investigating", "confirmed", "resolved", "false_positive"):
            by_status[st] = await Finding.filter(status=st).count()

        last_24h = await Finding.filter(
            created_at__gte=__import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            - __import__("datetime").timedelta(hours=24)
        ).count()
        last_7d = await Finding.filter(
            created_at__gte=__import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            - __import__("datetime").timedelta(days=7)
        ).count()

        recent = await Finding.all().order_by("-created_at").limit(20)
        recent_list = [
            {
                "id": f.id,
                "title": f.title,
                "severity": f.severity if isinstance(f.severity, str) else f.severity.value,
                "status": f.status if isinstance(f.status, str) else f.status.value,
                "created_at": f.created_at.isoformat() if hasattr(f, "created_at") and f.created_at else None,
            }
            for f in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "trend": {"last_24h": last_24h, "last_7d": last_7d},
        "recent": recent_list,
    })


async def api_iocs(request: Request) -> JSONResponse:
    """IOC summary — totals by type/status/confidence + recent 20."""
    try:
        from db.models.investigation import IOC
        total = await IOC.all().count()

        # Aggregate by ioc_type (free-form field)
        all_iocs = await IOC.all().values_list("ioc_type", flat=True)
        by_type: dict[str, int] = {}
        for t in all_iocs:
            by_type[t or "unknown"] = by_type.get(t or "unknown", 0) + 1

        by_status: dict[str, int] = {}
        for st in ("active", "cleared", "watchlist", "expired"):
            by_status[st] = await IOC.filter(status=st).count()
        by_confidence: dict[str, int] = {}
        for cf in ("low", "medium", "high", "confirmed"):
            by_confidence[cf] = await IOC.filter(confidence=cf).count()

        recent = await IOC.all().order_by("-updated_at").limit(20)
        recent_list = [
            {
                "ioc_id": ioc.ioc_id,
                "type": ioc.ioc_type,
                "value": ioc.value,
                "status": ioc.status if isinstance(ioc.status, str) else ioc.status.value,
            }
            for ioc in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])[:10]),
        "by_status": by_status,
        "by_confidence": by_confidence,
        "recent": recent_list,
    })


async def api_yara(request: Request) -> JSONResponse:
    """YARA rule summary — totals by status/severity/source + recent 10."""
    try:
        from db.models.yara_rule import YaraRule
        total = await YaraRule.all().count()
        by_status: dict[str, int] = {}
        for st in ("draft", "tested", "optimized", "active", "deprecated"):
            by_status[st] = await YaraRule.filter(status=st).count()
        by_source: dict[str, int] = {}
        for src in ("ioc_derived", "manual", "imported", "generated"):
            by_source[src] = await YaraRule.filter(source=src).count()

        recent = await YaraRule.all().order_by("-created_at").limit(10)
        recent_list = [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "status": r.status if isinstance(r.status, str) else r.status.value,
                "source": r.source if isinstance(r.source, str) else r.source.value,
                "created_at": r.created_at.isoformat() if hasattr(r, "created_at") and r.created_at else None,
            }
            for r in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_status": by_status,
        "by_source": by_source,
        "recent": recent_list,
    })


async def api_network(request: Request) -> JSONResponse:
    """Network assets summary — hosts and IP addresses."""
    try:
        from db.models.network import IPAddress, Host
        total_hosts = await Host.all().count()
        compromised = await Host.filter(is_compromised=True).count()
        targets = await Host.filter(is_target=True).count()
        total_ips = await IPAddress.all().count()
        private_ips = await IPAddress.filter(is_private=True).count()

        # Top countries by IP
        all_countries = await IPAddress.all().values_list("geo_country", flat=True)
        country_counts: dict[str, int] = {}
        for c in all_countries:
            if c:
                country_counts[c] = country_counts.get(c, 0) + 1
        top_countries = [
            {"code": code, "count": cnt}
            for code, cnt in sorted(country_counts.items(), key=lambda x: -x[1])[:10]
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "hosts": {"total": total_hosts, "compromised": compromised, "targets": targets},
        "ip_addresses": {"total": total_ips, "private": private_ips, "public": total_ips - private_ips},
        "top_countries": top_countries,
    })


async def api_intelligence(request: Request) -> JSONResponse:
    """Threat intelligence database counts — MITRE, CVE, CWE, CAPEC."""
    try:
        from db.models.mitre_technique import MitreTechniqueIntel
        from db.models.cve_entry import CVEIntelligenceEntry
        from db.models.cwe import CWEIntel
        from db.models.capec import CapecAttackPatternIntel

        mitre_count = await MitreTechniqueIntel.all().count()
        cve_count = await CVEIntelligenceEntry.all().count()
        cwe_count = await CWEIntel.all().count()
        capec_count = await CapecAttackPatternIntel.all().count()

        # Unique tactics from MITRE
        tactics = await MitreTechniqueIntel.all().values_list("tactic", flat=True)
        unique_tactics = len({t for t in tactics if t})

        # Last seeded — check feed snapshot or update log
        last_seeded = None
        try:
            from db.models.feed_snapshot import FeedSnapshot
            snap = await FeedSnapshot.all().order_by("-created_at").first()
            last_seeded = snap.created_at.isoformat() if snap and snap.created_at else None
        except Exception:
            pass
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "mitre": {"techniques": mitre_count, "tactics": unique_tactics},
        "cve": {"total": cve_count},
        "cwe": {"total": cwe_count},
        "capec": {"total": capec_count},
        "last_seeded": last_seeded,
    })


async def api_audit(request: Request) -> JSONResponse:
    """Audit log summary — recent entries and action counts."""
    try:
        from db.models.audit import AuditLog
        import datetime as _dt

        total = await AuditLog.all().count()
        recent = await AuditLog.all().order_by("-created_at").limit(50)

        recent_list = [
            {
                "action": e.action if isinstance(e.action, str) else e.action.value,
                "entity_type": e.entity_type,
                "agent": e.agent,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in recent
        ]

        # Count by action
        by_action: dict[str, int] = {}
        for e in recent_list:
            a = e["action"]
            by_action[a] = by_action.get(a, 0) + 1

        # Count by agent
        by_agent: dict[str, int] = {}
        for e in recent_list:
            ag = e["agent"] or "unknown"
            by_agent[ag] = by_agent.get(ag, 0) + 1

        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=1)
        last_hour_count = await AuditLog.filter(created_at__gte=cutoff).count()
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "last_hour_count": last_hour_count,
        "by_action": by_action,
        "by_agent": by_agent,
        "recent": recent_list,
    })


async def api_compliance(request: Request) -> JSONResponse:
    """Compliance rules summary — totals by framework and severity."""
    try:
        from db.models.compliance import ComplianceRule
        total = await ComplianceRule.all().count()

        all_rules = await ComplianceRule.all().values_list("framework", "severity")
        by_framework: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for framework, severity in all_rules:
            f = framework or "unknown"
            by_framework[f] = by_framework.get(f, 0) + 1
            s = severity if isinstance(severity, str) else (severity.value if severity else "unknown")
            by_severity[s] = by_severity.get(s, 0) + 1
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_framework": dict(sorted(by_framework.items(), key=lambda x: -x[1])),
        "by_severity": by_severity,
    })


async def api_nist_csf(request: Request) -> JSONResponse:
    """NIST CSF 2.0 controls — totals by function and category."""
    try:
        from db.models.nist_csf import NistCsfControl
        total = await NistCsfControl.all().count()
        if total == 0:
            return JSONResponse({"total": 0, "note": "Run: python3 manage.py seed-nist-csf"})
        rows = await NistCsfControl.all().values_list("function", "function_code", "category")
        by_function: dict[str, int] = {}
        by_category: dict[str, int] = {}
        for fn, _fc, cat in rows:
            by_function[fn] = by_function.get(fn, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
    })


async def api_nist_ai_rmf(request: Request) -> JSONResponse:
    """NIST AI RMF 1.0 controls — totals by function and topic."""
    try:
        from db.models.nist_ai_rmf import NistAiRmfControl
        total = await NistAiRmfControl.all().count()
        if total == 0:
            return JSONResponse({"total": 0, "note": "Run: python3 manage.py seed-nist-ai-rmf"})
        rows = await NistAiRmfControl.all().values_list("function", "topic")
        by_function: dict[str, int] = {}
        by_topic: dict[str, int] = {}
        for fn, topic in rows:
            by_function[fn] = by_function.get(fn, 0) + 1
            t = topic or "general"
            by_topic[t] = by_topic.get(t, 0) + 1
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_topic": dict(sorted(by_topic.items(), key=lambda x: -x[1])),
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


async def sse_telemetry(request: Request) -> StreamingResponse:
    """SSE stream of telemetry snapshots every 5 s."""
    async def event_generator():
        try:
            import json
            import asyncio
            from telemetry import get_snapshot
            while True:
                snap = await get_snapshot()
                yield f"event: telemetry_update\ndata: {json.dumps(snap, default=str)}\n\n"
                await asyncio.sleep(5)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def api_task_create(request: Request) -> JSONResponse:
    """Submit a new A2A task — body: {agent, message, session_id?, metadata?}."""
    try:
        import uuid
        body = await request.json()
        agent: str = body.get("agent", "orchestrator")
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


# ── Dashboard HTML (self-contained) ──────────────────────────────────────────

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CyberSecSuite Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwindcss_config={theme:{extend:{colors:{cyber:'#0ff',dark:'#0a0e17'}}}}</script>
<style>
  body { background: #0a0e17; color: #e2e8f0; font-family: 'JetBrains Mono', 'Fira Code', monospace; }
  .card { background: #111827; border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1.25rem; }
  .card:hover { border-color: #0ff3; }
  .glow { text-shadow: 0 0 10px #0ff6; }
  .badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
  .badge-free { background: #064e3b; color: #34d399; }
  .badge-budget { background: #1e3a5f; color: #60a5fa; }
  .badge-standard { background: #3b2f63; color: #a78bfa; }
  .badge-premium { background: #5b2130; color: #fb7185; }
  .badge-ok { background: #064e3b; color: #34d399; }
  .badge-err { background: #5b2130; color: #fb7185; }
  .badge-browser { background: #312e81; color: #818cf8; }
  .progress { height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; }
  .progress-bar { height: 100%; background: linear-gradient(90deg, #0ff, #6366f1); transition: width 0.5s; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 0.5rem; border-bottom: 1px solid #1e293b; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }
  td { padding: 0.5rem; border-bottom: 1px solid #1e293b08; font-size: 0.875rem; }
  tr:hover td { background: #1e293b40; }
  .tab { cursor: pointer; padding: 0.5rem 1rem; border-bottom: 2px solid transparent; color: #94a3b8; }
  .tab.active { border-color: #0ff; color: #0ff; }
  .tab:hover { color: #e2e8f0; }
  @keyframes pulse-glow { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
  .loading { animation: pulse-glow 1.5s infinite; }
</style>
</head>
<body class="min-h-screen">
<div class="max-w-7xl mx-auto px-4 py-6">
  <!-- Header -->
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-2xl font-bold glow" style="color:#0ff">&#x1f6e1; CyberSecSuite</h1>
      <p class="text-sm text-gray-500 mt-1">AI Proxy Dashboard &mdash; Multi-Provider Router</p>
    </div>
    <div class="flex gap-3">
      <button onclick="refresh()" class="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700">&#x21bb; Refresh</button>
      <span id="uptime" class="text-xs text-gray-500 self-center"></span>
    </div>
  </div>

  <!-- Stats row -->
  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6" id="stats">
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-providers">-</div><div class="text-xs text-gray-500">Providers</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-enabled">-</div><div class="text-xs text-gray-500">Enabled</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-models">-</div><div class="text-xs text-gray-500">Models</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-requests">-</div><div class="text-xs text-gray-500">Requests</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-tokens">-</div><div class="text-xs text-gray-500">Tokens</div></div>
    <div class="card text-center loading"><div class="text-2xl font-bold" id="s-cost">-</div><div class="text-xs text-gray-500">Cost (USD)</div></div>
  </div>

  <!-- Tier breakdown -->
  <div class="grid grid-cols-4 gap-4 mb-6" id="tiers">
    <div class="card text-center"><span class="badge badge-free">FREE</span><div class="text-xl font-bold mt-2" id="t-free">-</div></div>
    <div class="card text-center"><span class="badge badge-budget">BUDGET</span><div class="text-xl font-bold mt-2" id="t-budget">-</div></div>
    <div class="card text-center"><span class="badge badge-standard">STANDARD</span><div class="text-xl font-bold mt-2" id="t-standard">-</div></div>
    <div class="card text-center"><span class="badge badge-premium">PREMIUM</span><div class="text-xl font-bold mt-2" id="t-premium">-</div></div>
  </div>

  <!-- Tabs -->
  <div class="flex gap-1 mb-4 border-b border-gray-800 flex-wrap">
    <div class="tab active" onclick="showTab('providers')">Providers</div>
    <div class="tab" onclick="showTab('usage')">Usage & Cost</div>
    <div class="tab" onclick="showTab('agents')">&#x1f916; Agents</div>
    <div class="tab" onclick="showTab('routing')">&#x1f500; Routing</div>
    <div class="tab" onclick="showTab('factory')">&#x1f3ed; Factory</div>
    <div class="tab" onclick="showTab('prompts')">&#x1f4dd; Prompts</div>
    <div class="tab" onclick="showTab('health')">Health</div>
    <div class="tab" onclick="showTab('crypto')">&#x1f512; Crypto</div>
    <div class="tab" onclick="showTab('a2a')">&#x1f310; A2A</div>
    <div class="tab" onclick="showTab('investigations')">&#x1f50d; Investigations</div>
    <div class="tab" onclick="showTab('dbcounts')">&#x1f4ca; DB Counts</div>
    <div class="tab" onclick="showTab('cases')">&#x1f4c2; Cases</div>
    <div class="tab" onclick="showTab('tasks')">&#x23f1; Tasks</div>
  </div>

  <!-- Providers tab -->
  <div id="tab-providers" class="card">
    <table>
      <thead><tr><th>Provider</th><th>Status</th><th>Type</th><th>Format</th><th>Models</th><th>RPM</th><th>Cost Range</th></tr></thead>
      <tbody id="providers-body"><tr><td colspan="7" class="text-center text-gray-500 loading">Loading...</td></tr></tbody>
    </table>
  </div>

  <!-- Usage tab -->
  <div id="tab-usage" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">Recent Requests</h3>
    <table>
      <thead><tr><th>Provider</th><th>Model</th><th>Tokens</th><th>Cost</th><th>Latency</th><th>Status</th></tr></thead>
      <tbody id="usage-body"><tr><td colspan="6" class="text-center text-gray-500">No requests yet</td></tr></tbody>
    </table>
  </div>

  <!-- Health tab -->
  <div id="tab-health" class="card" style="display:none">
    <div id="health-content" class="loading">Checking health...</div>
  </div>

  <!-- Agents tab -->
  <div id="tab-agents" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f916; Agent Registry</h3>
    <div id="agents-content" class="loading">Loading agents...</div>
  </div>

  <!-- Routing tab -->
  <div id="tab-routing" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f500; Routing Engine</h3>
    <div id="routing-content" class="loading">Loading routing...</div>
  </div>

  <!-- Factory tab -->
  <div id="tab-factory" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f3ed; Agent Factory</h3>
    <div id="factory-content" class="loading">Loading factory...</div>
  </div>

  <!-- Prompts tab -->
  <div id="tab-prompts" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f4dd; Prompts & Templates</h3>
    <div id="prompts-content" class="loading">Loading prompts...</div>
  </div>

  <!-- Crypto tab -->
  <div id="tab-crypto" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f512; Artifact Signing</h3>
    <div id="crypto-content" class="loading">Loading crypto stats...</div>
  </div>

  <!-- A2A tab -->
  <div id="tab-a2a" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f916; A2A Agent Tasks</h3>
    <div id="a2a-content" class="loading">Loading A2A stats...</div>
  </div>

  <!-- Investigations tab -->
  <div id="tab-investigations" class="card" style="display:none">
    <h3 class="text-lg font-semibold mb-3">&#x1f50d; Investigations</h3>
    <div id="inv-content" class="loading">Loading investigation stats...</div>
  </div>

   <!-- DB Counts tab -->
   <div id="tab-dbcounts" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f4ca; Database Table Counts</h3>
     <div id="db-content" class="loading">Loading DB counts...</div>
   </div>

   <!-- Cases tab -->
   <div id="tab-cases" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x1f4c2; Phase 0 Case Intake</h3>
     <div class="grid grid-cols-3 gap-4 mb-4">
       <div class="card text-center"><div class="text-2xl font-bold" id="cases-total">-</div><div class="text-xs text-gray-500">Total Cases</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-green-400" id="cases-open">-</div><div class="text-xs text-gray-500">Open</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-gray-400" id="cases-closed">-</div><div class="text-xs text-gray-500">Closed</div></div>
     </div>
     <table>
       <thead><tr><th>Title</th><th>Priority</th><th>Mode</th><th>Facts</th><th>IOCs</th><th>Assets</th><th>MITRE</th><th>Created</th><th>Status</th></tr></thead>
       <tbody id="cases-body"><tr><td colspan="9" class="text-center text-gray-500 loading">Loading cases...</td></tr></tbody>
     </table>
   </div>

   <!-- Tasks tab -->
   <div id="tab-tasks" class="card" style="display:none">
     <h3 class="text-lg font-semibold mb-3">&#x23f1; Task Management</h3>
     <div class="grid grid-cols-5 gap-4 mb-4">
       <div class="card text-center"><div class="text-2xl font-bold" id="tasks-total">-</div><div class="text-xs text-gray-500">Total</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-blue-400" id="tasks-submitted">-</div><div class="text-xs text-gray-500">Submitted</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-yellow-400" id="tasks-working">-</div><div class="text-xs text-gray-500">Working</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-green-400" id="tasks-completed">-</div><div class="text-xs text-gray-500">Done</div></div>
       <div class="card text-center"><div class="text-2xl font-bold text-red-400" id="tasks-failed">-</div><div class="text-xs text-gray-500">Failed</div></div>
     </div>
     <table>
       <thead><tr><th>Task ID</th><th>State</th><th>Agent</th><th>Created</th><th>Updated</th><th>Action</th></tr></thead>
       <tbody id="tasks-body"><tr><td colspan="6" class="text-center text-gray-500 loading">Loading tasks...</td></tr></tbody>
     </table>
   </div>
</div>

<script>
const $ = id => document.getElementById(id);
let currentTab = 'providers';

function showTab(name) {
  document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  $('tab-' + name).style.display = '';
  event.target.classList.add('active');
  currentTab = name;
}

function fmt(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return String(n);
}

function tierBadge(p) {
  if (p.is_free || p.auth_type === 'none' || p.auth_type === 'browser') return '<span class="badge badge-free">FREE</span>';
  if (!p.models.length) return '<span class="badge badge-standard">STD</span>';
  const avg = p.models.reduce((s,m) => s + (m.cost_in + m.cost_out)/2, 0) / p.models.length;
  if (avg < 1) return '<span class="badge badge-budget">BUDGET</span>';
  if (avg <= 5) return '<span class="badge badge-standard">STD</span>';
  return '<span class="badge badge-premium">PREMIUM</span>';
}

function costRange(models) {
  if (!models.length) return '$0';
  const costs = models.map(m => m.cost_in);
  const min = Math.min(...costs), max = Math.max(...costs);
  if (min === max) return '$' + min.toFixed(2);
  return '$' + min.toFixed(2) + '-' + max.toFixed(2);
}

async function refresh() {
  try {
    const [ov, pv, uv, hv, cv, av, iv, dv, agv, rtv, fv, pmv, casesv, tasksv] = await Promise.all([
      fetch('/dashboard/api/overview').then(r => r.json()),
      fetch('/dashboard/api/providers').then(r => r.json()),
      fetch('/dashboard/api/usage').then(r => r.json()),
      fetch('/dashboard/api/health').then(r => r.json()),
      fetch('/dashboard/api/crypto').then(r => r.json()),
      fetch('/dashboard/api/a2a').then(r => r.json()),
      fetch('/dashboard/api/investigations').then(r => r.json()),
      fetch('/dashboard/api/db-counts').then(r => r.json()),
      fetch('/dashboard/api/agents').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/routing').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/agent-factory').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/prompts').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/cases').then(r => r.json()).catch(() => ({error:'unavailable'})),
      fetch('/dashboard/api/tasks').then(r => r.json()).catch(() => ({error:'unavailable'})),
    ]);

    // Stats
    $('s-providers').textContent = ov.providers.total;
    $('s-enabled').textContent = ov.providers.enabled;
    $('s-models').textContent = ov.models.total;
    $('s-requests').textContent = fmt(ov.usage.total_requests);
    $('s-tokens').textContent = fmt(ov.usage.total_tokens);
    $('s-cost').textContent = '$' + ov.usage.total_cost_usd.toFixed(4);
    $('uptime').textContent = Math.round(ov.uptime_seconds) + 's uptime';

    // Tiers
    $('t-free').textContent = ov.tiers.free;
    $('t-budget').textContent = ov.tiers.budget;
    $('t-standard').textContent = ov.tiers.standard;
    $('t-premium').textContent = ov.tiers.premium;

    // Remove loading
    document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));

    // Providers table
    const pbody = $('providers-body');
    pbody.innerHTML = pv.map(p => {
      const statusBadge = p.status === 'available'
        ? '<span class="badge badge-ok">ON</span>'
        : '<span class="badge badge-err">' + p.status.toUpperCase() + '</span>';
      const typeBadge = p.auth_type === 'browser'
        ? '<span class="badge badge-browser">BROWSER</span>'
        : tierBadge(p);
      const rpm = p.rate_limit.rpm_remaining !== undefined
        ? Math.round(p.rate_limit.rpm_remaining) + '/' + p.rate_limit.rpm_capacity
        : '-';
      return '<tr><td><strong>' + p.name + '</strong><br><span class="text-xs text-gray-500">' + p.id + '</span></td>'
        + '<td>' + statusBadge + '</td>'
        + '<td>' + typeBadge + '</td>'
        + '<td class="text-xs">' + p.api_format + '</td>'
        + '<td>' + p.models.length + '</td>'
        + '<td class="text-xs">' + rpm + '</td>'
        + '<td class="text-xs">' + costRange(p.models) + '/M</td></tr>';
    }).join('');

    // Usage table
    const ubody = $('usage-body');
    if (uv.recent.length) {
      ubody.innerHTML = uv.recent.map(r => {
        const badge = r.success ? '<span class="badge badge-ok">OK</span>' : '<span class="badge badge-err">FAIL</span>';
        return '<tr><td>' + r.provider + '</td><td class="text-xs">' + r.model + '</td>'
          + '<td>' + fmt(r.tokens) + '</td><td>$' + r.cost_usd.toFixed(6) + '</td>'
          + '<td>' + r.latency_ms.toFixed(0) + 'ms</td><td>' + badge + '</td></tr>';
      }).join('');
    }

    // Health
    const hc = $('health-content');
    const dbStatus = hv.database.status === 'ok' ? '&#x2705;' : '&#x274c;';
    hc.innerHTML = '<div class="grid grid-cols-2 gap-4">'
      + '<div><h4 class="font-semibold mb-2">Database</h4>'
      + '<p>' + dbStatus + ' ' + (hv.database.status || 'unknown') + '</p>'
      + '<p class="text-xs text-gray-500">Tables: ' + (hv.database.table_count || '?') + '</p></div>'
      + '<div><h4 class="font-semibold mb-2">Proxy</h4>'
      + '<p>&#x2705; ' + hv.proxy.providers_enabled + ' providers enabled</p>'
      + '<p class="text-xs text-gray-500">' + hv.proxy.providers_free + ' free providers</p></div>'
      + '</div>';
    hc.classList.remove('loading');

    // Crypto tab
    const cc = $('crypto-content');
    if (cv.error) {
      cc.innerHTML = '<p class="text-red-400">Error: ' + cv.error + '</p>';
    } else {
      cc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + cv.total_artifacts + '</div><div class="text-xs text-gray-500">Total Artifacts</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-green-400">' + cv.valid + '</div><div class="text-xs text-gray-500">Valid Sigs</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' + cv.invalid + '</div><div class="text-xs text-gray-500">Invalid Sigs</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Recent Signature Logs</h4>'
        + '<table><thead><tr><th>Artifact</th><th>Action</th><th>Status</th><th>Key</th><th>Time</th></tr></thead><tbody>'
        + (cv.recent_signature_logs || []).map(l =>
          '<tr><td>' + l.artifact_id + '</td><td>' + l.action + '</td>'
          + '<td><span class="badge ' + (l.status === 'valid' ? 'badge-ok' : 'badge-err') + '">' + l.status + '</span></td>'
          + '<td class="text-xs">' + l.key_id + '</td>'
          + '<td class="text-xs">' + (l.created_at || '-') + '</td></tr>'
        ).join('') + '</tbody></table>';
    }

    // A2A tab
    const ac = $('a2a-content');
    if (av.error) {
      ac.innerHTML = '<p class="text-red-400">Error: ' + av.error + '</p>';
    } else {
      ac.innerHTML = '<div class="grid grid-cols-3 md:grid-cols-6 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + av.total_tasks + '</div><div class="text-xs text-gray-500">Total</div></div>'
        + Object.entries(av.by_state || {}).map(([k,v]) =>
          '<div class="card text-center"><div class="text-xl font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k + '</div></div>'
        ).join('')
        + '</div>'
        + '<h4 class="font-semibold mb-2">Recent Tasks</h4>'
        + '<table><thead><tr><th>ID</th><th>Session</th><th>State</th><th>Updated</th></tr></thead><tbody>'
        + (av.recent_tasks || []).map(t =>
          '<tr><td class="text-xs">' + t.id + '</td><td class="text-xs">' + (t.session_id || '-') + '</td>'
          + '<td><span class="badge ' + (t.state === 'completed' ? 'badge-ok' : t.state === 'failed' ? 'badge-err' : 'badge-budget') + '">' + t.state + '</span></td>'
          + '<td class="text-xs">' + (t.updated_at || '-') + '</td></tr>'
        ).join('') + '</tbody></table>';
    }

    // Investigations tab
    const ic = $('inv-content');
    if (iv.error) {
      ic.innerHTML = '<p class="text-red-400">Error: ' + iv.error + '</p>';
    } else {
      ic.innerHTML = '<div class="grid grid-cols-4 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.findings + '</div><div class="text-xs text-gray-500">Findings</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.iocs + '</div><div class="text-xs text-gray-500">IOCs</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.risks + '</div><div class="text-xs text-gray-500">Risks</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + iv.mitre_techniques + '</div><div class="text-xs text-gray-500">MITRE</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Findings by Severity</h4>'
        + '<div class="grid grid-cols-5 gap-2">'
        + Object.entries(iv.findings_by_severity || {}).map(([k,v]) =>
          '<div class="card text-center"><div class="font-bold">' + v + '</div><div class="text-xs text-gray-500">' + k.toUpperCase() + '</div></div>'
        ).join('')
        + '</div>';
    }

    // DB Counts tab
    const dc = $('db-content');
    if (dv.error) {
      dc.innerHTML = '<p class="text-red-400">Error: ' + dv.error + '</p>';
    } else {
      dc.innerHTML = '<table><thead><tr><th>Table</th><th>Rows</th></tr></thead><tbody>'
        + Object.entries(dv.counts || {}).sort((a,b) => b[1] - a[1]).map(([t,c]) =>
          '<tr><td>' + t + '</td><td class="font-bold">' + fmt(c) + '</td></tr>'
        ).join('') + '</tbody></table>';
    }

    // Agents tab
    const agc = $('agents-content');
    if (agv.error) {
      agc.innerHTML = '<p class="text-red-400">Error: ' + agv.error + '</p>';
    } else {
      agc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + agv.total + '</div><div class="text-xs text-gray-500">Total Agents</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-purple-400">' + agv.orchestrators + '</div><div class="text-xs text-gray-500">Orchestrators</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-blue-400">' + agv.specialists + '</div><div class="text-xs text-gray-500">Specialists</div></div>'
        + '</div>'
        + '<table><thead><tr><th>Agent</th><th>Role</th><th>Model</th><th>Skills</th><th>URL</th></tr></thead><tbody>'
        + (agv.agents || []).map(a => {
          const role = (a.claude_metadata||{}).role || 'specialist';
          const model = (a.claude_metadata||{}).model || '-';
          const roleBadge = role === 'orchestrator'
            ? '<span class="badge badge-premium">ORCH</span>'
            : '<span class="badge badge-budget">SPEC</span>';
          const skills = (a.skills||[]).map(s => s.name).join(', ');
          return '<tr><td><strong>' + a.name + '</strong><br><span class="text-xs text-gray-500">' + (a.description||'').substring(0,80) + '</span></td>'
            + '<td>' + roleBadge + '</td>'
            + '<td class="text-xs">' + model + '</td>'
            + '<td class="text-xs">' + skills + '</td>'
            + '<td class="text-xs">' + (a.url||'-') + '</td></tr>';
        }).join('') + '</tbody></table>';
    }

    // Routing tab
    const rtc = $('routing-content');
    if (rtv.error) {
      rtc.innerHTML = '<p class="text-red-400">Error: ' + rtv.error + '</p>';
    } else {
      rtc.innerHTML = '<div class="grid grid-cols-3 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (rtv.strategies||[]).length + '</div><div class="text-xs text-gray-500">Strategies</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (rtv.circuit_breakers||[]).length + '</div><div class="text-xs text-gray-500">Circuit Breakers</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold text-red-400">' + (rtv.open_circuits||0) + '</div><div class="text-xs text-gray-500">Open Circuits</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Strategies</h4>'
        + '<div class="flex flex-wrap gap-2 mb-4">' + (rtv.strategies||[]).map(s =>
          '<span class="badge badge-standard">' + s + '</span>'
        ).join('') + '</div>'
        + '<h4 class="font-semibold mb-2">Circuit Breakers</h4>'
        + '<table><thead><tr><th>Target</th><th>State</th><th>Failures</th></tr></thead><tbody>'
        + (rtv.circuit_breakers||[]).map(cb =>
          '<tr><td class="text-xs">' + cb.target + '</td>'
          + '<td><span class="badge ' + (cb.state === 'closed' ? 'badge-ok' : 'badge-err') + '">' + cb.state.toUpperCase() + '</span></td>'
          + '<td>' + cb.failures + '</td></tr>'
        ).join('') + '</tbody></table>'
        + '<h4 class="font-semibold mt-4 mb-2">Budget Guards</h4>'
        + '<pre class="text-xs bg-gray-900 p-3 rounded overflow-auto">' + JSON.stringify(rtv.budgets||{}, null, 2) + '</pre>';
    }

    // Factory tab
    const fc = $('factory-content');
    if (fv.error) {
      fc.innerHTML = '<p class="text-red-400">Error: ' + fv.error + '</p>';
    } else {
      fc.innerHTML = '<div class="grid grid-cols-4 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold ' + (fv.factory_available ? 'text-green-400' : 'text-red-400') + '">' + (fv.factory_available ? '&#x2705;' : '&#x274c;') + '</div><div class="text-xs text-gray-500">Factory</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + fv.total_agents + '</div><div class="text-xs text-gray-500">Agent Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + fv.total_teams + '</div><div class="text-xs text-gray-500">Team Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + (fv.templates||[]).length + '</div><div class="text-xs text-gray-500">Templates</div></div>'
        + '</div>'
        + '<h4 class="font-semibold mb-2">Archetypes</h4>'
        + '<div class="flex gap-2 mb-4">' + (fv.archetypes||[]).map(a =>
          '<span class="badge badge-standard">' + a + '</span>'
        ).join('') + '</div>'
        + '<h4 class="font-semibold mb-2">Agent Files</h4>'
        + '<table><thead><tr><th>Name</th><th>Size</th><th>Lines</th></tr></thead><tbody>'
        + (fv.agents||[]).map(a =>
          '<tr><td>' + a.name + '</td><td class="text-xs">' + (a.size/1024).toFixed(1) + ' KB</td><td class="text-xs">' + a.lines + '</td></tr>'
        ).join('') + '</tbody></table>'
        + '<h4 class="font-semibold mt-4 mb-2">Teams</h4>'
        + '<div class="flex flex-wrap gap-2">' + (fv.teams||[]).map(t =>
          '<span class="badge badge-budget">' + t.name + '</span>'
        ).join('') + '</div>';
    }

    // Prompts tab
    const pmc = $('prompts-content');
    if (pmv.error) {
      pmc.innerHTML = '<p class="text-red-400">Error: ' + pmv.error + '</p>';
    } else {
      pmc.innerHTML = '<div class="grid grid-cols-2 gap-4 mb-4">'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.total_templates + '</div><div class="text-xs text-gray-500">Template Files</div></div>'
        + '<div class="card text-center"><div class="text-2xl font-bold">' + pmv.sessions + '</div><div class="text-xs text-gray-500">Sessions</div></div>'
        + '</div>'
        + Object.entries(pmv.templates||{}).map(([cat, files]) =>
          '<h4 class="font-semibold mt-3 mb-2">' + cat + '</h4>'
          + '<div class="flex flex-wrap gap-2">' + files.map(f =>
            '<span class="badge badge-standard">' + f + '</span>'
          ).join('') + '</div>'
        ).join('');
    }

    // Cases tab (Phase 0)
    $('cases-total').textContent = cv.total || 0;
    $('cases-open').textContent = cv.open || 0;
    $('cases-closed').textContent = cv.closed || 0;
    const cases_body = $('cases-body');
    if (cv.error) {
      cases_body.innerHTML = '<tr><td colspan="9" class="text-center text-red-400">' + cv.error + '</td></tr>';
    } else {
      cases_body.innerHTML = (cv.cases || []).map(c => {
        const status_badge = c.closed_at ? '<span class="badge badge-err">CLOSED</span>' : '<span class="badge badge-ok">OPEN</span>';
        const priority_color = c.priority === 'critical' ? 'text-red-400' : c.priority === 'high' ? 'text-yellow-400' : 'text-gray-300';
        return '<tr>'
          + '<td><strong>' + (c.title || '').substring(0, 40) + '</strong></td>'
          + '<td class="' + priority_color + '">' + (c.priority || '?').toUpperCase() + '</td>'
          + '<td><span class="badge badge-standard">' + (c.mode || '?').toUpperCase() + '</span></td>'
          + '<td>' + (c.facts_count || 0) + '</td>'
          + '<td>' + (c.iocs_count || 0) + '</td>'
          + '<td>' + (c.assets_count || 0) + '</td>'
          + '<td>' + (c.mitre_count || 0) + '</td>'
          + '<td class="text-xs">' + (c.created_at ? c.created_at.substring(0, 10) : '?') + '</td>'
          + '<td>' + status_badge + '</td>'
          + '</tr>';
      }).join('') || '<tr><td colspan="9" class="text-center text-gray-500">No cases found</td></tr>';
    }

    // Tasks tab
    $('tasks-total').textContent = tv.total || 0;
    $('tasks-submitted').textContent = tv.by_state?.submitted || 0;
    $('tasks-working').textContent = tv.by_state?.working || 0;
    $('tasks-completed').textContent = tv.by_state?.completed || 0;
    $('tasks-failed').textContent = tv.by_state?.failed || 0;
    const tasks_body = $('tasks-body');
    if (tv.error) {
      tasks_body.innerHTML = '<tr><td colspan="6" class="text-center text-red-400">' + tv.error + '</td></tr>';
    } else {
      tasks_body.innerHTML = (tv.tasks || []).map(t => {
        const state_badge = t.state === 'completed' ? '<span class="badge badge-ok">✓ DONE</span>'
          : t.state === 'failed' ? '<span class="badge badge-err">✗ FAIL</span>'
          : t.state === 'working' ? '<span class="badge badge-standard">⟳ WORK</span>'
          : t.state === 'submitted' ? '<span class="badge badge-budget">⊕ SBMT</span>'
          : '<span class="badge">' + t.state.toUpperCase() + '</span>';
        const cancel_btn = (t.state === 'completed' || t.state === 'failed' || t.state === 'canceled')
          ? '-'
          : '<button onclick="cancelTask(' + t.id + ')" class="text-xs px-2 py-1 bg-red-900 hover:bg-red-800 rounded">Cancel</button>';
        return '<tr>'
          + '<td class="font-mono text-xs">' + t.id + '</td>'
          + '<td>' + state_badge + '</td>'
          + '<td class="text-xs">' + (t.agent || '?') + '</td>'
          + '<td class="text-xs">' + (t.created_at ? t.created_at.substring(0, 10) : '?') + '</td>'
          + '<td class="text-xs">' + (t.updated_at ? t.updated_at.substring(0, 10) : '?') + '</td>'
          + '<td>' + cancel_btn + '</td>'
          + '</tr>';
      }).join('') || '<tr><td colspan="6" class="text-center text-gray-500">No tasks found</td></tr>';
    }

  } catch (e) {
    console.error('Dashboard refresh error:', e);
  }
}

async function cancelTask(taskId) {
  try {
    const response = await fetch('/dashboard/api/tasks/' + taskId + '/cancel', { method: 'POST' });
    const data = await response.json();
    if (data.status === 'success') {
      alert('Task ' + taskId + ' canceled');
      refresh();
    } else {
      alert('Error: ' + (data.error || 'Unknown error'));
    }
  } catch (e) {
    alert('Failed to cancel task: ' + e);
  }
}

async function fetchApi(endpoint) {
  try {
    const response = await fetch('/dashboard' + endpoint);
    return await response.json();
  } catch (e) {
    console.error('API fetch failed for ' + endpoint, e);
    return { error: 'Failed to fetch: ' + e.message };
  }
}

refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>"""


async def dashboard_page(request: Request) -> HTMLResponse:
    """Serve the dashboard SPA."""
    return HTMLResponse(_DASHBOARD_HTML)


# ── Router ───────────────────────────────────────────────────────────────────

def create_dashboard_router() -> Router:
    """Create the /dashboard router."""
    return Router(routes=[
        Route("/", dashboard_page, methods=["GET"]),
        Route("/api/overview", api_overview, methods=["GET"]),
        Route("/api/providers", api_providers, methods=["GET"]),
        Route("/api/usage", api_usage, methods=["GET"]),
        Route("/api/health", api_health, methods=["GET"]),
        Route("/api/crypto", api_crypto, methods=["GET"]),
        Route("/api/a2a", api_a2a, methods=["GET"]),
        Route("/api/investigations", api_investigations, methods=["GET"]),
        Route("/api/db-counts", api_db_counts, methods=["GET"]),
        Route("/api/agents", api_agents, methods=["GET"]),
        Route("/api/routing", api_routing, methods=["GET"]),
        Route("/api/agent-factory", api_agent_factory, methods=["GET"]),
        Route("/api/prompts", api_prompts, methods=["GET"]),
        # New endpoints
        Route("/api/cases", api_cases, methods=["GET"]),
        Route("/api/tasks", api_tasks, methods=["GET"]),
        Route("/api/tasks/{task_id}/cancel", api_task_cancel, methods=["POST"]),
        Route("/api/findings", api_findings, methods=["GET"]),
        Route("/api/iocs", api_iocs, methods=["GET"]),
        Route("/api/yara", api_yara, methods=["GET"]),
        Route("/api/network", api_network, methods=["GET"]),
        Route("/api/intelligence", api_intelligence, methods=["GET"]),
        Route("/api/audit", api_audit, methods=["GET"]),
        Route("/api/compliance", api_compliance, methods=["GET"]),
        Route("/api/nist-csf", api_nist_csf, methods=["GET"]),
        Route("/api/nist-ai-rmf", api_nist_ai_rmf, methods=["GET"]),
        Route("/api/telemetry", api_telemetry, methods=["GET"]),
        Route("/api/tasks/create", api_task_create, methods=["POST"]),
        Route("/api/tasks/{task_id}", api_task_get, methods=["GET"]),
        # SSE streaming endpoints
        Route("/sse/cases", sse_cases, methods=["GET"]),
        Route("/sse/tasks", sse_tasks, methods=["GET"]),
        Route("/sse/health", sse_health, methods=["GET"]),
        Route("/sse/telemetry", sse_telemetry, methods=["GET"]),
    ])

