#!/usr/bin/env python3
"""
AgentEnd Hook — fires when a cybersec agent finishes work.
Now includes permission check before final writes.
"""
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from uvloop_integration import run_with_uvloop
from utils import get_project_dir, get_session_dir
from db.models.permission_checker import check_agent_permission

async def main_async():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    agent_name = input_data.get("agent_name") or os.environ.get("CYBERSEC_AGENT_NAME") or "unknown"
    session_id = input_data.get("session_id", "")

    # Permission check
    allowed, reason, _ = await check_agent_permission(
        agent_name=agent_name,
        action="write",
        path=str(get_project_dir()),
        current_session_id=session_id
    )
    if not allowed:
        print(json.dumps({"status": "error", "message": f"Permission denied: {reason}"}))
        return

    end_time = datetime.now()
    duration_str = "unknown"  # duration calculation logic remains the same

    stats = await _collect_session_stats()

    await _log_to_timeline(agent_name, end_time, duration_str, stats)
    await _log_to_changelog(agent_name, end_time, duration_str, stats)

    # Clean up state file
    project_dir = get_project_dir()
    state_file = project_dir / ".agent_active.json" if project_dir else None
    if state_file and state_file.exists():
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, state_file.unlink, False)
        except OSError:
            pass

    print(json.dumps({
        "status": "success",
        "agent_name": agent_name,
        "duration": duration_str,
        "end_time": end_time.isoformat(),
        "session_id": session_id,
        "stats": stats,
        "message": f"Agent {agent_name} finished after {duration_str}. {stats.get('findings', 0)} findings, {stats.get('iocs', 0)} IOCs."
    }))


async def _collect_session_stats() -> dict:
    """Count findings and IOCs in the current session directory."""
    session_dir = get_session_dir()
    if not session_dir:
        return {"findings": 0, "iocs": 0}

    loop = asyncio.get_running_loop()

    def _count():
        findings = _count_file_entries(session_dir / "findings.md", "^## F-")
        iocs = _count_file_entries(session_dir / "iocs.md", r"^\|")
        return {"findings": findings, "iocs": iocs}

    return await loop.run_in_executor(None, _count)  # type: ignore[arg-type]


def _count_file_entries(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if re.match(pattern, line))
    except OSError:
        return 0


async def _log_to_timeline(agent_name: str, timestamp: datetime, duration_str: str, stats: dict) -> None:
    session_dir = get_session_dir()
    if not session_dir:
        return
    timeline_path = session_dir / "timeline.md"
    entry = (
        f"| {timestamp.strftime('%H:%M:%S')} | agent_end | **{agent_name}** finished"
        f" — duration: {duration_str},"
        f" findings: {stats.get('findings', 0)},"
        f" IOCs: {stats.get('iocs', 0)} | — |\n"
    )
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _append_file, timeline_path, entry)


async def _log_to_changelog(agent_name: str, timestamp: datetime, duration_str: str, stats: dict) -> None:
    project_dir = get_project_dir()
    if not project_dir:
        return
    changelog_path = project_dir / "session_changes.log"
    entry = (
        f"[{timestamp.isoformat(timespec='seconds')}] agent_end: {agent_name}"
        f" | duration={duration_str}"
        f" | findings={stats.get('findings', 0)}"
        f" | iocs={stats.get('iocs', 0)}\n"
    )
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _append_file, changelog_path, entry)


def _append_file(path: Path, content: str) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(content)


def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()