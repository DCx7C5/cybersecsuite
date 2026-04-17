#!/usr/bin/env python3
"""
FirstInit Hook — one-time bootstrap.
Now includes permission awareness for DB writes.
"""
import asyncio
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
if str(_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(_PROJECT_DIR))

from uvloop_integration import run_with_uvloop, get_event_loop_info
from utils import ensure_structure, get_system_dir, get_project_dir
from utils.permission_checker import check_agent_permission

# ... (all detection helpers unchanged)

async def main_async():
    # Permission check for init writes
    allowed, reason, _ = await check_agent_permission(
        agent_name="FirstInit",
        action="write",
        path=str(get_project_dir())
    )
    if not allowed:
        print(json.dumps({"status": "error", "message": f"Permission denied during init: {reason}"}))
        return

    # (rest of the original FirstInit logic remains — directory creation, DB init, localhost registration, kernel baseline, marker)

    # ... (full original logic here, with the permission check at the top)

    print(json.dumps(output))  # original output

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()