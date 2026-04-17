#!/usr/bin/env python3
"""
FindingConfirmed Hook — records a confirmed security finding with severity and MITRE mapping.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_session_dir, audit, append_file, emit, hook_context, read_stdin, SEVERITY_EMOJI

async def main():
    ensure_structure()
    data = read_stdin()

    finding_id  = data.get("finding_id", f"F-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    title       = data.get("title", "Unnamed finding")
    severity    = data.get("severity", "medium").lower()
    status      = data.get("status", "confirmed")
    mitre       = data.get("mitre", [])
    description = data.get("description", "")
    agent_name  = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))

    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)
    emoji       = SEVERITY_EMOJI.get(severity, "🟡")

    record = {
        "finding_id": finding_id,
        "title":      title,
        "severity":   severity,
        "status":     status,
        "mitre":      mitre,
        "description": description,
        "agent":      agent_name,
        "ts":         now.isoformat(),
    }

    if session_dir:
        # findings.md
        findings_path = session_dir / "findings.md"
        if not findings_path.exists():
            append_file(findings_path, "# Findings\n\n")
        append_file(
            findings_path,
            f"## {finding_id} — {title}\n"
            f"**Severity:** {severity.upper()} | **Status:** {status} | **Agent:** {agent_name}\n"
            f"**MITRE:** {', '.join(mitre) if mitre else 'N/A'}\n"
            f"{description}\n\n"
        )

        # JSON record
        findings_dir = session_dir / "findings"
        findings_dir.mkdir(exist_ok=True)
        (findings_dir / f"{finding_id}.json").write_text(json.dumps(record, indent=2))

        # Timeline
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | finding_confirmed | `{finding_id}` | {severity} — {title[:40]} |\n"
        )

    audit({"event": "FindingConfirmed", "finding_id": finding_id, "severity": severity, "status": status})

    mitre_fmt = ", ".join(mitre) if mitre else "N/A"
    emit(hook_context(
        f"{emoji} **FINDING {status.upper()}: `{finding_id}`**\n\n"
        f"**Title:** {title}\n"
        f"**Severity:** {severity.upper()}\n"
        f"**MITRE:** {mitre_fmt}\n"
        f"**Agent:** {agent_name}\n"
        + (f"\n**Description:** {description}" if description else "")
    ))


if __name__ == "__main__":
    asyncio.run(main())

