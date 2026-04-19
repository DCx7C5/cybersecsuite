"""Agent CRUD API: create, update, delete agent .md files in .claude/agents/."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

_CLAUDE_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".claude"
_AGENTS_DIR = _CLAUDE_DIR / "agents"

PROTECTED_AGENTS = frozenset({
    "cybersec-agent",
    "AGENT_FACTORY",
})

ALLOWED_MODELS = ("haiku", "sonnet", "opus")
ALLOWED_TOOLS = (
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task",
)


def _slugify(name: str) -> str:
    """Convert agent name to valid filename slug."""
    slug = re.sub(r"[^a-z0-9-]", "-", name.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _build_frontmatter(data: dict[str, Any]) -> str:
    """Build YAML frontmatter from agent data."""
    lines = ["---"]
    lines.append(f"name: {data['name']}")
    if data.get("description"):
        desc = data["description"].replace("\n", " ").strip()
        if len(desc) > 80:
            lines.append(f"description: >")
            # Word-wrap at ~78 chars
            words = desc.split()
            current = "  "
            for w in words:
                if len(current) + len(w) + 1 > 78:
                    lines.append(current)
                    current = f"  {w}"
                else:
                    current += f" {w}" if current.strip() else f"  {w}"
            if current.strip():
                lines.append(current)
        else:
            lines.append(f"description: {desc}")
    lines.append(f"model: {data.get('model', 'sonnet')}")
    lines.append(f"maxTurns: {data.get('maxTurns', 25)}")

    if data.get("tools"):
        lines.append("tools:")
        for tool in data["tools"]:
            lines.append(f"  - {tool}")

    if data.get("skills"):
        lines.append("skills:")
        for skill in data["skills"]:
            lines.append(f"  - {skill}")

    if data.get("mcpServers"):
        lines.append("mcpServers:")
        for srv in data["mcpServers"]:
            lines.append(f"  - {srv}")

    lines.append("---")
    return "\n".join(lines)


def _build_body(data: dict[str, Any]) -> str:
    """Build the markdown body for an agent file."""
    title = data["name"].replace("-", " ").title()
    body = f"\n# {title}\n"
    if data.get("instructions"):
        body += f"\n{data['instructions'].strip()}\n"
    return body


async def api_agent_create(request: Request) -> JSONResponse:
    """POST /api/agents — create a new agent .md file.

    Body: {name, description, model?, maxTurns?, tools?, skills?, mcpServers?, instructions?}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    name = body.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    slug = _slugify(name)
    if not slug:
        return JSONResponse({"error": "name produces empty slug"}, status_code=400)

    if name in PROTECTED_AGENTS or slug in PROTECTED_AGENTS:
        return JSONResponse({"error": f"cannot create protected agent: {name}"}, status_code=403)

    # Validate model
    model = body.get("model", "sonnet")
    if model not in ALLOWED_MODELS:
        return JSONResponse({"error": f"invalid model: {model}. Use: {', '.join(ALLOWED_MODELS)}"}, status_code=400)

    # Validate tools
    tools = body.get("tools", list(ALLOWED_TOOLS[:6]))
    for t in tools:
        if t not in ALLOWED_TOOLS:
            return JSONResponse({"error": f"invalid tool: {t}. Allowed: {', '.join(ALLOWED_TOOLS)}"}, status_code=400)

    target = body.get("target_dir", "")
    if target == "sub_agents":
        dest_dir = _AGENTS_DIR / "sub_agents"
    else:
        dest_dir = _AGENTS_DIR

    dest_dir.mkdir(parents=True, exist_ok=True)
    filepath = dest_dir / f"{slug}.md"

    if filepath.exists():
        return JSONResponse({"error": f"agent '{slug}' already exists"}, status_code=409)

    data = {
        "name": slug,
        "description": body.get("description", ""),
        "model": model,
        "maxTurns": body.get("maxTurns", 25),
        "tools": tools,
        "skills": body.get("skills", []),
        "mcpServers": body.get("mcpServers", ["cybersec"]),
        "instructions": body.get("instructions", ""),
    }

    content = _build_frontmatter(data) + _build_body(data)
    filepath.write_text(content, encoding="utf-8")

    return JSONResponse({
        "status": "created",
        "agent": slug,
        "file": filepath.name,
        "path": str(filepath.relative_to(_CLAUDE_DIR.parent)),
    }, status_code=201)


