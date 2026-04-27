#!/usr/bin/env python3
"""
FirstInit Hook — one-time bootstrap for cybersecsuite.
Creates directory structure, writes system baseline, registers agent card.
"""
import asyncio
import json
import platform
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

from hooks.utils import get_project_dir, get_app_home, hook_context, emit, ensure_structure, audit

sys.path.insert(0, str(Path(__file__).resolve().parent))

MARKER = get_project_dir() / ".claude" / ".initialized"


async def main(SESSIONS_DIR=None):
    project_dir = get_project_dir()
    app_home = get_app_home()

    if MARKER.exists():
        emit(hook_context("✅ **CyberSecSuite already initialized** — skipping FirstInit."))
        return

    ensure_structure()

    # Create memory hierarchy under app home
    for layer in ["system", "project", "session"]:
        (app_home / "memory" / layer).mkdir(parents=True, exist_ok=True)

    # System baseline
    sys_info = {
        "hostname":    socket.gethostname(),
        "os":          platform.system(),
        "os_version":  platform.release(),
        "arch":        platform.machine(),
        "python":      platform.python_version(),
        "initialized": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_dir),
        "app_home": str(app_home),
    }

    sys_dir = app_home / "memory" / "system"
    (sys_dir / "baseline.json").write_text(json.dumps(sys_info, indent=2))
    (sys_dir / "scope.md").write_text(
        f"# CyberSecSuite Scope\n\n"
        f"Host: `{sys_info['hostname']}`  \nOS: `{sys_info['os']} {sys_info['os_version']}`  \n"
        f"Project: `{project_dir}`\n"
        f"App home: `{app_home}`\n\n"
        "## Active Agents\n- cybersec-agent (SDK → .claude/agents/ → AI Proxy)\n"
    )

    # Write init marker
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(datetime.now(timezone.utc).isoformat())

    # Sessions dir
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    audit({"event": "FirstInit", "host": sys_info["hostname"]})

    emit(hook_context(
        f"🚀 **CYBERSECSUITE INITIALIZED**\n\n"
        f"Host: `{sys_info['hostname']}` | OS: `{sys_info['os']} {sys_info['os_version']}`\n"
        f"Project root: `{project_dir}`\n"
        f"App home: `{app_home}`\n\n"
        "**Memory layers created:** System → Project → Session\n"
        "**A2A agent registered:** CybersecA2AAgent (SDK routes to .claude/agents/)\n\n"
        "Ready for investigation."
    ))


if __name__ == "__main__":
    asyncio.run(main())
