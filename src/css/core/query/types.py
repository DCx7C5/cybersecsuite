"""Query types — normalized user-facing execution request.

Query = user-facing execution request (prompt + metadata)
Converted to msgspec.Struct.

Note: Task types are in modules.tasks.types (internal TeamMember assignment).
"""

import msgspec
from datetime import datetime
from typing import Any


class QueryHeader(msgspec.Struct, frozen=True, kw_only=True):
    """Metadata header for query execution.

    ``name`` / ``description`` follow the canonical fields defined on
    ``BaseFrontmatterHeader`` (``base_frontmatter_header.py``).
    """

    name: str = "query"
    description: str = "Execution request"
    mode: str = "blue"
    agent_name: str = ""
    version: str = "1.0"


class Query(msgspec.Struct, frozen=True, kw_only=True):
    """Normalized user-facing query.

    Input to QueryExecutor.query() — encapsulates prompt + execution metadata.
    """

    id: str
    prompt: str
    mode: str = "default"
    agent_name: str = "cybersec-agents"
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for inter-process communication."""
        return msgspec.to_builtins(self)
