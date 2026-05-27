"""Internal A2A dispatcher surface with QoL transport publisher/subscriber."""

from collections.abc import Mapping
from typing import Protocol

import msgspec

from css.core.redis import dispatcher as redis_dispatcher
from css.core.redis.messaging import Message
from css.core.settings.qol import QoLSettings

MessageDispatcher = redis_dispatcher.MessageDispatcher


class SupportsQoLPresetRegistry(Protocol):
    async def invalidate(self, user_id: str | None = None) -> None:
        ...

    async def bind_agent_preset(
        self,
        *,
        user_id: str | None,
        agent_id: str,
        preset_name: str,
    ) -> None:
        ...


class SupportsMessageDispatch(Protocol):
    async def send(self, message: Message) -> None:
        ...


class QoLToggleChanged(msgspec.Struct, frozen=True, kw_only=True):
    user_id: str
    scope: str
    scope_id: str
    toggle_names: list[str]
    toggle_count: int


class QoLPresetBound(msgspec.Struct, frozen=True, kw_only=True):
    user_id: str
    agent_id: str
    preset_name: str


class QoLSettingsSync(msgspec.Struct, frozen=True, kw_only=True):
    user_id: str
    scope: str
    scope_id: str
    preset_name: str | None = None
    toggle_names: list[str] = msgspec.field(default_factory=list)


class QoLA2APublisher:
    """Publish QoL change events over the internal A2A dispatcher transport."""

    def __init__(self, dispatcher: SupportsMessageDispatch, from_id: str) -> None:
        self._dispatcher = dispatcher
        self._from_id = from_id

    async def publish_toggle_changed(
        self,
        *,
        to_id: str,
        user_id: str,
        scope: str,
        scope_id: str,
        settings: QoLSettings,
    ) -> None:
        toggle_names = sorted(toggle.value for toggle in settings.enabled_toggles)
        payload = QoLToggleChanged(
            user_id=user_id,
            scope=scope,
            scope_id=scope_id,
            toggle_names=toggle_names,
            toggle_count=len(toggle_names),
        )
        await self._dispatcher.send(
            Message(
                from_id=self._from_id,
                to_id=to_id,
                type="qol.toggle_changed",
                payload=msgspec.to_builtins(payload),
                routing_mode="direct",
            )
        )

    async def publish_preset_bound(
        self,
        *,
        to_id: str,
        user_id: str,
        agent_id: str,
        preset_name: str,
    ) -> None:
        payload = QoLPresetBound(user_id=user_id, agent_id=agent_id, preset_name=preset_name)
        await self._dispatcher.send(
            Message(
                from_id=self._from_id,
                to_id=to_id,
                type="qol.preset_bound",
                payload=msgspec.to_builtins(payload),
                routing_mode="direct",
            )
        )

    async def publish_settings_sync(
        self,
        *,
        to_id: str,
        user_id: str,
        scope: str,
        scope_id: str,
        settings: QoLSettings,
    ) -> None:
        payload = QoLSettingsSync(
            user_id=user_id,
            scope=scope,
            scope_id=scope_id,
            preset_name=settings.preset_name,
            toggle_names=sorted(toggle.value for toggle in settings.enabled_toggles),
        )
        await self._dispatcher.send(
            Message(
                from_id=self._from_id,
                to_id=to_id,
                type="qol.settings_sync",
                payload=msgspec.to_builtins(payload),
                routing_mode="direct",
            )
        )


class QoLA2ASubscriber:
    """Apply QoL transport messages to local preset-registry cache state."""

    def __init__(self, registry: SupportsQoLPresetRegistry) -> None:
        self._registry = registry

    async def handle_toggle_changed(self, payload: Mapping[str, object]) -> None:
        user_id = payload.get("user_id")
        await self._registry.invalidate(user_id if isinstance(user_id, str) else None)

    async def handle_preset_bound(self, payload: Mapping[str, object]) -> None:
        user_id = payload.get("user_id")
        agent_id = payload.get("agent_id")
        preset_name = payload.get("preset_name")
        if not (isinstance(user_id, str) and isinstance(agent_id, str) and isinstance(preset_name, str)):
            await self._registry.invalidate(user_id if isinstance(user_id, str) else None)
            return
        await self._registry.bind_agent_preset(
            user_id=user_id,
            agent_id=agent_id,
            preset_name=preset_name,
        )

    async def handle_settings_sync(self, payload: Mapping[str, object]) -> None:
        user_id = payload.get("user_id")
        await self._registry.invalidate(user_id if isinstance(user_id, str) else None)

    async def handle_message(self, message: Message) -> None:
        payload = message.payload if isinstance(message.payload, Mapping) else {}
        if message.type == "qol.toggle_changed":
            await self.handle_toggle_changed(payload)
            return
        if message.type == "qol.preset_bound":
            await self.handle_preset_bound(payload)
            return
        if message.type == "qol.settings_sync":
            await self.handle_settings_sync(payload)
