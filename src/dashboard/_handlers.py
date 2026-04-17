"""Dashboard API + SSE request handlers."""
from __future__ import annotations

import time
from pathlib import Path

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, StreamingResponse

from dashboard._html import _DASHBOARD_HTML

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
    """Agent factory metadata: available plugins, capabilities."""
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
        "plugins": ["orchestrator", "specialist"],
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

        _FINDING_FIELDS = [
            "id", "title", "description", "severity", "status", "confidence",
            "location", "evidence", "evidence_hash", "command_output",
            "cross_validation", "next_action", "analyst_notes", "remediation",
            "resolved_at", "tags", "created_at", "updated_at", "is_active",
        ]
        recent = await Finding.all().order_by("-created_at").limit(20).values(*_FINDING_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
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

        _IOC_FIELDS = [
            "id", "ioc_id", "ioc_type", "value", "confidence", "status",
            "sightings", "context", "source", "evidence_hash", "tags",
            "created_at", "updated_at", "is_active",
        ]
        recent = await IOC.all().order_by("-updated_at").limit(20).values(*_IOC_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
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

        _YARA_FIELDS = [
            "id", "rule_id", "name", "description", "content", "status", "source",
            "severity", "detection_count", "false_positive_rate",
            "test_results", "tags", "created_at", "updated_at",
        ]
        # Use values() to avoid enum instantiation issues
        try:
            recent = await YaraRule.all().order_by("-created_at").limit(20).values(*_YARA_FIELDS)
        except Exception:
            # Fallback if some fields don't exist on this model version
            recent = await YaraRule.all().order_by("-created_at").limit(20).values(
                "id", "rule_id", "name", "status", "source", "created_at"
            )
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
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
    """Network assets summary — hosts and IP addresses with full fields."""
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

        recent_hosts = await Host.all().order_by("-created_at").limit(20).values(
            "id", "hostname", "os_name", "os_version", "architecture",
            "is_localhost", "is_target", "is_compromised", "notes", "created_at",
        )
        recent_hosts_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_hosts
        ]

        recent_ips = await IPAddress.all().order_by("-last_seen_at").limit(20).values(
            "id", "address", "version", "is_private", "geo_country",
            "first_seen_at", "last_seen_at", "notes",
        )
        recent_ips_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_ips
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "hosts": {"total": total_hosts, "compromised": compromised, "targets": targets},
        "ip_addresses": {"total": total_ips, "private": private_ips, "public": total_ips - private_ips},
        "top_countries": top_countries,
        "recent_hosts": recent_hosts_list,
        "recent_ips": recent_ips_list,
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

        # Recent MITRE techniques with full fields
        _MITRE_FIELDS = [
            "id", "technique_id", "name", "description", "tactics",
            "platforms", "data_sources", "is_sub_technique", "parent_technique_id",
            "detection", "url", "tags", "created_at", "updated_at",
        ]
        recent_mitre = await MitreTechniqueIntel.all().order_by("-created_at").limit(10).values(*_MITRE_FIELDS)
        recent_mitre_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_mitre
        ]

        # Recent CVE entries with full fields
        _CVE_FIELDS = ["id", "cve_id", "cvss_score", "severity", "description",
                       "exploit_available", "patch_available", "published_at", "tags", "created_at"]
        try:
            from db.models.cve import CVEIntel
            recent_cve = await CVEIntel.all().order_by("-published_at").limit(10).values(*_CVE_FIELDS)
        except Exception:
            recent_cve = []
        recent_cve_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent_cve
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "mitre": {"techniques": mitre_count, "tactics": unique_tactics},
        "cve": {"total": cve_count},
        "cwe": {"total": cwe_count},
        "capec": {"total": capec_count},
        "last_seeded": last_seeded,
        "recent_mitre": recent_mitre_list,
        "recent_cve": recent_cve_list,
    })


async def api_audit(request: Request) -> JSONResponse:
    """Audit log summary — recent entries and action counts."""
    try:
        from db.models.audit import AuditLog
        import datetime as _dt

        total = await AuditLog.all().count()
        _AUDIT_FIELDS = [
            "id", "action", "entity_type", "entity_id", "entity_repr",
            "agent", "resource", "ip_address", "old_value", "new_value",
            "metadata", "created_at",
        ]
        recent = await AuditLog.all().order_by("-created_at").limit(50).values(*_AUDIT_FIELDS)

        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]

        # Count by action
        by_action: dict[str, int] = {}
        for e in recent_list:
            a = e.get("action") or "unknown"
            by_action[a] = by_action.get(a, 0) + 1

        # Count by agent
        by_agent: dict[str, int] = {}
        for e in recent_list:
            ag = e.get("agent") or "unknown"
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
    """Compliance rules summary — totals by framework and severity + recent rules."""
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

        _COMPLIANCE_FIELDS = [
            "id", "rule_id", "title", "description", "framework", "severity",
            "check_procedures", "remediation_steps", "evidence_requirements",
            "retention_period_days", "audit_frequency", "created_at", "updated_at",
        ]
        recent = await ComplianceRule.all().order_by("-created_at").limit(20).values(*_COMPLIANCE_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_framework": dict(sorted(by_framework.items(), key=lambda x: -x[1])),
        "by_severity": by_severity,
        "recent": recent_list,
    })


