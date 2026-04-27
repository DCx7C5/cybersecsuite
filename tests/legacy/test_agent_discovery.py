from __future__ import annotations

from pathlib import Path

from a2a import agent_sdk
from a2a.agent_loader import load_agents_from_dir
from a2a.registry import AgentRegistry

# Import stubs for deleted src/dashboard/ module
from tests.legacy.conftest import _scan_agents  # noqa: F401


def _write_agent(path: Path, name: str, *, role: str | None = None, tools: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"name: {name}",
        f"description: Test agent {name}",
        "model: sonnet",
        "maxTurns: 10",
        "tools:",
    ]
    for tool in tools or ["Read"]:
        lines.append(f"  - {tool}")
    if role:
        lines.append(f"role: {role}")
    lines.extend(["---", "", f"# {name}", "", "## Capabilities", "- test"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_load_agents_from_dir_includes_sub_agents_and_dedupes(tmp_path: Path) -> None:
    agents_dir = tmp_path / ".claude" / "agents"
    _write_agent(agents_dir / "alpha.md", "alpha")
    _write_agent(agents_dir / "sub_agents" / "beta.md", "beta")
    _write_agent(agents_dir / "sub_agents" / "alpha.md", "alpha")

    registry = AgentRegistry()
    load_agents_from_dir(agents_dir, registry)
    summary = {entry["name"]: entry for entry in registry.summary()}

    assert set(summary) == {"alpha", "beta"}
    assert summary["alpha"]["claude_metadata"]["source_kind"] == "project-agent"
    assert summary["beta"]["claude_metadata"]["source_kind"] == "project-sub-agent"


def test_load_claude_agents_includes_sub_agents_and_orchestrators(monkeypatch, tmp_path: Path) -> None:
    agents_dir = tmp_path / ".claude" / "agents"
    _write_agent(agents_dir / "cybersec-agent.md", "cybersec-agent", role="orchestrator", tools=["Read", "Task"])
    _write_agent(agents_dir / "sub_agents" / "python-developer.md", "python-developer", tools=["Read", "Write"])

    monkeypatch.setattr(agent_sdk, "_find_project_root", lambda: tmp_path)

    cards = agent_sdk.load_claude_agents()
    defs = agent_sdk.build_agent_definitions()

    assert set(cards) == {"cybersec-agent", "python-developer"}
    assert "cybersec-agent" in defs
    assert "Agent" in defs["cybersec-agent"].tools


def test_team_builder_scan_agents_dedupes_names(monkeypatch, tmp_path: Path) -> None:
    agents_dir = tmp_path / ".claude" / "agents"
    _write_agent(agents_dir / "frontend.md", "frontend")
    _write_agent(agents_dir / "sub_agents" / "frontend.md", "frontend")
    _write_agent(agents_dir / "sub_agents" / "network.md", "network")

    monkeypatch.setattr("dashboard.api.team_builder._AGENTS_DIR", agents_dir)

    agents = _scan_agents()

    assert [agent["name"] for agent in agents] == ["frontend", "network"]
    assert agents[0]["source_dir"] == "agents"
    assert agents[1]["source_dir"] == "sub_agents"