async def api_agent_update(request: Request) -> JSONResponse:
    """PUT /api/agents/{name} — update an existing agent .md file.

    Body: {description?, model?, maxTurns?, tools?, skills?, mcpServers?, instructions?}
    """
    name = request.path_params.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "agent name is required"}, status_code=400)

    if name in PROTECTED_AGENTS:
        return JSONResponse({"error": f"cannot modify protected agent: {name}"}, status_code=403)

    # Find the file (check main dir, sub_agents)
    filepath = None
    for d in (_AGENTS_DIR, _AGENTS_DIR / "sub_agents"):
        candidate = d / f"{name}.md"
        if candidate.exists():
            filepath = candidate
            break

    if not filepath:
        return JSONResponse({"error": f"agent '{name}' not found"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    # Read existing frontmatter
    from dashboard.api.team_builder import _parse_frontmatter
    existing_text = filepath.read_text(encoding="utf-8", errors="replace")
    existing_fm = _parse_frontmatter(existing_text)

    # Merge updates
    data = {
        "name": name,
        "description": body.get("description", existing_fm.get("description", "")),
        "model": body.get("model", existing_fm.get("model", "sonnet")),
        "maxTurns": body.get("maxTurns", existing_fm.get("maxTurns", 25)),
        "tools": body.get("tools", existing_fm.get("tools", [])),
        "skills": body.get("skills", existing_fm.get("skills", [])),
        "mcpServers": body.get("mcpServers", existing_fm.get("mcpServers", [])),
        "instructions": body.get("instructions", ""),
    }

    # Preserve body if no new instructions
    if not data["instructions"]:
        m = re.search(r"^---\n.*?\n---\n?(.*)", existing_text, re.DOTALL)
        body_text = m.group(1).strip() if m else ""
    else:
        body_text = ""

    content = _build_frontmatter(data)
    if data["instructions"]:
        content += _build_body(data)
    elif body_text:
        content += "\n" + body_text + "\n"
    else:
        content += _build_body(data)

    filepath.write_text(content, encoding="utf-8")

    return JSONResponse({
        "status": "updated",
        "agent": name,
        "file": filepath.name,
    })


async def api_agent_delete(request: Request) -> JSONResponse:
    """DELETE /api/agents/{name} — delete an agent .md file."""
    name = request.path_params.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "agent name is required"}, status_code=400)

    if name in PROTECTED_AGENTS:
        return JSONResponse({"error": f"cannot delete protected agent: {name}"}, status_code=403)

    filepath = None
    for d in (_AGENTS_DIR, _AGENTS_DIR / "sub_agents"):
        candidate = d / f"{name}.md"
        if candidate.exists():
            filepath = candidate
            break

    if not filepath:
        return JSONResponse({"error": f"agent '{name}' not found"}, status_code=404)

    filepath.unlink()

    return JSONResponse({
        "status": "deleted",
        "agent": name,
    })


async def api_agent_get(request: Request) -> JSONResponse:
    """GET /api/agents/{name} — get full agent definition including body."""
    name = request.path_params.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "agent name is required"}, status_code=400)

    filepath = None
    for d in (_AGENTS_DIR, _AGENTS_DIR / "sub_agents"):
        candidate = d / f"{name}.md"
        if candidate.exists():
            filepath = candidate
            break

    if not filepath:
        return JSONResponse({"error": f"agent '{name}' not found"}, status_code=404)

    from dashboard.api.team_builder import _parse_frontmatter
    text = filepath.read_text(encoding="utf-8", errors="replace")
    fm = _parse_frontmatter(text)

    # Extract body (after frontmatter)
    m = re.search(r"^---\n.*?\n---\n?(.*)", text, re.DOTALL)
    body = m.group(1).strip() if m else ""

    return JSONResponse({
        "agent": fm.get("name", name),
        "file": filepath.name,
        "source_dir": filepath.parent.name,
        "frontmatter": fm,
        "body": body,
        "raw": text,
    })


# ── Agent Generate (Factory) ──────────────────────────────────────────────────
_TEMPLATES_DIR = _AGENTS_DIR / "agents"

_TYPE_ROLE_MAP = {
    "orchestrator": "Inter-API orchestrator. Routes tasks across multiple API providers and teams via the AI proxy. Delegates to sub-agents using Task tool.",
    "team-leader":  "Claude team orchestrator. Manages a cohesive multi-agent Claude team. Delegates internally using Task tool, stays within a single Claude session.",
    "specialist":   "Specialist sub-agent. Executes focused tasks and returns structured results. Never delegates further.",
}

_RESEARCH_SECTIONS = {
    "mitre":  "## MITRE ATT&CK Context\nReference relevant MITRE ATT&CK techniques, tactics, and mitigations when applicable.",
    "cve":    "## CVE / Vulnerability Context\nCross-reference known CVEs and CVSS scores when analyzing vulnerabilities.",
    "tools":  "## Tool Usage Notes\nDocument tool selection rationale and output expectations for each tool used.",
    "api":    "## API Integration Notes\nDescribe external API calls, authentication, and error handling expectations.",
}

_CHAPTER_TEMPLATE = """\
## Chapter {n}: {title}

{content}
"""


