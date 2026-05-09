from datetime import UTC, datetime
from typing import Any, Literal

import msgspec


class Message(msgspec.Struct, frozen=True):
    id: str = ""
    from_id: str
    to_id: str
    type: str = "task"
    payload: Any
    routing_mode: Literal["direct", "shortest_path"] = "shortest_path"
    timestamp: datetime = datetime.now(UTC)

    def to_msgpack(self) -> bytes:
        """Serialize for Redis IPC transport using msgpack."""
        return msgspec.msgpack.encode(msgspec.to_builtians(self))

    @classmethod
    def from_msgpack(cls, raw: bytes) -> "Message":
        """Deserialize msgpack payload from Redis IPC transport."""
        return msgspec.msgpack.Decoder(cls).decode(raw)
