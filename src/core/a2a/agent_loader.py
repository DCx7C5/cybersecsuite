"""
Agent Loader — parses .claude/agents/*.md files and registers them in AgentRegistry.

Supports all .claude agent frontmatter fields:
  name, description, model, maxTurns, tools, disallowedTools,
  role (orchestrator, team-mode), default, effort, alias, loaded-by
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from a2a.models import AgentCard, AgentCapabilities, AgentAuthentication, AgentSkill
from a2a.enums import AuthScheme

if TYPE_CHECKING:
    from src.registries.agents import AgentRegistry, RemoteAgent


# ── Frontmatter parsing ───────────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)

# Headings to skip when extracting skills from body
_SKIP_HEADINGS = {
    "rules", "output format", "integration", "behavior",
    "key rules", "crypto stack", "agent hierarchy",
    "project stack", "methodology", "defensive focus areas",
    "core capabilities", "tools", "tool usage",
}

_SKIP_PREFIXES = ("AGENT_", "CLAUDE_", "COPILOT_")


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract and parse YAML frontmatter from a Markdown file."""
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}
    raw = m.group(1)
    if HAS_YAML:
        result = yaml.safe_load(raw)
        return result if isinstance(result, dict) else {}
    # Minimal fallback: key: value, no nesting
    out: Dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _parse_tools(tools_val: Any) -> List[str]:
    """
    Normalize tools field from frontmatter, which can be a list or comma-separated string.
     - If it's a list, convert all items to strings.
     - If it's a string, split by commas and strip whitespace.
     - Otherwise, return an empty list.
    """
    if not tools_val:
        return []
    if isinstance(tools_val, list):
        return [str(t) for t in tools_val]
    if isinstance(tools_val, str):
        return [tools_val]
    return []


def _extract_skills_from_body(body: str, agent_name: str) -> List[AgentSkill]:
    """Derive skills from the Markdown body (## Capabilities / ## sections)."""
    skills: List[AgentSkill] = []
    for m in re.finditer(r'^#{2,3}\s+(.+)$', body, re.MULTILINE):
        heading = m.group(1).strip()
        if heading.lower() in _SKIP_HEADINGS:
            continue
        skill_id = re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')
        if not skill_id:
            continue
        skills.append(AgentSkill(
            id=f"{agent_name}-{skill_id}",
            name=heading,
            tags=[t for t in heading.lower().split() if len(t) > 3],
        ))
    return skills[:8]  # cap at 8 skills per agent


def _source_metadata_for_path(path: Path) -> Dict[str, str]:
    """Classify where an agent definition came from for UI grouping/filtering."""
    parts = set(path.parts)
    if ".claude" in parts and "agents" in parts:
        if path.parent.name == "sub_agents":
            return {"source_kind": "project-sub-agent", "source_label": "Project sub-agent"}
        if path.parent.name == "teams":
            return {"source_kind": "project-team", "source_label": "Project team"}
        if path.parent.name == "agents":
            return {"source_kind": "project-agent", "source_label": "Project agent"}
    return {"source_kind": "external-agent", "source_label": "External agent"}


def iter_agent_markdown_files(
    agents_dir: Path,
    recurse: bool = False,
    include_sub_agents: bool = True,
) -> List[Path]:
    """Return agent markdown files in deterministic priority order."""
    if not agents_dir.exists():
        return []

    groups = [sorted(agents_dir.glob("*.md"))]
    if include_sub_agents:
        groups.append(sorted((agents_dir / "sub_agents").glob("*.md")))
    if recurse:
        groups.append(sorted((agents_dir / "teams").glob("*.md")))

    files: List[Path] = []
    seen_paths: set[Path] = set()
    for group in groups:
        for path in group:
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            files.append(path)
    return files


# ── ClaudeAgentCard ───────────────────────────────────────────────────────────

class ClaudeAgentCard:
    """AgentCard with .claude-specific metadata attached."""

    def __init__(self, card: AgentCard, metadata: Dict[str, Any]) -> None:
        self.name = None
        self.card = card
        self.metadata = metadata

    @property
    def is_default(self) -> bool:
        return bool(self.metadata.get("default", False))

    @property
    def role(self) -> str:
        return self.metadata.get("role", "")

    @property
    def model(self) -> str:
        return self.metadata.get("model", "sonnet")

    @property
    def max_turns(self) -> int:
        return int(self.metadata.get("max_turns", 25))

    @property
    def effort(self) -> str:
        return self.metadata.get("effort", "medium")

    @property
    def tools(self) -> List[str]:
        return self.metadata.get("tools", [])

    @property
    def disallowed_tools(self) -> List[str]:
        return self.metadata.get("disallowed_tools", [])


