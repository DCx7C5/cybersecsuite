"""Team Builder API: agents, skills, teams from .claude/ filesystem."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from a2a.agent_loader import iter_agent_markdown_files

_CLAUDE_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".claude"
_AGENTS_DIR = _CLAUDE_DIR / "agents"
_SKILLS_DIR = _CLAUDE_DIR / "skills"

# ── Frontmatter parser ────────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract YAML-ish frontmatter between --- delimiters."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in block.splitlines():
        if line.startswith("  - ") or line.startswith("- "):
            val = line.lstrip("- ").strip()
            if current_list_key:
                result[current_list_key].append(val)
        elif ":" in line and not line.startswith(" "):
            current_list_key = None
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                result[key] = []
                current_list_key = key
            elif val.lower() in ("true", "yes"):
                result[key] = True
            elif val.lower() in ("false", "no"):
                result[key] = False
            else:
                try:
                    result[key] = int(val)
                except ValueError:
                    result[key] = val.strip('"').strip("'")
    return result


def _scan_agents() -> list[dict]:
    """Parse frontmatter from all .claude/agents/**/*.md files."""
    agents = []
    seen_names: set[str] = set()
    for md in iter_agent_markdown_files(_AGENTS_DIR, recurse=False, include_sub_agents=True):
        if md.name.upper().startswith(("AGENT_FACTORY", "DEV_", "CLAUDE_", "COPILOT_")):
            continue
        try:
            fm = _parse_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            if not fm.get("name"):
                fm["name"] = md.stem
            key = str(fm["name"]).casefold()
            if key in seen_names:
                continue
            seen_names.add(key)
            fm["file"] = md.name
            fm["source_dir"] = md.parent.name
            agents.append(fm)
        except Exception:
            continue
    return agents


def _scan_teams() -> list[dict]:
    """Parse frontmatter from .claude/agents/teams/*.md."""
    teams_dir = _AGENTS_DIR / "teams"
    if not teams_dir.exists():
        return []
    teams = []
    for md in sorted(teams_dir.glob("*.md")):
        try:
            fm = _parse_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            if not fm.get("name"):
                fm["name"] = md.stem
            fm["file"] = md.name
            teams.append(fm)
        except Exception:
            continue
    return teams


def _scan_skills(domain_filter: str = "", query: str = "") -> tuple[list[str], list[dict]]:
    """Scan SKILL.md files and return (domains, skills)."""
    # Derive domain from top-level subdirectory name
    domains: list[str] = sorted(d.name for d in _SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    skills = []
    ql = query.lower()
    for skill_file in sorted(_SKILLS_DIR.rglob("SKILL.md")):
        # Top-level dir relative to skills root = domain
        rel = skill_file.relative_to(_SKILLS_DIR)
        top = rel.parts[0] if len(rel.parts) > 1 else ""
        if domain_filter and top != domain_filter:
            continue
        try:
            fm = _parse_frontmatter(skill_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not fm.get("name"):
            continue
        entry = {
            "name": fm.get("name", ""),
            "domain": top or fm.get("domain", ""),
            "subdomain": fm.get("subdomain", ""),
            "description": fm.get("description", ""),
            "tags": fm.get("tags") if isinstance(fm.get("tags"), list) else [],
            "mitre_attack": fm.get("mitre_attack") if isinstance(fm.get("mitre_attack"), list) else [],
        }
        if ql:
            haystack = (entry["name"] + " " + entry["description"] + " " + " ".join(entry["tags"])).lower()
            if ql not in haystack:
                continue
        skills.append(entry)
    return domains, skills


# ── Handlers ─────────────────────────────────────────────────────────────────

async def api_team_agents(request: Request) -> JSONResponse:
    """List all agents parsed from .claude/agents/."""
    try:
        agents = _scan_agents()
        return JSONResponse({"total": len(agents), "agents": agents})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_skills(request: Request) -> JSONResponse:
    """List skills, optionally filtered by domain and search query."""
    domain = request.query_params.get("domain", "")
    query = request.query_params.get("q", "")
    try:
        domains, skills = _scan_skills(domain_filter=domain, query=query)
        return JSONResponse({"total": len(skills), "domains": domains, "skills": skills})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_teams(request: Request) -> JSONResponse:
    """List team mode definitions from .claude/agents/teams/."""
    try:
        teams = _scan_teams()
        return JSONResponse({"total": len(teams), "teams": teams})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
