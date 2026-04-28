from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

from .dispatcher import MessageDispatcher
from .messaging import Message

log = logging.getLogger(__name__)

# Valid vault memory types
_MEMORY_TYPES = {"factual", "episodic", "procedural", "semantic"}
# Map generic category names to vault types
_CATEGORY_MAP: dict[str, str] = {
    "general": "factual",
    "fact": "factual",
    "event": "episodic",
    "procedure": "procedural",
    "concept": "semantic",
}


def _resolve_memory_type(category: str) -> str:
    if category in _MEMORY_TYPES:
        return category
    return _CATEGORY_MAP.get(category, "factual")


@dataclass
class RedisCommunicator:
    """High-level async messaging interface for a single agent/entity.

    Wraps ``MessageDispatcher`` with a sender identity so callers never
    have to manually construct ``Message`` objects or remember their own ID.

    ``entity_id`` is the canonical agent identifier (e.g. ``"research:analyst"``).
    """

    entity_id: str
    dispatcher: MessageDispatcher

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
        """Post a plain-text message.

        ``target="all"`` broadcasts globally; any other value is treated as
        a recipient ``entity_id`` and routed via ``send()``.
        """
        if target == "all":
            msg = Message(
                from_id=self.entity_id,
                to_id="",
                type="broadcast",
                payload={"content": content},
            )
            await self.dispatcher.broadcast(msg, scope="global")
        else:
            await self.send(to_id=target, payload={"content": content}, msg_type=msg_type, routing_mode=routing_mode)

    async def save_to_memory(self, content: str, category: str = "general") -> None:
        """Persist a memory entry to the vault.

        ``category`` accepts vault types (``factual``, ``episodic``,
        ``procedural``, ``semantic``) as well as common aliases
        (``general`` → ``factual``, ``event`` → ``episodic``, etc.).
        """
        from core.cssmcp.cybersec.ai_memory import memory_add

        mem_type = _resolve_memory_type(category)
        result = await memory_add({"content": content, "type": mem_type, "tags": [self.entity_id]})
        log.debug("save_to_memory [%s]: %s", self.entity_id, result)


@dataclass
class RedisCommunicationGroup:
    """A named group of agents that can be messaged collectively or individually.

    ``members`` stores entity IDs (e.g. ``["research:researcher", "research:analyst"]``).
    ``dispatcher`` is optional — set it before calling any messaging methods.
    """

    name: str
    members: list[str] = field(default_factory=list)
    dispatcher: MessageDispatcher | None = None

    def _require_dispatcher(self) -> MessageDispatcher:
        if self.dispatcher is None:
            raise RuntimeError(f"CommunicationGroup {self.name!r} has no dispatcher set")
        return self.dispatcher

    async def add_member(self, entity_id: str) -> None:
        """Add an agent to the group (idempotent)."""
        if entity_id not in self.members:
            self.members.append(entity_id)
            log.debug("group [%s]: added member %r (%d total)", self.name, entity_id, len(self.members))

    async def remove_member(self, entity_id: str) -> None:
        """Remove an agent from the group (no-op if not present)."""
        try:
            self.members.remove(entity_id)
            log.debug("group [%s]: removed member %r (%d remaining)", self.name, entity_id, len(self.members))
        except ValueError:
            pass

    async def broadcast(
        self,
        payload: Any,
        *,
        from_id: str | None = None,
        msg_type: str = "task",
    ) -> None:
        """Send a message to every member of the group."""
        dispatcher = self._require_dispatcher()
        sender = from_id or self.name
        for member_id in list(self.members):
            msg = Message(
                from_id=sender,
                to_id=member_id,
                type=msg_type,
                payload=payload,
                routing_mode="direct",
            )
            await dispatcher.send(msg)

    async def send_to_member(
        self,
        entity_id: str,
        payload: Any,
        *,
        from_id: str | None = None,
        msg_type: str = "task",
    ) -> None:
        """Send a message to one specific member of the group."""
        if entity_id not in self.members:
            raise ValueError(f"{entity_id!r} is not a member of group {self.name!r}")
        dispatcher = self._require_dispatcher()
        sender = from_id or self.name
        msg = Message(
            from_id=sender,
            to_id=entity_id,
            type=msg_type,
            payload=payload,
            routing_mode="direct",
        )
        await dispatcher.send(msg)

    async def get_members(self) -> list[str]:
        """Return a snapshot of current group members."""
        return list(self.members)
