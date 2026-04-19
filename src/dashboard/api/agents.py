"""Agent and routing API handlers: agents, routing, agent factory, A2A, agent query."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from ai_proxy.routing.combo import (
    RoutingTier,
    Strategy,
    budget_guard,
    get_circuit_breaker_status,
    get_usage_counts,
)


def _agent_priority(entry: dict) -> tuple[int, int, int, str]:
    meta = entry.get("claude_metadata") or {}
    source_kind = meta.get("source_kind", "")
    source_rank = {
        "project-agent": 3,
        "project-sub-agent": 2,
        "project-team": 1,
        "external-agent": 0,
    }.get(source_kind, 0)
    return (
        source_rank,
        1 if meta.get("default") else 0,
        1 if meta.get("role") == "orchestrator" else 0,
        entry.get("name", "").lower(),
    )


def _dedupe_agent_summaries(agents: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for entry in agents:
        name = str(entry.get("name", "")).strip()
        if not name:
            continue
        key = name.casefold()
        current = deduped.get(key)
        if current is None or _agent_priority(entry) > _agent_priority(current):
            deduped[key] = entry
    return sorted(
        deduped.values(),
        key=lambda entry: (
            -int(bool((entry.get("claude_metadata") or {}).get("default"))),
            -int((entry.get("claude_metadata") or {}).get("role") == "orchestrator"),
            -_agent_priority(entry)[0],
            entry.get("name", "").lower(),
        ),
    )


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

        agents = _dedupe_agent_summaries(agents)

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


async def api_agent_query(request: Request) -> JSONResponse:
    """POST /api/agent-query — run a prompt through an agent via the agent-sdk.

    Body: {agent: str, prompt: str, context_table?: str, row_ids?: list[int]}
    Returns: {agent, response, session_id, elapsed_ms}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "error": "invalid JSON body"}, status_code=400)

    agent_name: str = body.get("agent", "cybersec-agent")
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
