"""Query types — normalized user-facing execution request.

Query = user-facing execution request (prompt + metadata)
Converted to msgspec.Struct (Phase 6 P1).

Note: Task types are in modules.tasks.types (internal TeamMember assignment).
"""

import msgspec
from datetime import datetime
from typing import Any

from .base_headers import BaseHeader


class QueryHeader(BaseHeader, frozen=True):
    """Metadata header for query execution."""
    mode: str = "blue"
    agent_name: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Set defaults for name and description."""
        if not self.name:
            self.name = "query"
        if not self.description:
            self.description = "Execution request"


class Query(msgspec.Struct, frozen=True):
    """Normalized user-facing query.
    
    Input to QueryExecutor.query() — encapsulates prompt + execution metadata.
    """
    id: str
    prompt: str
    mode: str = "blue"
    agent_name: str = "cybersec-agents"
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for inter-process communication."""
        return msgspec.to_builtin(self)


__all__ = ["QueryHeader", "Query"]
