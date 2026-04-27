#!/usr/bin/env python3
"""
BaselineUpdated Hook — fires when a system baseline is recaptured.
Logs the domain and timestamp to the session baseline history.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_app_home, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin


async def main():
    ensure_structure()
    data = read_stdin()

    domain     = data.get("domain", "unknown")
    agent_name = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))
    scope      = data.get("scope", "full")
    item_count = data.get("item_count")

    project_dir = get_project_dir()
    app_home = get_app_home()
    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)

    record = {
        "ts":         now.isoformat(),
        "domain":     domain,
        "agent":      agent_name,
        "scope":      scope,
        "item_count": item_count,
    }

    # Baseline history log
    baseline_log = app_home / "memory" / "system" / "baseline_history.jsonl"
    baseline_log.parent.mkdir(parents=True, exist_ok=True)
    append_file(baseline_log, json.dumps(record) + "\n")

    if session_dir:
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | baseline_updated | {agent_name} | domain={domain} scope={scope} |\n"
        )

    append_file(
        project_dir / "session_changes.log",
        f"[{now.isoformat(timespec='seconds')}] baseline_updated: domain={domain} scope={scope}\n"
    )

    audit({"event": "BaselineUpdated", "domain": domain, "scope": scope})

    emit(hook_context(
        f"📊 **BASELINE UPDATED — {domain.upper()}**\n\n"
        f"**Domain:** {domain}\n"
        f"**Scope:** {scope}\n"
        f"**Agent:** {agent_name}\n"
        f"**Items:** {item_count if item_count is not None else 'N/A'}\n"
        f"**Time:** {now.strftime('%H:%M:%S UTC')}\n\n"
        "Baseline synced to `~/.cybersecsuite/memory/system/baseline_history.jsonl`."
    ))


if __name__ == "__main__":
    asyncio.run(main())

