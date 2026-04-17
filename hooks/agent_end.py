#!/usr/bin/env python3
"""
AgentEnd Hook — fires when an A2A agent finishes. Logs stats, cleans state.
"""
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, read_stdin


def _count_entries(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for ln in path.read_text("utf-8").splitlines() if re.match(pattern, ln))
    except Exception:
        return 0


async def collect_stats(session_dir: Path) -> dict:
    loop = asyncio.get_running_loop()
    def _count():
        return {
            "findings": _count_entries(session_dir / "findings.md", r"^## F-"),
            "iocs":     _count_entries(session_dir / "iocs.md", r"^\|"),
            "artifacts": _count_entries(session_dir / "artifacts.md", r"^- "),
        }
    return await loop.run_in_executor(None, _count)


async def main():
    ensure_structure()
    data = read_stdin()

    agent_name = data.get("agent_name") or os.environ.get("CYBERSEC_AGENT_NAME") or "unknown"
    session_id = data.get("session_id", "")

    project_dir = get_project_dir()
    session_dir = get_session_dir()
    end_time    = datetime.now(timezone.utc)

    stats = await collect_stats(session_dir) if session_dir else {"findings": 0, "iocs": 0, "artifacts": 0}
    loop  = asyncio.get_running_loop()

    # Timeline
    if session_dir:
        timeline = session_dir / "timeline.md"
        entry = (
            f"| {end_time.strftime('%H:%M:%S')} | agent_end | **{agent_name}** | "
            f"findings={stats['findings']} iocs={stats['iocs']} artifacts={stats['artifacts']} |\n"
        )
        await loop.run_in_executor(None, append_file, timeline, entry)

    # Changelog
    changelog = project_dir / "session_changes.log"
    await loop.run_in_executor(
        None, append_file, changelog,
        f"[{end_time.isoformat(timespec='seconds')}] agent_end: {agent_name}"
        f" findings={stats['findings']} iocs={stats['iocs']}\n"
    )

    # Clean up state file
    state_file = project_dir / ".agent_active.json"
    if state_file.exists():
        await loop.run_in_executor(None, state_file.unlink)

    audit({"event": "AgentEnd", "agent": agent_name, "stats": stats})

    emit({
        "status":     "success",
        "agent_name": agent_name,
        "end_time":   end_time.isoformat(),
        "session_id": session_id,
        "stats":      stats,
        "message":    f"Agent {agent_name} finished. {stats['findings']} findings, {stats['iocs']} IOCs, {stats['artifacts']} artifacts.",
    })


if __name__ == "__main__":
    asyncio.run(main())

