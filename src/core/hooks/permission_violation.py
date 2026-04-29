#!/usr/bin/env python3
"""
PermissionViolation Hook — fires when an agent attempts an unauthorized action.
Logs, blocks, and alerts.
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin


async def main():
    ensure_structure()
    data = read_stdin()

    agent_name = data.get("agent_name", "unknown")
    action     = data.get("action", "unknown")
    resource   = data.get("resource") or data.get("path", "unknown")
    reason     = data.get("reason", "Unauthorized")

    project_dir = get_project_dir()
    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)

    violation = {
        "ts":         now.isoformat(),
        "agent":      agent_name,
        "action":     action,
        "resource":   resource,
        "reason":     reason,
    }

    # Violations log
    violations_log = project_dir / ".claude" / "hooks" / "violations.jsonl"
    append_file(violations_log, json.dumps(violation) + "\n")

    # Session timeline
    if session_dir:
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | PERMISSION_VIOLATION | {agent_name} | {action} on `{resource}` |\n"
        )

    audit({"event": "PermissionViolation", **violation})

    emit(hook_context(
        f"🚫 **PERMISSION VIOLATION**\n\n"
        f"**Agent:** {agent_name}\n"
        f"**Action:** {action}\n"
        f"**Resource:** `{resource}`\n"
        f"**Reason:** {reason}\n"
        f"**Time:** {now.strftime('%H:%M:%S UTC')}\n\n"
        "**Action blocked and logged to violations.jsonl.**"
    ))


if __name__ == "__main__":
    asyncio.run(main())

