"""Orchestrator entity."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Orchestrator:
    """Orchestrator entity."""
    orchestrator_id: str
    team_id: int
    status: str
    heartbeat_at: Optional[str] = None
    crashed_at: Optional[str] = None
