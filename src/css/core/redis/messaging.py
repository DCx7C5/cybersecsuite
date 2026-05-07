import uuid
from datetime import UTC, datetime
from typing import Any, Literal

import msgspec
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

    def to_msgpack(self) -> bytes:
        """Serialize for Redis IPC transport using msgpack."""
        return msgspec.msgpack.encode(self.model_dump(mode="json"))

    @classmethod
    def from_msgpack(cls, raw: bytes) -> "Message":
        """Deserialize msgpack payload from Redis IPC transport."""
        data = msgspec.msgpack.decode(raw)
        return cls(**data)
