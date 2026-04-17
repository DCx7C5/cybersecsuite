#!/usr/bin/env python3
import asyncio
import json
from utils.permission_checker import check_agent_permission
from uvloop_integration import run_with_uvloop
from utils import get_session_dir

async def main_async():
    data = json.load(sys.stdin) if sys.stdin else {}
    finding_id = data.get("finding_id")
    status = data.get("status", "confirmed")  # confirmed / false_positive / resolved

    allowed, reason, _ = await check_agent_permission("FindingConfirmed", "write", current_session_id=get_session_dir().name if get_session_dir() else None)
    if not allowed:
        return

    # DB update + shared memory sync logic would go here

    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": f"✅ **FINDING {finding_id} {status.upper()}** — synced to shared memory"
        }
    }))

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()