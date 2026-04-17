#!/usr/bin/env python3
"""
SessionEnd Hook — syncs session findings to project layer and writes a summary artifact.
"""
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_project_dir, get_session_dir, audit, append_file, emit


async def main():
    ensure_structure()
    session_dir = get_session_dir()
    project_dir = get_project_dir()

    if not session_dir:
        emit({"status": "warning", "message": "No active session to end."})
        return

    end_time = datetime.now(timezone.utc)
    session_files = ["findings.md", "iocs.md", "timeline.md", "artifacts.md"]

    # Read session files concurrently
    loop = asyncio.get_running_loop()
    results = await asyncio.gather(*[
        loop.run_in_executor(None, _read_safe, session_dir / f)
        for f in session_files
    ])
    file_data = dict(zip(session_files, results))

    # Write session summary to project layer
    summary_path = project_dir / ".memory" / "project" / "last_session.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_lines = [
        f"# Session Summary — {end_time.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Session: `{session_dir.name}`",
        "",
    ]
    for fname, content in file_data.items():
        if content:
            summary_lines.append(f"## {fname}\n{content[:600]}")
    await loop.run_in_executor(None, summary_path.write_text, "\n".join(summary_lines), "utf-8")

    # Changelog
    changelog = project_dir / "session_changes.log"
    append_file(changelog, f"[{end_time.isoformat(timespec='seconds')}] session_end: {session_dir.name}\n")

    audit({"event": "SessionEnd", "session_id": session_dir.name})

    emit({
        "status": "success",
        "message": f"Session {session_dir.name} ended and synced.",
        "files_synced": [f for f, c in file_data.items() if c],
        "end_time": end_time.isoformat(),
    })


def _read_safe(path: Path) -> str:
    try:
        return path.read_text("utf-8")[:800] if path.exists() else ""
    except Exception:
        return ""


if __name__ == "__main__":
    asyncio.run(main())

