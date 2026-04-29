#!/usr/bin/env python3
"""
PreCompact Hook — fires before context compaction.
Saves critical session state that might be lost during compaction.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import get_session_dir, audit


def main():
    session_dir = get_session_dir()
    if not session_dir:
        return

    now = datetime.now(timezone.utc)
    state = {
        "timestamp": now.isoformat(),
        "event": "pre_compact",
    }

    # Save current findings count
    findings_file = session_dir / "findings.jsonl"
    if findings_file.exists():
        state["findings_count"] = sum(1 for _ in findings_file.open())

    # Save current IOC count
    ioc_file = session_dir / "iocs.jsonl"
    if ioc_file.exists():
        state["ioc_count"] = sum(1 for _ in ioc_file.open())

    # Write compaction checkpoint
    checkpoint_file = session_dir / "compaction_checkpoint.json"
    checkpoint_file.write_text(json.dumps(state, indent=2))

    audit("pre_compact", state)


if __name__ == "__main__":
    main()
