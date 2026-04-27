#!/usr/bin/env python3
"""
AgentStart Hook — fires when any A2A agent begins work in cybersecsuite.
Delegates to agent_hooks.on_agent_start for baseline snapshotting and logging.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_hooks import on_agent_start
from utils import read_stdin


async def main():
    data = read_stdin()
    agent_name = (
        data.get("agent_name")
        or data.get("agent")
        or os.environ.get("CYBERSEC_AGENT_NAME")
        or "unknown"
    )
    session_id = data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""
    target_files = data.get("target_files") or []

    await on_agent_start(agent_name, session_id, target_files)


if __name__ == "__main__":
    asyncio.run(main())

