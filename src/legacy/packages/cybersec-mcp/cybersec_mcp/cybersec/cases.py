"""Investigation case tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from ..helpers import JsonDict, _get_current_scope, sdk_error, sdk_result
from ..sdk_compat import tool


@tool(
    "case_open",
    "Open a new investigation case (Phase 0). Creates a CaseIntake record and sets session phase.",
    {
        "title": "string",
        "problem_statement": "string",
        "attack_hypothesis": {"type": "string", "default": ""},
        "known_facts": {"type": "array", "items": {"type": "string"}, "default": []},
        "suspected_iocs": {"type": "array", "items": {"type": "string"}, "default": []},
        "affected_assets": {"type": "array", "items": {"type": "string"}, "default": []},
        "timeline_hints": {"type": "array", "items": {"type": "string"}, "default": []},
        "scope_in": {"type": "array", "items": {"type": "string"}, "default": []},
        "scope_out": {"type": "array", "items": {"type": "string"}, "default": []},
        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
        "mode": {"type": "string", "enum": ["blue", "red", "purple"], "default": "blue"},
        "mitre_hypotheses": {"type": "array", "items": {"type": "string"}, "default": []},
        "data_sources": {"type": "array", "items": {"type": "string"}, "default": []},
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
        "analyst_notes": {"type": "string", "default": ""},
    },
)
async def case_open(args: dict[str, Any]) -> JsonDict:
    try:
        from db.bootstrap import init_tortoise_async
        await init_tortoise_async()
        from db.models.case_intake import CaseIntake
        from db.models.layers import SessionLayer
        from db.models.scope import ProjectScope, SessionScope
    except ImportError as exc:
        return sdk_error(f"db models not available: {exc}")

    scope = _get_current_scope()
    title = args["title"]
    problem_statement = args["problem_statement"]
    attack_hypothesis = args.get("attack_hypothesis", "")
    known_facts = args.get("known_facts", [])
    suspected_iocs = args.get("suspected_iocs", [])
    affected_assets = args.get("affected_assets", [])
    timeline_hints = args.get("timeline_hints", [])
    scope_in = args.get("scope_in", [])
    scope_out = args.get("scope_out", [])
    priority = args.get("priority", "medium")
    mode = args.get("mode", "blue")
    mitre_hypotheses = args.get("mitre_hypotheses", [])
    data_sources = args.get("data_sources", [])
    tags = args.get("tags", [])
    analyst_notes = args.get("analyst_notes", "")

    try:
        proj = None
        if scope.get("project"):
            proj, _ = await ProjectScope.get_or_create(name=scope["project"])
        sess = None
        if scope.get("session"):
            sess = await SessionScope.get_or_none(session_id=scope["session"])
            if sess:
                sess.phase = "case_opening"
                sess.mode = mode
                await sess.save()

        intake = await CaseIntake.create(
            project=proj, session=sess,
            title=title, problem_statement=problem_statement, attack_hypothesis=attack_hypothesis,
            known_facts=known_facts, suspected_iocs=suspected_iocs, affected_assets=affected_assets,
            timeline_hints=timeline_hints, scope_in=scope_in, scope_out=scope_out,
            priority=priority, mode=mode, mitre_hypotheses=mitre_hypotheses,
            data_sources=data_sources, tags=tags, analyst_notes=analyst_notes,
        )

        if sess:
            layer, _ = await SessionLayer.get_or_create(
                session=sess, defaults={"name": f"phase0-{sess.session_id}"},
            )
            layer.active_phase = "case_opening"
            layer.current_hypotheses = mitre_hypotheses
            layer.investigation_focus = affected_assets
            layer.analysis_notes = (
                f"Case: {title}\nHypothesis: {attack_hypothesis}\n"
                f"Facts: {'; '.join(known_facts)}"
            )
            await layer.save()

        return sdk_result({
            "status": "success", "case_id": intake.id, "title": title,
            "priority": priority, "mode": mode, "phase": "case_opening",
            "facts_count": len(known_facts), "iocs_count": len(suspected_iocs),
            "assets_count": len(affected_assets), "mitre_count": len(mitre_hypotheses),
            "message": f"Case '{title}' opened. Ready for Phase 1 (Recon).",
        })
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "case_status",
    "Get the status of the current or a specific case intake by ID.",
    {"case_id": {"type": "integer", "nullable": True}},
)
async def case_status(args: dict[str, Any]) -> JsonDict:
    try:
        from db.bootstrap import init_tortoise_async
        await init_tortoise_async()
        from db.models.case_intake import CaseIntake
    except ImportError as exc:
        return sdk_error(f"db models not available: {exc}")

    try:
        case_id = args.get("case_id")
        if case_id:
            intake = await CaseIntake.get_or_none(id=case_id)
        else:
            intake = await CaseIntake.all().order_by("-created_at").first()

        if not intake:
            return sdk_error("No case found")

        return sdk_result({
            "status": "success",
            "case": {
                "id": intake.id, "title": intake.title,
                "problem": intake.problem_statement,
                "hypothesis": intake.attack_hypothesis,
                "priority": intake.priority.value if hasattr(intake.priority, "value") else intake.priority,
                "mode": intake.mode.value if hasattr(intake.mode, "value") else intake.mode,
                "known_facts": intake.known_facts, "suspected_iocs": intake.suspected_iocs,
                "affected_assets": intake.affected_assets, "timeline_hints": intake.timeline_hints,
                "scope_in": intake.scope_in, "scope_out": intake.scope_out,
                "mitre_hypotheses": intake.mitre_hypotheses, "data_sources": intake.data_sources,
                "tags": intake.tags, "opened_by": intake.opened_by,
                "created_at": intake.created_at.isoformat() if intake.created_at else None,
                "closed_at": intake.closed_at.isoformat() if intake.closed_at else None,
            },
        })
    except Exception as exc:
        return sdk_error(str(exc))


ALL_TOOLS = [case_open, case_status]
