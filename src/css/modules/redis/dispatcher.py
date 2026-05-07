from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable

import redis.asyncio as aioredis

from .messaging import Message

log = logging.getLogger(__name__)


class MessageDispatcher:
    def __init__(
        self,
        redis_client: aioredis.Redis,
        allow_leader_peer: bool = True,
        allow_role_peer: bool = True,
        allow_broadcast: bool = True,
    ) -> None:
        self.redis = redis_client
        self.handlers: dict[str, Callable[[Message], Awaitable[None]]] = {}
        self.team_leaders: dict[str, str] = {}
        self.team_members: dict[str, list[str]] = {}
        self.allow_leader_peer = allow_leader_peer
        self.allow_role_peer = allow_role_peer
        self.allow_broadcast = allow_broadcast

    # ==================== REGISTRATION ====================

    def register(self, agent_id: str, handler: Callable[[Message], Awaitable[None]]) -> None:
        """Register an async handler for a given agents ID."""
        self.handlers[agent_id] = handler

    def set_team(self, team_id: str, leader_id: str, member_ids: list[str]) -> None:
        """Declare a team with its leader and member roster."""
        self.team_leaders[team_id] = leader_id
        self.team_members[team_id] = member_ids

    # ==================== TOGGLES ====================

    def set_leader_peer_communication(self, enabled: bool) -> None:
        self.allow_leader_peer = enabled
        log.info("leader peer-to-peer: %s", "ON" if enabled else "OFF")

    def set_role_peer_communication(self, enabled: bool) -> None:
        self.allow_role_peer = enabled
        log.info("role peer-to-peer: %s", "ON" if enabled else "OFF")

    def set_broadcast_enabled(self, enabled: bool) -> None:
        self.allow_broadcast = enabled
        log.info("broadcast: %s", "ON" if enabled else "OFF")

    # ==================== BROADCAST ====================

    async def broadcast(self, msg: Message, scope: str = "global") -> None:
        """Publish to the global or team channel if broadcast is enabled."""
        if not self.allow_broadcast:
            log.warning("broadcast is currently disabled")
            return

        if scope == "global":
            await self.redis.publish("channel:broadcast", msg.model_dump_json())
        elif scope == "team" and msg.to_id in self.team_leaders:
            await self.redis.publish(f"channel:team:{msg.to_id}", msg.model_dump_json())

    # ==================== SMART ROUTING ====================

    async def send(self, msg: Message) -> None:
        if msg.type == "broadcast":
            await self.broadcast(msg)
            return

        if msg.routing_mode == "direct":
            await self._send_direct(msg)
        else:
            await self._send_shortest_path(msg)

    async def _send_direct(self, msg: Message) -> None:
        channel = f"channel:agents:{msg.to_id}"
        await self.redis.publish(channel, msg.model_dump_json())
        log.debug("dispatched %s → %s on %s", msg.from_id, msg.to_id, channel)
        handler = self.handlers.get(msg.to_id)
        if handler is not None:
            await handler(msg)

    def _get_team_of(self, agent_id: str) -> str | None:
        """Return the team ID that contains *agent_id* (as member or leader)."""
        for team_id, members in self.team_members.items():
            if agent_id in members or self.team_leaders.get(team_id) == agent_id:
                return team_id
        return None

    async def _send_shortest_path(self, msg: Message) -> None:
        from_team = self._get_team_of(msg.from_id)
        to_team = self._get_team_of(msg.to_id)

        if from_team == to_team:
            await self._send_direct(msg)
            return

        # Cross-team: role peer allows direct cross-team delivery
        if self.allow_role_peer:
            await self._send_direct(msg)
            return

        # Leader-to-leader relay
        if self.allow_leader_peer and from_team and to_team:
            leader_from = self.team_leaders.get(from_team)
            leader_to = self.team_leaders.get(to_team)
            if leader_from and leader_to:
                relay = Message(
                    from_id=leader_from,
                    to_id=leader_to,
                    type="relay",
                    payload={"original": msg.model_dump(), "final_to": msg.to_id},
                )
                await self._send_direct(relay)
                return

        # Final fallback: forward to manager
        await self._send_direct(
            Message(
                from_id=msg.from_id,
                to_id="manager",
                type="forward",
                payload=msg.model_dump(),
            )
        )

    # ==================== LISTENER ====================

    async def start_listener(self, entity_id: str) -> None:
        """Subscribe to an entity's channel and dispatch incoming messages.

        Each agents/role should run this in its own task::

            asyncio.create_task(dispatcher.start_listener("agents-1"))

        The loop runs until the connection is closed or the task is cancelled.
        Messages that arrive with no registered handler are logged and skipped.
        """
        handler = self.handlers.get(entity_id)
        if handler is None:
            log.warning("start_listener: no handler registered for %r — messages will be dropped", entity_id)

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"channel:agents:{entity_id}")
        log.info("listener started for %r", entity_id)

        try:
            async for raw in pubsub.listen():
                if raw["type"] != "message":
                    continue
                try:
                    msg = Message(**json.loads(raw["data"]))
                except Exception as exc:
                    log.error("listener [%s]: failed to parse message: %s", entity_id, exc)
                    continue

                current_handler = self.handlers.get(entity_id)
                if current_handler is None:
                    log.debug("listener [%s]: dropped message (no handler)", entity_id)
                    continue

                try:
                    await current_handler(msg)
                except Exception as exc:
                    log.exception("listener [%s]: handler raised: %s", entity_id, exc)
        finally:
            await pubsub.unsubscribe(f"channel:agents:{entity_id}")
            log.info("listener stopped for %r", entity_id)