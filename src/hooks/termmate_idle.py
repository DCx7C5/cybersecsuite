#!/usr/bin/env python3
"""
TeammateIdle Hook — fires when a subagent is about to go idle.

Exit code 2 + message on stderr sends feedback and keeps the teammate working.
Exit code 0 allows the agent to go idle normally.
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from uvloop_integration import run_with_uvloop
from _utils import get_project_dir, get_session_dir


# Map agent roles to the artifact patterns they are responsible for
SPECIALIST_DOMAINS: dict[str, list[str]] = {
    "Layer2-Specialist": ["arp", "mac", "vlan", "switch"],
    "Layer3-Specialist": ["ip", "routing", "icmp", "bgp"],
    "Layer4-Specialist": ["tcp", "udp", "port", "syn"],
    "Layer5-Specialist": ["tls", "session", "auth"],
    "Layer6-Specialist": ["encoding", "serialization", "crypto"],
    "Layer7-Specialist": ["http", "dns", "api", "web"],
    "Memory-Analyst": ["memory", "heap", "injection", "ram"],
    "Firmware-Analyst": ["firmware", "uefi", "bios", "flash"],
    "Reverse-Engineer": ["binary", "disassembly", "malware", "yara"],
    "Kernel-Analyst": ["kernel", "module", "rootkit", "ebpf"],
    "Process-Analyst": ["process", "pid", "thread", "service"],
    "Filesystem-Analyst": ["file", "path", "inode", "directory"],
    "Persistence-Analyst": ["persistence", "cron", "registry", "startup"],
    "Steganography-Analyst": ["steganography", "hidden", "lsb", "covert"],
    "Logfile-Analyst": ["log", "syslog", "event", "audit"],
    "Settings-Analyst": ["config", "settings", "env", "registry"],
    "AudioVideo-Analyst": ["audio", "video", "media", "codec"],
}


async def main_async() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError, ValueError, EOFError):
        input_data = {}

    agent_name: str = (
        input_data.get("agent_name")
        or input_data.get("agent")
        or os.environ.get("CYBERSEC_AGENT_NAME")
        or "unknown"
    )
    session_id: str = input_data.get("session_id", "")
    idle_reason: str = input_data.get("reason", "done")

    session_dir = get_session_dir()

    # --- 1. Collect open action items from session artefacts ---
    pending_items = await _collect_pending_items(session_dir, agent_name)

    # --- 2. Decide whether the agent should stay active ---
    blocking_feedback: list[str] = []

    if pending_items["unresolved_iocs"] > 0:
        blocking_feedback.append(
            f"⚠️  {pending_items['unresolved_iocs']} unresolved IOC(s) still require "
            f"classification — do not go idle until each entry has a confidence score "
            f"and MITRE ATT&CK tag."
        )

    if pending_items["open_findings"] > 0:
        blocking_feedback.append(
            f"⚠️  {pending_items['open_findings']} finding(s) are marked OPEN — "
            f"confirm or dismiss every finding before finishing."
        )

    if pending_items["domain_keywords"] and agent_name in SPECIALIST_DOMAINS:
        blocking_feedback.append(
            f"⚠️  Unreviewed artefacts contain {agent_name} domain keywords "
            f"({', '.join(pending_items['domain_keywords'])}) — finish specialist "
            f"analysis before handing back to HUNTER."
        )

    # --- 3. Log the idle event regardless ---
    await _log_idle_event(agent_name, session_id, idle_reason, blocking_feedback, session_dir)

    if blocking_feedback:
        # Exit 2 → Claude keeps the agent working and delivers the feedback
        feedback = (
            f"🛑 **{agent_name} idle blocked** — incomplete work detected:\n\n"
            + "\n".join(blocking_feedback)
            + "\n\nResolve all items above, then you may mark yourself done."
        )
        print(feedback, file=sys.stderr)
        sys.exit(2)

    # Exit 0 → agent may go idle
    print(
        json.dumps(
            {
                "status": "idle_allowed",
                "agent_name": agent_name,
                "reason": idle_reason,
                "timestamp": datetime.now().isoformat(),
                "message": f"Agent {agent_name} cleared to go idle — no outstanding items found.",
            }
        )
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _collect_pending_items(session_dir: Path | None, agent_name: str) -> dict:
    result = {
        "unresolved_iocs": 0,
        "open_findings": 0,
        "domain_keywords": [],
    }

    if not session_dir or not session_dir.exists():
        return result

    loop = asyncio.get_running_loop()

    def _scan() -> dict:
        out = dict(result)

        # Count IOC rows that lack a confidence score
        iocs_path = session_dir / "iocs.md"
        if iocs_path.exists():
            for line in iocs_path.read_text(encoding="utf-8").splitlines():
                if re.match(r"^\|", line) and "---" not in line:
                    cols = [c.strip() for c in line.split("|")]
                    # Expect: | type | value | confidence | tag | source |
                    if len(cols) >= 4 and not re.search(r"\d", cols[3] if len(cols) > 3 else ""):
                        out["unresolved_iocs"] += 1

        # Count findings still marked [OPEN]
        findings_path = session_dir / "findings.md"
        if findings_path.exists():
            text = findings_path.read_text(encoding="utf-8")
            out["open_findings"] = len(re.findall(r"\[OPEN]", text, re.IGNORECASE))

        # Check artifacts dir for domain-relevant but unreviewed files
        artefacts_dir = session_dir / "artefacts"
        if artefacts_dir.exists() and agent_name in SPECIALIST_DOMAINS:
            keywords = SPECIALIST_DOMAINS[agent_name]
            found_kw: set[str] = set()
            for f in artefacts_dir.rglob("*"):
                if f.is_file():
                    name_lower = f.name.lower()
                    for kw in keywords:
                        if kw in name_lower:
                            found_kw.add(kw)
            out["domain_keywords"] = sorted(found_kw)

        return out

    return await loop.run_in_executor(None, _scan)  # type: ignore[arg-type]


async def _log_idle_event(
    agent_name: str,
    session_id: str,
    reason: str,
    blocking: list[str],
    session_dir: Path | None,
) -> None:
    project_dir = get_project_dir()
    if not project_dir:
        return

    loop = asyncio.get_running_loop()
    timestamp = datetime.now()
    status = "BLOCKED" if blocking else "ALLOWED"

    entry = (
        f"[{timestamp.isoformat(timespec='seconds')}] teammate_idle: {agent_name}"
        f" | status={status} | reason={reason}"
        f" | blocking_items={len(blocking)}\n"
    )
    changelog = project_dir / "session_changes.log"
    await loop.run_in_executor(None, _append_file, changelog, entry)

    if session_dir:
        timeline = session_dir / "timeline.md"
        icon = "⛔" if blocking else "💤"
        tl_entry = (
            f"| {timestamp.strftime('%H:%M:%S')} | teammate_idle | "
            f"{icon} **{agent_name}** idle {status.lower()} "
            f"(reason: {reason}) | session_id={session_id} |\n"
        )
        await loop.run_in_executor(None, _append_file, timeline, tl_entry)


def _append_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(content)


def main() -> None:
    run_with_uvloop(main_async())


if __name__ == "__main__":
    main()
