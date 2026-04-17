#!/usr/bin/env python3
import asyncio
import json
from datetime import datetime
from uvloop_integration import run_with_uvloop
from utils.permission_checker import check_agent_permission
from utils import get_session_dir

async def main_async():
    data = json.load(sys.stdin) if sys.stdin else {}
    agent = data.get("agent_name", "unknown")
    command = data.get("command", "unknown")
    uid = data.get("run_as_uid", 1000)

    allowed, reason, _ = await check_agent_permission(agent, "root", command=command)
    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": f"🔑 **ROOT COMMAND EXECUTED** by {agent}\n"
                                f"Command: {command}\n"
                                f"Run-as-UID: {uid}\n"
                                f"Permission: {reason}"
        }
    }))

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()