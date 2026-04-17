#!/usr/bin/env python3
"""
SessionStart Hook — fires when Claude opens a new session in cybersecsuite.
Loads 3-tier memory (System → Project → Session) and injects A2A registry status.
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_project_dir, get_session_dir, audit, emit, hook_context


AGENT_PROFILES = {
    "cybersec-agent":      "General-purpose cybersec agent — CVE, IOC, MITRE, artifacts.",
    "OrchestratorAgent":   "Multi-agent orchestrator — routes tasks to specialist agents.",
    "PythonDeveloper":     "Python developer — write, review, debug, test Python code.",
    "CppDeveloper":        "C++ developer — write, review, debug, optimize C++ code.",
    "CybersecAgent":       "Threat intelligence agent — CVE, IOC, MITRE ATT&CK.",
}

MEMORY_FILES = ["scope.md", "threat_model.md", "risk_register.md", "mitre-attack.md", "iocs.md"]


async def load_layer(layer_name: str, layer_dir: Path) -> list[str]:
    parts = []
    loop = asyncio.get_running_loop()
    for filename in MEMORY_FILES:
        p = layer_dir / filename
        if p.exists():
            try:
                content = await loop.run_in_executor(None, p.read_text, "utf-8")
                if content.strip():
                    parts.append(f"### {layer_name} — {filename}\n{content.strip()[:800]}")
            except Exception:
                pass
    return parts


async def main():
    ensure_structure()

    project_dir = get_project_dir()
    session_dir = get_session_dir()

    layers = [
        ("System", project_dir / ".memory" / "system"),
        ("Project", project_dir / ".memory" / "project"),
        ("Session", session_dir if session_dir else project_dir / ".memory" / "session"),
    ]

    parts: list[str] = []
    results = await asyncio.gather(*[
        load_layer(name, d) for name, d in layers if d and d.exists()
    ], return_exceptions=True)
    for r in results:
        if isinstance(r, list):
            parts.extend(r)

    memory_ctx = "\n\n".join(parts) or "_No prior memory yet._"

    # A2A registry summary (static read)
    a2a_summary = _a2a_summary(project_dir)

    audit({"event": "SessionStart", "session_dir": str(session_dir)})

    emit(hook_context(f"""🔐 **CYBERSECSUITE SESSION STARTED**
⏱  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

{memory_ctx}

{a2a_summary}

**Active Layers**: System → Project → Session
**Agent**: {_agent_name()}
Ready for investigation."""))


def _agent_name() -> str:
    import os
    name = os.environ.get("CYBERSEC_AGENT_NAME", "cybersec-agent")
    profile = AGENT_PROFILES.get(name, f"Custom agent: {name}")
    return f"{name} — {profile}"


def _a2a_summary(project_dir: Path) -> str:
    settings = project_dir / "settings.json"
    if not settings.exists():
        return ""
    try:
        import json as _json
        data = _json.loads(settings.read_text())
        agent = data.get("agent", "unknown")
        return f"**Configured agent**: `{agent}`\n**A2A Orchestrator**: `OrchestratorAgent` with PythonDeveloper, CppDeveloper, CybersecAgent skills."
    except Exception:
        return ""


if __name__ == "__main__":
    asyncio.run(main())

