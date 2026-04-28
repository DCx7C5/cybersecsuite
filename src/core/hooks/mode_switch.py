#!/usr/bin/env python3
"""
ModeSwitch Hook — switches Blue/Red/Purple team mode.
Updates session, adjusts agent behaviour context.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin

MODE_PROFILES = {
    "blue":   {"emoji": "🔵", "label": "Defensive / Forensic", "focus": "Detection, monitoring, incident response, artifact signing."},
    "red":    {"emoji": "🔴", "label": "Offensive / Adversarial", "focus": "Exploit development, penetration testing, adversary simulation."},
    "purple": {"emoji": "🟣", "label": "Purple Team", "focus": "Attack simulation with defensive coverage validation."},
    "hunt":   {"emoji": "🟠", "label": "Threat Hunting", "focus": "Proactive IOC search, anomaly detection, MITRE ATT&CK coverage."},
}


async def main():
    ensure_structure()
    data = read_stdin()

    new_mode   = (data.get("mode") or os.environ.get("CYBERSEC_MODE", "blue")).lower()
    agent_name = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))
    reason     = data.get("reason", "")

    session_dir = get_session_dir()
    project_dir = get_project_dir()
    now         = datetime.now(timezone.utc)

    profile = MODE_PROFILES.get(new_mode, MODE_PROFILES["blue"])

    # Persist mode to project state
    state = {
        "mode":       new_mode,
        "switched_at": now.isoformat(),
        "switched_by": agent_name,
        "reason":     reason,
    }
    (project_dir / ".claude" / ".mode.json").write_text(json.dumps(state, indent=2))

    if session_dir:
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | mode_switch | {agent_name} | → {new_mode.upper()} |\n"
        )

    append_file(
        project_dir / "session_changes.log",
        f"[{now.isoformat(timespec='seconds')}] mode_switch: {new_mode} by {agent_name}\n"
    )

    audit({"event": "ModeSwitch", "mode": new_mode, "agent": agent_name})

    emit(hook_context(
        f"{profile['emoji']} **MODE SWITCHED → {new_mode.upper()} TEAM**\n\n"
        f"**Mode:** {profile['label']}\n"
        f"**Focus:** {profile['focus']}\n"
        f"**Agent:** {agent_name}\n"
        + (f"**Reason:** {reason}\n" if reason else "")
        + f"\nAll subsequent agent actions will respect `{new_mode}` mode constraints."
    ))


if __name__ == "__main__":
    asyncio.run(main())

