#!/usr/bin/env python3
"""
PostToolUse Hook — runs after every MCP tool call.
Now includes permission check for any write operations.
"""
import asyncio
import json
import sys
from datetime import datetime

from uvloop_integration import run_with_uvloop
from utils import get_project_dir
from db.models.permission_checker import check_agent_permission

async def main_async():
    try:
        tool_result = json.load(sys.stdin)
    except Exception:
        tool_result = {"tool": "unknown"}

    agent_name = tool_result.get("agent_name", "MCP_Tool")

    # Permission check before logging write
    allowed, reason, _ = await check_agent_permission(
        agent_name=agent_name,
        action="write",
        path=str(get_project_dir())
    )

    log_entry = f"[{datetime.now().isoformat()}] Tool used → {tool_result.get('tool', 'unknown')} → Layer sync (permission: {reason})\n"

    log_file = get_project_dir() / "session_changes.log"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _append_file, log_file, log_entry)

    print(json.dumps({
        "status": "success",
        "message": f"Post-tool layer sync executed (permission: {reason})",
        "tool": tool_result.get('tool', 'unknown'),
        "timestamp": datetime.now().isoformat()
    }))

def main():
    run_with_uvloop(main_async())


def _append_file(path, content):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(content)

if __name__ == "__main__":
    main()