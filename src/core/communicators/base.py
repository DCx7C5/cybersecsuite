"""BaseCommunicator protocol — interface for entity-to-entity async messaging."""

from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable


@runtime_checkable
class BaseCommunicator(Protocol):
    """Interface for asynchronous inter-entity messaging.

    Communicators wrap a message dispatcher to provide a high-level async interface
    for sending messages between agents, skills, and other domain entities.

    Properties:
        entity_id: Unique identifier of the sending entity (e.g., "agent:analyst")
        dispatcher: Underlying message dispatch infrastructure

    Any implementation must support:
        - async send(to_id, payload, msg_type, routing_mode)
        - async post_message(content, target, msg_type, routing_mode)
        - async subscribe(handler, message_types)
        - async unsubscribe(handler)
    """

    @property
    def entity_id(self) -> str:
        """Canonical identifier of the sending entity."""
        ...

    @property
    def dispatcher(self) -> Any:  # MessageDispatcher
        """Underlying message dispatcher infrastructure."""
        ...

    async def send(
        self,
        to_id: str,
        payload: Any,
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Send a structured message to a specific recipient entity."""
        ...

    async def post_message(
        self,
        content: str,
        target: str = "all",
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Post a plain-text message (broadcast or direct)."""
        ...

    async def subscribe(
        self, handler: Any, message_types: list[str] | None = None
    ) -> None:
        """Subscribe to incoming messages (optionally filtered by type)."""
        ...

    async def unsubscribe(self, handler: Any) -> None:
        """Unsubscribe a handler from incoming messages."""
        ...
