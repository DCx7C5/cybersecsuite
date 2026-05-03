"""Query types — normalized user-facing execution request.

Query = user-facing execution request (prompt + metadata)

Note: Task types are in modules.tasks.types (internal TeamMember assignment).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

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


__all__ = ["QueryHeader", "Query"]
