#!/usr/bin/env python3
"""
RootCommandExecuted Hook — fires when an agent runs a privileged command.
Logs uid, command, and permission reason to audit trail.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin

# Commands that are always high-risk regardless of mode
HIGH_RISK = {"dd", "mkfs", "fdisk", "parted", "cryptsetup", "shred", "wipefs"}


async def main():
    ensure_structure()
    data = read_stdin()

    agent_name = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))
    command    = data.get("command", "unknown")
    run_as_uid = data.get("run_as_uid", os.getuid())
    exit_code  = data.get("exit_code")
    mode       = data.get("mode", "blue")

    project_dir = get_project_dir()
    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)

    # Risk assessment
    cmd_base  = command.split()[0].lstrip("sudo ").split("/")[-1] if command else ""
    high_risk = cmd_base in HIGH_RISK
    risk_level = "CRITICAL" if high_risk else ("HIGH" if run_as_uid == 0 else "MEDIUM")

    record = {
        "ts":         now.isoformat(),
        "agent":      agent_name,
        "command":    command,
        "run_as_uid": run_as_uid,
        "exit_code":  exit_code,
        "risk_level": risk_level,
        "mode":       mode,
    }

    # Root commands log
    root_log = project_dir / ".claude" / "hooks" / "root_commands.jsonl"
    append_file(root_log, json.dumps(record) + "\n")

    if session_dir:
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | root_command | {agent_name} | `{command[:60]}` uid={run_as_uid} |\n"
        )

    audit({"event": "RootCommandExecuted", **record})

    emit(hook_context(
        f"🔑 **ROOT COMMAND EXECUTED — {risk_level}**\n\n"
        f"**Agent:** {agent_name}\n"
        f"**Command:** `{command}`\n"
        f"**UID:** {run_as_uid}\n"
        f"**Exit code:** {exit_code if exit_code is not None else 'N/A'}\n"
        f"**Mode:** {mode.upper()}\n"
        f"**Risk:** {risk_level}\n\n"
        + ("⚠️ **HIGH-RISK command** — verify this was intentional.\n" if high_risk else "")
        + "Logged to `root_commands.jsonl`."
    ))


if __name__ == "__main__":
    asyncio.run(main())

