import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_id: str
    to_id: str
    type: str = "task"
    payload: Any
    routing_mode: Literal["direct", "shortest_path"] = "shortest_path"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))