def frontmatter_to_claude_agent(
    path: Path,
    base_url: str = "http://localhost:8000",
) -> Optional[ClaudeAgentCard]:
    """Parse a .claude/agents/*.md file into a ClaudeAgentCard.

    Returns None for team-mode files and reference-only filenames.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm = _parse_frontmatter(content)

    if fm.get("role") == "team-mode":
        return None
    if any(path.name.startswith(p) for p in _SKIP_PREFIXES):
        return None

    name = str(fm.get("name") or path.stem)
    description = str(fm.get("description") or f"Agent: {name}")
    role = str(fm.get("role", ""))
    model = str(fm.get("model", "sonnet"))
    max_turns = int(fm.get("maxTurns", 25))
    tools = _parse_tools(fm.get("tools"))
    disallowed_tools = _parse_tools(fm.get("disallowedTools"))
    is_default = bool(fm.get("default", False))
    effort = str(fm.get("effort", "medium"))
    alias = fm.get("alias")

    # Extract body (after frontmatter)
    body_match = re.search(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
    body = body_match.group(1) if body_match else content

    # Build skills from body headings + description keywords
    skills = _extract_skills_from_body(body, name)
    if not skills:
        skills = [AgentSkill(
            id=f"{name}-general",
            name=name.replace("-", " ").title(),
            description=description[:100],
            tags=description.lower().split()[:5],
        )]

    # Writable agents (orchestrator or has Written/Edit tools) use Ed25519
    auth_schemes = [AuthScheme.NONE]
    if role == "orchestrator" or (tools and any(t in tools for t in ("Write", "Edit", "MultiEdit"))):
        auth_schemes = [AuthScheme.ED25519, AuthScheme.BEARER]

    card = AgentCard(
        name=name,
        description=description,
        url=base_url,
        version="0.1.0",
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=True,
        ),
        authentication=AgentAuthentication(schemes=auth_schemes),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=skills,
        provider={"name": "cybersecsuite", "url": base_url},
    )

    metadata: Dict[str, Any] = {
        "source": str(path),
        "source_file": path.name,
        "model": model,
        "max_turns": max_turns,
        "effort": effort,
    }
    metadata.update(_source_metadata_for_path(path))
    if role:
        metadata["role"] = role
    if is_default:
        metadata["default"] = True
    if tools:
        metadata["tools"] = tools
    if disallowed_tools:
        metadata["disallowed_tools"] = disallowed_tools
    if alias:
        metadata["alias"] = alias

    return ClaudeAgentCard(card=card, metadata=metadata)


# ── Registry loaders ──────────────────────────────────────────────────────────

def load_agents_from_dir(
    agents_dir: Path,
    registry: AgentRegistry,
    base_url: str = "http://localhost:8000",
    recurse: bool = False,
    include_sub_agents: bool = True,
) -> List[RemoteAgent]:
    """Scan agents_dir for *.md files and register each in the registry.

    Args:
        agents_dir: Path to .claude/agents/
        registry:   AgentRegistry to register into
        base_url:   Base URL for all local agent cards
        recurse:    Also scan teams/ subdirectory
    """
    if not agents_dir.exists():
        return []

    md_files = iter_agent_markdown_files(
        agents_dir,
        recurse=recurse,
        include_sub_agents=include_sub_agents,
    )

    registered: List[RemoteAgent] = []
    seen_names: set[str] = set()
    for md_path in md_files:
        claude_agent = frontmatter_to_claude_agent(md_path, base_url)
        if claude_agent is None:
            continue
        agent_name = claude_agent.card.name.casefold()
        if agent_name in seen_names:
            continue
        seen_names.add(agent_name)
        agent_url = f"{base_url.rstrip('/')}/agents/{claude_agent.card.name}"
        agent = registry.register(agent_url, claude_agent.card)
        agent.claude_metadata = claude_agent.metadata  # type: ignore[attr-defined]
        registered.append(agent)

    return registered


def load_cybersecsuite_agents(
    registry: AgentRegistry,
    project_root: Optional[Path] = None,
    base_url: str = "http://localhost:8000",
) -> List[RemoteAgent]:
    """Load all agents from the cybersecsuite .claude/agents/ directory.

    Auto-detects project root if not provided.
    """
    if project_root is None:
        here = Path(__file__).resolve()
        for candidate in (here.parent.parent.parent, Path.cwd()):
            if (candidate / ".claude" / "agents").exists():
                project_root = candidate
                break

    if project_root is None:
        return []

    return load_agents_from_dir(
        project_root / ".claude" / "agents",
        registry,
        base_url,
        recurse=True,
    )
