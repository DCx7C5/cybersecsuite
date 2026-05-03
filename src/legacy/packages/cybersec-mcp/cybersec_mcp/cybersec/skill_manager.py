"""Skill management MCP tools."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..helpers import JsonDict, sdk_error, sdk_result
from ..sdk_compat import tool


def _discover_skills(domain: str | None = None, project_dir: Path | None = None) -> list[dict]:
    """Discover skills from marketplace, ~/.claude/skills, and skills-index.json."""
    global_dir = Path("~/.claude").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()

    marketplace_dir = Path("/home/daen/Projects/ai-marketplace/skills")
    marketplace_index = marketplace_dir / "index.json"
    skills_dir = global_dir / "skills"
    index_file = global_dir / "skills-index.json"

    results: list[dict] = []
    seen_ids: set[str] = set()

    def add_skill(skill_data: dict) -> None:
        skill_id = skill_data.get("id") or skill_data.get("path", "")
        if skill_id not in seen_ids:
            results.append(skill_data)
            seen_ids.add(skill_id)

    if marketplace_index.exists():
        try:
            index = json.loads(marketplace_index.read_text())
            skills = index.get("skills", [])
            for s in skills:
                if domain is None or s.get("category", "").startswith(domain):
                    add_skill(s)
            if results:
                return results
        except Exception:
            pass

    if marketplace_dir.exists() and not results:
        for p in sorted(marketplace_dir.rglob("SKILL.md")):
            name = p.parent.name
            rel = str(p.parent.relative_to(marketplace_dir))
            if domain and not rel.startswith(domain):
                continue
            add_skill({
                "name": name,
                "path": str(p),
                "domain": rel.split("/")[0] if "/" in rel else "other",
                "source": "marketplace",
            })

    if index_file.exists():
        try:
            index = json.loads(index_file.read_text())
            skills = index.get("skills", [])
            for s in skills:
                if domain is None or s.get("domain") == domain:
                    add_skill(s)
        except Exception:
            pass

    if skills_dir.exists():
        for p in sorted(skills_dir.rglob("SKILL.md")):
            name = p.parent.name
            rel = str(p.parent.relative_to(skills_dir))
            if domain and not rel.startswith(domain):
                continue
            add_skill({
                "name": name,
                "path": str(p),
                "domain": rel.split("/")[0] if "/" in rel else "other",
                "source": "user",
            })

    return results


@tool(
    "skill_list",
    "List available skills from the registry",
    {"domain": {"type": "string", "description": "Filter by domain (e.g., forensics, ops)"}},
)
async def skill_list(args: dict[str, Any]) -> JsonDict:
    """List all available skills."""
    domain = args.get("domain", "")
    try:
        skills = _discover_skills(domain=domain if domain else None)
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
        all_skills = _discover_skills()
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
        all_skills = _discover_skills()
        skill = next((s for s in all_skills if s.get("name") == name), None)
        if not skill:
            return sdk_error(f"skill {name} not found")
        return sdk_result({"skill": skill})
    except Exception as e:
        return sdk_error(str(e))


ALL_TOOLS = [skill_list, skill_search, skill_load]