async def api_nist_csf(request: Request) -> JSONResponse:
    """NIST CSF 2.0 controls — totals by function/category + recent controls."""
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

        # Full fields for recent controls
        _CSF_FIELDS = list(NistCsfControl._meta.fields_map.keys())
        _CSF_SCALAR = [f for f in _CSF_FIELDS
                       if type(NistCsfControl._meta.fields_map[f]).__name__ not in (
                           "ForeignKeyFieldInstance", "ManyToManyFieldInstance",
                           "BackwardsOneToOneRelation", "BackwardsFKRelation",
                       )]
        recent = await NistCsfControl.all().order_by("function_code").limit(20).values(*_CSF_SCALAR)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "recent": recent_list,
    })


async def api_nist_ai_rmf(request: Request) -> JSONResponse:
    """NIST AI RMF 1.0 controls — totals by function/topic + recent controls."""
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

        _RMF_FIELDS = list(NistAiRmfControl._meta.fields_map.keys())
        _RMF_SCALAR = [f for f in _RMF_FIELDS
                       if type(NistAiRmfControl._meta.fields_map[f]).__name__ not in (
                           "ForeignKeyFieldInstance", "ManyToManyFieldInstance",
                           "BackwardsOneToOneRelation", "BackwardsFKRelation",
                       )]
        recent = await NistAiRmfControl.all().order_by("function").limit(20).values(*_RMF_SCALAR)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_topic": dict(sorted(by_topic.items(), key=lambda x: -x[1])),
        "recent": recent_list,
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


# ── Generic table endpoint ───────────────────────────────────────────────────

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


# ── Agent-SDK query endpoint ──────────────────────────────────────────────────

async def api_agent_query(request: Request) -> JSONResponse:
    """POST /api/agent-query — run a prompt through an agent via the agent-sdk.

    Body: {agent: str, prompt: str, context_table?: str, row_ids?: list[int]}
    Returns: {agent, response, session_id, elapsed_ms}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "error": "invalid JSON body"}, status_code=400)

    agent_name: str = body.get("agent", "cybersec")
    prompt: str = body.get("prompt", "")
    context_table: str | None = body.get("context_table")
    row_ids: list[int] = body.get("row_ids") or []

    if not prompt:
        return JSONResponse({"status": "error", "error": "prompt is required"}, status_code=400)

    # Optionally enrich prompt with DB context
    if context_table and row_ids:
        from dashboard._schema import resolve_model, fetch_rows
        info = resolve_model(context_table)
        if info:
            rows, _ = await fetch_rows(
                model_cls=info["model_cls"],
                scalar_fields=info["scalar_fields"],
                page=1,
                limit=min(len(row_ids), 20),
                sort=None,
                filters={"id__in": row_ids} if "id" in info["scalar_fields"] else {},
            )
            if rows:
                import json
                context_snippet = json.dumps(rows[:5], default=str)
                prompt = f"{prompt}\n\nContext ({context_table} rows):\n{context_snippet}"

    try:
        import time
        import asyncio
        from a2a.agent_sdk import run_agent_query

        t0 = time.monotonic()
        result = await asyncio.wait_for(
            run_agent_query(agent_name=agent_name, prompt=prompt),
            timeout=120,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
    except asyncio.TimeoutError:
        return JSONResponse({"status": "error", "error": "agent query timed out (120s)"}, status_code=504)
    except Exception as exc:
        return JSONResponse({"status": "error", "error": str(exc)}, status_code=500)

    return JSONResponse({
        "agent": agent_name,
        "response": result,
        "elapsed_ms": elapsed_ms,
    })


# ── Dashboard HTML (self-contained) ──────────────────────────────────────────

async def dashboard_page(request: Request) -> HTMLResponse:
    """Serve the dashboard SPA."""
    return HTMLResponse(_DASHBOARD_HTML)


# ── Router ───────────────────────────────────────────────────────────────────

