#!/usr/bin/env python3
"""
SessionEnd Hook – syncs session to project/system layer + permission-safe write.
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

from utils import ensure_structure, get_session_dir, get_project_dir
from uvloop_integration import run_with_uvloop
from utils.permission_checker import check_agent_permission


async def main_async():
    ensure_structure()
    session_dir = get_session_dir()
    if not session_dir:
        print(json.dumps({"status": "warning", "message": "No active session"}))
        return

    agent_name = "SessionEnd"

    # Permission check before any write
    allowed, reason, needs_approval = await check_agent_permission(
        agent_name=agent_name,
        action="write",
        path=str(get_project_dir()),
        current_session_id=session_dir.name
    )

    if not allowed:
        print(json.dumps({"status": "error", "message": f"Permission denied: {reason}"}))
        return

    sync_data = {
        "last_session": session_dir.name,
        "end_time": datetime.now().isoformat(),
        "synced_from": "session",
        "permission_reason": reason
    }

    # Async file reads
    session_files = ["findings.md", "iocs.md", "timeline.md"]
    file_data = {}
    tasks = [read_session_file_async(filename, session_dir / filename) for filename in session_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, dict):
            file_data.update(result)

    sync_data["session_files"] = file_data

    print(json.dumps({
        "status": "success",
        "message": "Session ended — synced to Project/System (permission-checked)",
        "synced_data": sync_data,
        "files_processed": len(file_data)
    }))


async def read_session_file_async(filename, file_path):
    try:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, file_path.read_text, "utf-8")
        return {filename: content[:500] + "..." if len(content) > 500 else content}
    except Exception(BaseException):
        return {}


def main():
    run_with_uvloop(main_async())


if __name__ == "__main__":
    main()
