#!/usr/bin/env python3
"""
InvestigationStart Hook — fires when a full investigation begins.
Sets up investigation directory, scope, and MITRE context.
"""
import asyncio
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_session_dir, audit, append_file, emit, hook_context, read_stdin


async def main():
    ensure_structure()
    data = read_stdin()

    investigation_id = (
        data.get("investigation_id")
        or os.environ.get("CYBERSEC_INVESTIGATION_ID")
        or datetime.now(timezone.utc).strftime("INV-%Y%m%d-%H%M%S")
    )
    target      = data.get("target", socket.gethostname())
    scenario    = data.get("scenario", "General threat hunt")
    agent_name  = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "cybersec-agent"))

    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)

    if session_dir:
        inv_dir = session_dir / investigation_id
        for sub in ["evidence", "threats", "iocs", "artifacts", "timeline", "reports", "phases"]:
            (inv_dir / sub).mkdir(parents=True, exist_ok=True)

        meta = {
            "investigation_id": investigation_id,
            "target":           target,
            "scenario":         scenario,
            "started_by":       agent_name,
            "start_time":       now.isoformat(),
            "status":           "active",
            "phases":           [],
        }
        (inv_dir / "investigation_meta.json").write_text(json.dumps(meta, indent=2))

        # Scope doc
        (inv_dir / "scope.md").write_text(
            f"# Investigation: {investigation_id}\n\n"
            f"**Target:** `{target}`  \n**Scenario:** {scenario}  \n"
            f"**Started:** {now.strftime('%Y-%m-%d %H:%M UTC')}  \n**Agent:** {agent_name}\n\n"
            "## Planned Phases\n- Rapid Recon\n- Deep Scan\n- IOC Correlation\n- Threat Attribution\n"
        )

        # Timeline headers
        timeline = inv_dir / "timeline" / "investigation_timeline.md"
        timeline.write_text(
            f"# Investigation Timeline: {investigation_id}\n\n"
            "| Time | Event | Agent | Details |\n"
            "|------|-------|-------|--------|\n"
            f"| {now.strftime('%H:%M:%S')} | investigation_start | {agent_name} | target={target} |\n"
        )

        # Also append to session timeline
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | investigation_start | **{investigation_id}** | target={target} |\n"
        )

    audit({"event": "InvestigationStart", "investigation_id": investigation_id, "target": target})

    emit(hook_context(
        f"🔬 **INVESTIGATION STARTED: `{investigation_id}`**\n\n"
        f"**Target:** `{target}`\n"
        f"**Scenario:** {scenario}\n"
        f"**Agent:** {agent_name}\n"
        f"**Time:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        "**Directory structure created:**\n"
        "evidence/ threats/ iocs/ artifacts/ timeline/ reports/ phases/\n\n"
        "**Suggested phases:** Rapid Recon → Deep Scan → IOC Correlation → Threat Attribution"
    ))


if __name__ == "__main__":
    asyncio.run(main())

