"""Plan proposal storage under .css/plan/."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import PlannerSession


class ProposalStore:
    """Persists planning proposals and plan snapshots to disk."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = (base_dir or Path.cwd() / ".css" / "plan").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write(self, plan: PlannerSession) -> Path:
        path = self.base_dir / f"{plan.session_id}.json"
        path.write_text(json.dumps(asdict(plan), default=str, indent=2), encoding="utf-8")
        return path

    def read(self, session_id: str) -> dict:
        path = self.base_dir / f"{session_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))
