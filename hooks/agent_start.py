#!/usr/bin/env python3
"""
AgentStart Hook — fires when any cybersec agent begins work.

Now includes a full AgentRootPermission check before any write operations.
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

from uvloop_integration import run_with_uvloop, get_event_loop_info
from utils import get_project_dir, get_session_dir, ensure_structure
from db.models.permission_checker import check_agent_permission

# Known agents → short descriptions for context injection
AGENT_PROFILES = {
    "Hunter":             "General-purpose threat hunter — broad recon across all layers.",
    "Hunter_Elite":       "Advanced threat hunter — APT-level persistence, rootkits, supply-chain.",
    "Layer2-Specialist":  "Data-link layer — ARP, MAC, VLAN, switch-level attacks.",
    "Layer3-Specialist":  "Network layer — IP, routing, ICMP, BGP hijack.",
    "Layer4-Specialist":  "Transport layer — TCP/UDP, port scans, SYN floods.",
    "Layer5-Specialist":  "Session layer — TLS, session hijack, auth tokens.",
    "Layer6-Specialist":  "Presentation layer — encoding, serialization, crypto.",
    "Layer7-Specialist":  "Application layer — HTTP, DNS, API, web app exploits.",
    "Memory-Analyst":     "Volatile memory forensics — process injection, rootkits in RAM.",
    "Firmware-Analyst":   "Firmware extraction, diffing, UEFI/BIOS implant detection.",
    "Reverse-Engineer":   "Binary analysis — malware RE, disassembly, deobfuscation.",
}

async def main_async():
    ensure_structure()

    # Read agent info from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    agent_name = (
        input_data.get("agent_name")
        or input_data.get("agent")
        or input_data.get("name")
        or os.environ.get("CYBERSEC_AGENT_NAME")
        or "unknown"
    )

    session_id = input_data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""

    start_time = datetime.now()

    # === PERMISSION CHECK BEFORE ANY WRITE ===
    allowed, reason, needs_approval = await check_agent_permission(
        agent_name=agent_name,
        action="write",
        path=str(get_project_dir()),
        current_session_id=session_id
    )

    if not allowed:
        print(json.dumps({"status": "error", "message": f"Permission denied for {agent_name}: {reason}"}))
        return

    # --- Write start marker to timeline ---
    await _log_to_timeline(agent_name, start_time, "start")

    # --- Write agent_active marker ---
    await _write_agent_state(agent_name, start_time, session_id)

    # --- Log to project session_changes.log ---
    await _log_to_changelog(agent_name, start_time)

    # --- Build context ---
    profile = AGENT_PROFILES.get(agent_name, f"Custom agent: {agent_name}")
    loop_info = get_event_loop_info()
    recent_summary = await _load_recent_summary()

    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🕵️ **AGENT STARTED: {agent_name}**
⏱️  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
📋 Profile: {profile}
🔄 Event Loop: {loop_info['class']} ({loop_info['performance']} performance)
✅ Permission: {reason}

{recent_summary}

**Agent {agent_name} is now active.** All findings will be attributed to this agent."""
        }
    }

    print(json.dumps(output))

async def _log_to_timeline(agent_name: str, timestamp: datetime, event: str):
    session_dir = get_session_dir()
    if not session_dir:
        return
    timeline_path = session_dir / "timeline.md"
    entry = f"| {timestamp.strftime('%H:%M:%S')} | agent_{event} | **{agent_name}** started | — |\n"
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _append_file, timeline_path, entry)

async def _write_agent_state(agent_name: str, timestamp: datetime, session_id: str) -> None:
    project_dir = get_project_dir()
    state_path = project_dir / ".agent_active.json"
    payload = {
        "agent_name": agent_name,
        "started_at": timestamp.isoformat(),
        "session_id": session_id,
    }
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, state_path.write_text, json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")


async def _log_to_changelog(agent_name: str, timestamp: datetime) -> None:
    project_dir = get_project_dir()
    changelog_path = project_dir / "session_changes.log"
    entry = f"[{timestamp.isoformat(timespec='seconds')}] agent_start: {agent_name}\n"
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _append_file, changelog_path, entry)


async def _load_recent_summary() -> str:
    session_dir = get_session_dir()
    if not session_dir:
        return ""

    summary_path = session_dir / "summary.md"
    if not summary_path.exists():
        return ""

    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(None, summary_path.read_text, "utf-8")
    return content.strip()[:2000]

def _append_file(path: Path, content: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()