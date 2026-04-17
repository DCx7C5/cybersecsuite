#!/usr/bin/env python3
"""
PhaseEnd Hook — finalizes a cybersecsuite investigation phase.
Collects artifacts, counts IOCs/findings, updates timeline.
"""
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit, hook_context, read_stdin


def _count(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for ln in path.read_text("utf-8").splitlines() if re.match(pattern, ln))
    except Exception:
        return 0


async def main():
    ensure_structure()
    data = read_stdin()

    phase_name      = data.get("phase_name") or os.environ.get("CYBERSEC_PHASE", "Unknown Phase")
    investigation_id = data.get("investigation_id") or os.environ.get("CYBERSEC_INVESTIGATION_ID", "unknown")

    session_dir = get_session_dir()
    project_dir = get_project_dir()
    now         = datetime.now(timezone.utc)

    stats = {"findings": 0, "iocs": 0, "artifacts": 0, "evidence_files": 0}

    if session_dir:
        phase_dir = session_dir / "phases" / phase_name.lower().replace(" ", "_")

        # Count items
        stats["findings"]      = _count(session_dir / "findings.md", r"^## F-")
        stats["iocs"]          = _count(session_dir / "iocs.md", r"^\|")
        stats["artifacts"]     = _count(session_dir / "artifacts.md", r"^- ")
        stats["evidence_files"] = len(list((phase_dir / "evidence").glob("*"))) if (phase_dir / "evidence").exists() else 0

        # Finalize metadata
        meta_file = phase_dir / "phase_metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            meta.update({"status": "completed", "end_time": now.isoformat(), "stats": stats})
            meta_file.write_text(json.dumps(meta, indent=2))

        # Phase summary report
        report = (
            f"# Phase Report: {phase_name}\n\n"
            f"Investigation: `{investigation_id}`  \nCompleted: {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"## Stats\n"
            f"- Findings: {stats['findings']}\n"
            f"- IOCs: {stats['iocs']}\n"
            f"- Artifacts: {stats['artifacts']}\n"
            f"- Evidence files: {stats['evidence_files']}\n"
        )
        (phase_dir / "reports" / "phase_summary.md").write_text(report)

        # Timeline
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | phase_end | **{phase_name}** | "
            f"findings={stats['findings']} iocs={stats['iocs']} |\n"
        )

        # Changelog
        append_file(
            project_dir / "session_changes.log",
            f"[{now.isoformat(timespec='seconds')}] phase_end: {phase_name}"
            f" findings={stats['findings']} iocs={stats['iocs']}\n"
        )

    audit({"event": "PhaseEnd", "phase": phase_name, "stats": stats})

    emit(hook_context(
        f"✅ **PHASE COMPLETE: {phase_name.upper()}**\n"
        f"Investigation: `{investigation_id}` | {now.strftime('%H:%M UTC')}\n\n"
        f"**Results:**\n"
        f"• Findings: {stats['findings']}\n"
        f"• IOCs: {stats['iocs']}\n"
        f"• Artifacts: {stats['artifacts']}\n"
        f"• Evidence files: {stats['evidence_files']}\n\n"
        f"Phase report written to `phases/{phase_name.lower().replace(' ', '_')}/reports/phase_summary.md`"
    ))


if __name__ == "__main__":
    asyncio.run(main())

