#!/usr/bin/env python3
"""
AgentEnd Hook — fires when an A2A agent finishes.
Delegates to agent_hooks.on_agent_stop for ruff scoping and dry-run mode.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_hooks import on_agent_stop
from utils import read_stdin


async def main():
    data = read_stdin()
    agent_name = data.get("agent_name") or data.get("agent") or os.environ.get("CYBERSEC_AGENT_NAME") or "unknown"
    session_id = data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""
    target_files = data.get("target_files") or []
    dry_run = data.get("dry_run", True)

    await on_agent_stop(agent_name, session_id, target_files, dry_run)


if __name__ == "__main__":
    asyncio.run(main())