def _build_generated_body(data: dict) -> str:
    """Build a full agent markdown body from factory variables."""
    agent_type  = data.get("type", "specialist")
    name        = data.get("name", "custom-agent")
    description = data.get("description", "")
    model       = data.get("model", "sonnet")
    max_turns   = data.get("maxTurns", 30)
    extra       = data.get("extra_instructions", "").strip()
    research    = data.get("research", [])
    templates   = data.get("agents", [])
    skills      = data.get("skills", [])
    project_ctx = data.get("project_context", False)

    title = name.replace("-", " ").title()
    role_guidance = _TYPE_ROLE_MAP.get(agent_type, _TYPE_ROLE_MAP["specialist"])

    parts = [f"# {title}\n"]
    parts.append(f"**Role**: `{agent_type}` · **Model**: `{model}` · **MaxTurns**: `{max_turns}`\n")

    # Chapter 1: Role & Mission
    mission = description or f"Specialist agent for {title} tasks."
    parts.append(_CHAPTER_TEMPLATE.format(n=1, title="Role & Mission", content=(
        f"**Purpose Statement**: {mission}\n\n"
        f"**Role Guidance**: {role_guidance}"
    )))

    # Chapter 2: Core Principles
    parts.append(_CHAPTER_TEMPLATE.format(n=2, title="Core Principles", content=(
        "- Always validate inputs before acting\n"
        "- Return structured, machine-readable results\n"
        "- Prefer reversible actions\n"
        "- Log all significant actions with timestamps"
    )))

    # Inject template content (selected agents)
    if templates:
        tpl_content_parts = []
        for tpl in templates:
            tpl_path = _TEMPLATES_DIR / f"{tpl}.md"
            if not tpl_path.exists():
                tpl_path = _TEMPLATES_DIR / tpl  # with .md suffix already
            if tpl_path.exists():
                text = tpl_path.read_text(encoding="utf-8", errors="replace").strip()
                tpl_content_parts.append(f"### Template: {tpl}\n\n{text}")
        if tpl_content_parts:
            parts.append("## Chapter 3: Domain Templates\n\n" + "\n\n---\n\n".join(tpl_content_parts) + "\n")

    # Skills reference section
    if skills:
        parts.append("## Skills\n\n" + "\n".join(f"- `{s}`" for s in skills) + "\n")

    # Research sections
    for key in research:
        if key in _RESEARCH_SECTIONS:
            parts.append(_RESEARCH_SECTIONS[key] + "\n")

    # Project context
    if project_ctx:
        parts.append("## Project Context\n\nThis agent operates within the CyberSecSuite project. "
                     "Use `mcp__cybersec__get_project_memory` to load session context before executing tasks.\n")

    # Extra instructions
    if extra:
        parts.append(f"## Additional Instructions\n\n{extra}\n")

    # Orchestrator/team-leader: delegation table stub
    if agent_type in ("orchestrator", "team-leader"):
        parts.append("## Delegation Matrix\n\n"
                     "| Task | Sub-Agent | Tool |\n"
                     "|------|-----------|------|\n"
                     "| _TBD_ | _TBD_ | Task |\n")

    return "\n".join(parts)


async def api_agents_generate(request: Request) -> JSONResponse:
    """POST /api/agents/generate — generate agent markdown via factory variables.

    Body: {
        type, name, description, model, maxTurns, tools,
        agents, research, project_context, extra_instructions, save
    }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    name = body.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    slug = _slugify(name)
    if not slug:
        return JSONResponse({"error": "name produces empty slug"}, status_code=400)

    model = body.get("model", "sonnet")
    if model not in ALLOWED_MODELS:
        return JSONResponse({"error": f"invalid model: {model}"}, status_code=400)

    tools = body.get("tools", list(ALLOWED_TOOLS[:6]))

    data = {
        "name": slug,
        "description": body.get("description", ""),
        "model": model,
        "maxTurns": body.get("maxTurns", 30),
        "tools": tools,
        "type": body.get("type", "specialist"),
        "agents": body.get("agents", []),
        "research": body.get("research", []),
        "project_context": body.get("project_context", False),
        "extra_instructions": body.get("extra_instructions", ""),
    }

    frontmatter = _build_frontmatter(data)
    body_md = _build_generated_body(data)
    content = frontmatter + "\n" + body_md

    result: dict = {"content": content, "agent": slug}

    if body.get("save", True):
        dest_dir = _AGENTS_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)
        filepath = dest_dir / f"{slug}.md"
        if filepath.exists():
            return JSONResponse({"error": f"agent '{slug}' already exists — delete it first or use a different name"}, status_code=409)
        filepath.write_text(content, encoding="utf-8")
        result["file"] = filepath.name
        result["saved"] = True

    return JSONResponse(result, status_code=201 if body.get("save", True) else 200)
