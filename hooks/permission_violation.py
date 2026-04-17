#!/usr/bin/env python3
import asyncio
import json
from uvloop_integration import run_with_uvloop

async def main_async():
    data = json.load(sys.stdin) if sys.stdin else {}
    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": f"🚫 **PERMISSION VIOLATION** by {data.get('agent_name')}\n"
                                f"Action: {data.get('action')}\n"
                                f"Reason: {data.get('reason')}\n"
                                f"Blocked and logged."
        }
    }))

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()