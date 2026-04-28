"""RedisCommunicator — implements BaseCommunicator protocol for Redis-backed messaging."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .dispatcher import MessageDispatcher
from .messaging import Message

log = logging.getLogger(__name__)


@dataclass
class RedisCommunicator:
    """High-level async messaging interface for a single agent/entity.

    Wraps ``MessageDispatcher`` with a sender identity so callers never
    have to manually construct ``Message`` objects or remember their own ID.

    Implements the BaseCommunicator protocol for inter-entity communication.

    ``entity_id`` is the canonical agent identifier (e.g. ``"research:analyst"``).
    """

    _entity_id: str
    _dispatcher: MessageDispatcher
    _handlers: dict[str, list[Callable]] = field(default_factory=dict)

    @property
    def entity_id(self) -> str:
        """Get the entity ID (as @property for protocol compliance)."""
        return self._entity_id

    @property
    def dispatcher(self) -> MessageDispatcher:
        """Get the message dispatcher (as @property for protocol compliance)."""
        return self._dispatcher

    async def send(
        self,
        to_id: str,
        payload: Any,
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Send a message to a specific agent."""
        msg = Message(
            from_id=self.entity_id,
            to_id=to_id,
            type=msg_type,
            payload=payload,
            routing_mode=routing_mode,
        )
        await self.dispatcher.send(msg)

    async def post_message(
        self,
        content: str,
        target: str = "all",
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Post a plain-text message (broadcast or direct)."""
        if target == "all":
            msg = Message(
                from_id=self.entity_id,
                to_id="",
                type="broadcast",
                payload={"content": content},
            )
            await self.dispatcher.send(msg)
        else:
            await self.send(to_id=target, payload={"content": content}, msg_type=msg_type, routing_mode=routing_mode)

    async def subscribe(
        self, handler: Callable, message_types: list[str] | None = None
    ) -> None:
        """Subscribe to incoming messages (optionally filtered by type).
        
        Args:
            handler: Async callable(message: Message) to invoke on new messages
            message_types: Optional list of msg_type values to filter (None = all)
        """
        if message_types is None:
            message_types = ["*"]

        for msg_type in message_types:
            if msg_type not in self._handlers:
                self._handlers[msg_type] = []
            if handler not in self._handlers[msg_type]:
                self._handlers[msg_type].append(handler)

    async def unsubscribe(self, handler: Callable) -> None:
        """Unsubscribe a handler from incoming messages.
        
        Args:
            handler: Previously registered handler to remove
        """
        for msg_type in list(self._handlers.keys()):
            if handler in self._handlers[msg_type]:
                self._handlers[msg_type].remove(handler)
            if not self._handlers[msg_type]:
                del self._handlers[msg_type]
