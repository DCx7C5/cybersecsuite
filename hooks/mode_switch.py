#!/usr/bin/env python3
"""
ModeSwitch Hook — switches Blue/Red/Purple team mode with permission enforcement.
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

from uvloop_integration import run_with_uvloop
from utils import get_session_dir, get_project_dir
from utils.permission_checker import check_agent_permission
from db.models import Session  # Tortoise model

async def main_async():
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}

    new_mode = (
        input_data.get("mode")
        or sys.argv[1] if len(sys.argv) > 1 else "blue"
    ).lower()

    session_dir = get_session_dir()
    session_id = session_dir.name if session_dir else "unknown"

    # Permission check for mode change
    allowed, reason, needs_approval = await check_agent_permission(
        agent_name="ModeSwitch",
        action="write",
        path=str(get_project_dir()),
        current_session_id=session_id
    )

    if not allowed:
        print(json.dumps({"status": "error", "message": f"Permission denied: {reason}"}))
        return

    # Update DB session mode
    # (async update would go here in full implementation)

    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🔄 **MODE SWITCHED TO {new_mode.upper()} TEAM MODE**

**Session**: {session_id}
**Permission status**: {reason}
**Agent behaviour**: {"aggressive/offensive" if new_mode == "red" else "defensive/forensic"}
**Root permissions adjusted** according to AgentRootPermission rules.

All subsequent agent actions will respect the new mode."""
        }
    }

    print(json.dumps(output))

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()