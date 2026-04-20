"""Skill management MCP tools."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "skill_list",
    "List available skills from the registry",
    {"domain": {"type": "string", "description": "Filter by domain (e.g., forensics, ops)"}},
)
async def skill_list(args: dict[str, Any]) -> JsonDict:
    """List all available skills."""
    domain = args.get("domain", "")
    try:
        from template_engine.discovery import discover_skills
    except ImportError:
        return sdk_error("template_engine not available")

    try:
        skills = discover_skills(domain=domain if domain else None)
        return sdk_result({"skills": skills, "count": len(skills)})
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "skill_search",
    "Search skills by keyword",
    {"query": {"type": "string", "description": "Search query"}},
)
async def skill_search(args: dict[str, Any]) -> JsonDict:
    """Search skills by keyword."""
    query = args.get("query", "").strip()
    if not query:
        return sdk_error("query is required")

    try:
        from template_engine.discovery import discover_skills
    except ImportError:
        return sdk_error("template_engine not available")

    try:
        all_skills = discover_skills()
        query_lower = query.lower()
        matches = [
            s for s in all_skills
            if query_lower in s.get("name", "").lower() or query_lower in s.get("description", "").lower()
        ]
        return sdk_result({"skills": matches, "count": len(matches)})
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "skill_load",
    "Load a skill by name",
    {"name": {"type": "string", "description": "Skill name to load"}},
)
async def skill_load(args: dict[str, Any]) -> JsonDict:
    """Load a specific skill."""
    name = args.get("name", "").strip()
    if not name:
        return sdk_error("name is required")

    try:
        from template_engine.discovery import discover_skills
    except ImportError:
        return sdk_error("template_engine not available")

    try:
        all_skills = discover_skills()
        skill = next((s for s in all_skills if s.get("name") == name), None)
        if not skill:
            return sdk_error(f"skill {name} not found")
        return sdk_result({"skill": skill})
    except Exception as e:
        return sdk_error(str(e))


ALL_TOOLS = [skill_list, skill_search, skill_load]