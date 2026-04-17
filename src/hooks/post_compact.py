#!/usr/bin/env python3
"""
PostCompact Hook — fires after context compaction.
Restores critical session state and logs compaction event.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import get_session_dir, audit


def main():
    session_dir = get_session_dir()
    if not session_dir:
        return

    now = datetime.now(timezone.utc)

    # Read pre-compact checkpoint if it exists
    checkpoint_file = session_dir / "compaction_checkpoint.json"
    pre_state = {}
    if checkpoint_file.exists():
        try:
            pre_state = json.loads(checkpoint_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    audit("post_compact", {
        "timestamp": now.isoformat(),
        "pre_compact_state": pre_state,
    })


if __name__ == "__main__":
    main()
