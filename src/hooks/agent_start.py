#!/usr/bin/env python3
"""
AgentStart Hook — fires when any A2A agent begins work in cybersecsuite.
Logs timeline entry, writes agent_active.json, injects context.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin

AGENT_PROFILES = {
    "cybersec-agent":     "General-purpose cybersec agent.",
    "CybersecAgent":      "Threat intelligence — CVE, IOC, MITRE ATT&CK, artifact signing.",
}


async def main():
    ensure_structure()
    data = read_stdin()

    agent_name = (
        data.get("agent_name")
        or data.get("agent")
        or os.environ.get("CYBERSEC_AGENT_NAME")
        or "unknown"
    )
    session_id = data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""

    project_dir = get_project_dir()
    session_dir = get_session_dir()
    start_time  = datetime.now(timezone.utc)

    loop = asyncio.get_running_loop()

    # Timeline entry
    if session_dir:
        timeline = session_dir / "timeline.md"
        entry = f"| {start_time.strftime('%H:%M:%S')} | agent_start | **{agent_name}** | — |\n"
        await loop.run_in_executor(None, append_file, timeline, entry)

    # agent_active.json
    state_file = project_dir / ".agent_active.json"
    payload = {"agent_name": agent_name, "started_at": start_time.isoformat(), "session_id": session_id}
    await loop.run_in_executor(None, state_file.write_text, json.dumps(payload, indent=2), "utf-8")

    # Changelog
    changelog = project_dir / "session_changes.log"
    await loop.run_in_executor(
        None, append_file, changelog,
        f"[{start_time.isoformat(timespec='seconds')}] agent_start: {agent_name}\n"
    )

    # Recent summary
    summary = ""
    if session_dir:
        sp = session_dir / "summary.md"
        if sp.exists():
            summary = (await loop.run_in_executor(None, sp.read_text, "utf-8"))[:1500]

    audit({"event": "AgentStart", "agent": agent_name, "session_id": session_id})

    profile = AGENT_PROFILES.get(agent_name, f"Custom agent: {agent_name}")
    emit(hook_context(f"""🕵️ **AGENT STARTED: {agent_name}**
⏱  {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
📋 Profile: {profile}

{summary}

**Agent `{agent_name}` is now active.** All findings will be attributed to this agent."""))


if __name__ == "__main__":
    asyncio.run(main())

