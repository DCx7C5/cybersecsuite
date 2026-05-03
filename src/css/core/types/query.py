"""Query and Task types — normalized execution units.

Query = user-facing execution request (prompt + metadata)
Task = internal assignment to TeamMember (query + team/orchestrator context)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .base import BaseHeader


@dataclass
class QueryHeader(BaseHeader):
    """Metadata header for query execution."""
    
    def __init__(
        self,
        name: str = "query",
        description: str = "Execution request",
    ):
        super().__init__(name, description)
        self.mode: str = "blue"
        self.agent_name: str = ""
        self.version: str = "1.0"


@dataclass
class Query:
    """Normalized user-facing query.
    
    Input to QueryExecutor.query() — encapsulates prompt + execution metadata.
    """
    id: str
    prompt: str
    mode: str = "blue"
    agent_name: str = "cybersec-agents"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for inter-process communication."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "mode": self.mode,
            "agent_name": self.agent_name,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Task:
    """Internal task assignment to TeamMember.
    
    Query + team/orchestrator context. Assigned by TeamLeader.
    """
    id: str
    query: Query
    team_id: int
    orchestrator_id: str
    assigned_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "id": self.id,
            "query": self.query.to_dict(),
            "team_id": self.team_id,
            "orchestrator_id": self.orchestrator_id,
            "assigned_at": self.assigned_at.isoformat(),
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


__all__ = ["QueryHeader", "Query", "Task"]
