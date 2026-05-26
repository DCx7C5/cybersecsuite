"""Append-only decision log for planner sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class DecisionLog:
    """Writes planner decisions to JSONL for auditability."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = (base_dir or Path.cwd() / ".css" / "plan").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def append(self, session_id: str, decision: str, metadata: dict | None = None) -> Path:
        path = self.base_dir / f"{session_id}.decisions.jsonl"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "metadata": metadata or {},
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        return path
