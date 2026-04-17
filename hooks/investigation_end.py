#!/usr/bin/env python3
"""
InvestigationEnd Hook — finalizes investigation, generates summary report.
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

    investigation_id = data.get("investigation_id") or os.environ.get("CYBERSEC_INVESTIGATION_ID", "unknown")
    verdict          = data.get("verdict", "inconclusive")

    session_dir = get_session_dir()
    project_dir = get_project_dir()
    now         = datetime.now(timezone.utc)

    stats = {"findings": 0, "iocs": 0, "artifacts": 0, "threats": 0}

    if session_dir:
        inv_dir = session_dir / investigation_id

        stats["findings"]  = _count(session_dir / "findings.md", r"^## F-")
        stats["iocs"]      = _count(session_dir / "iocs.md", r"^\|")
        stats["artifacts"] = _count(session_dir / "artifacts.md", r"^- ")
        stats["threats"]   = len(list((inv_dir / "threats").glob("*.json"))) if (inv_dir / "threats").exists() else 0

        # Final report
        report = (
            f"# Investigation Report: {investigation_id}\n\n"
            f"**Verdict:** {verdict.upper()}  \n"
            f"**Completed:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"## Summary\n"
            f"| Metric | Count |\n|--------|-------|\n"
            f"| Findings | {stats['findings']} |\n"
            f"| IOCs | {stats['iocs']} |\n"
            f"| Artifacts | {stats['artifacts']} |\n"
            f"| Threats | {stats['threats']} |\n\n"
            "## Next Steps\n- Review all findings\n- Brief stakeholders\n- Implement mitigations\n"
        )
        report_path = inv_dir / "reports" / "final_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)

        # Update meta
        meta_file = inv_dir / "investigation_meta.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            meta.update({"status": "completed", "end_time": now.isoformat(), "verdict": verdict, "stats": stats})
            meta_file.write_text(json.dumps(meta, indent=2))

        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | investigation_end | **{investigation_id}** | verdict={verdict} |\n"
        )

    audit({"event": "InvestigationEnd", "investigation_id": investigation_id, "verdict": verdict, "stats": stats})

    emit(hook_context(
        f"🏁 **INVESTIGATION COMPLETE: `{investigation_id}`**\n\n"
        f"**Verdict:** {verdict.upper()}\n\n"
        f"**Results:**\n"
        f"• Findings: {stats['findings']}\n"
        f"• IOCs: {stats['iocs']}\n"
        f"• Artifacts: {stats['artifacts']}\n"
        f"• Threats: {stats['threats']}\n\n"
        f"Final report: `{investigation_id}/reports/final_report.md`"
    ))


if __name__ == "__main__":
    asyncio.run(main())

