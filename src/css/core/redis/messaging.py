from datetime import UTC, datetime
from typing import Any, Literal

import msgspec


class Message(msgspec.Struct, frozen=True, kw_only=True):
    from_id: str
    to_id: str
    payload: Any
    id: str = ""
    type: str = "task"
    routing_mode: Literal["direct", "shortest_path"] = "shortest_path"
    timestamp: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))

    def to_msgpack(self) -> bytes:
        """Serialize for Redis IPC transport using msgpack."""
        return msgspec.msgpack.encode(msgspec.to_builtins(self))

    @classmethod
    def from_msgpack(cls, raw: bytes) -> "Message":
        """Deserialize msgpack payload from Redis IPC transport."""
        return msgspec.msgpack.Decoder(cls).decode(raw)
