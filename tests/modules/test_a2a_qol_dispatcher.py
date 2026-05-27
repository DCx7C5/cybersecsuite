from collections.abc import Mapping
from typing import Any

import pytest

from css.core.redis.messaging import Message
from css.core.settings.qol import QoLSettings, QoLToggle
from css.modules.a2a_internal.dispatcher import QoLA2APublisher, QoLA2ASubscriber


class _DispatcherStub:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    async def send(self, message: Message) -> None:
        self.messages.append(message)


class _RegistryStub:
    def __init__(self) -> None:
        self.invalidations: list[str | None] = []
        self.bindings: list[tuple[str | None, str, str]] = []

    async def invalidate(self, user_id: str | None = None) -> None:
        self.invalidations.append(user_id)

    async def bind_agent_preset(
        self,
        *,
        user_id: str | None,
        agent_id: str,
        preset_name: str,
    ) -> None:
        self.bindings.append((user_id, agent_id, preset_name))


def _payload(message: Message) -> Mapping[str, Any]:
    payload = message.payload
    assert isinstance(payload, Mapping)
    return payload


@pytest.mark.asyncio
async def test_qol_a2a_publisher_emits_typed_messages() -> None:
    dispatcher = _DispatcherStub()
    publisher = QoLA2APublisher(dispatcher=dispatcher, from_id="qol-controller")
    settings = QoLSettings(
        enabled_toggles={QoLToggle.NO_CHAT, QoLToggle.NO_THINKING},
        scope="agent",
        preset_name="silent",
    )

    await publisher.publish_toggle_changed(
        to_id="registry",
        user_id="u1",
        scope="agent",
        scope_id="agent-1",
        settings=settings,
    )
    await publisher.publish_preset_bound(
        to_id="registry",
        user_id="u1",
        agent_id="agent-1",
        preset_name="silent",
    )
    await publisher.publish_settings_sync(
        to_id="registry",
        user_id="u1",
        scope="agent",
        scope_id="agent-1",
        settings=settings,
    )

    assert [msg.type for msg in dispatcher.messages] == [
        "qol.toggle_changed",
        "qol.preset_bound",
        "qol.settings_sync",
    ]
    toggle_payload = _payload(dispatcher.messages[0])
    assert toggle_payload["toggle_count"] == 2
    assert toggle_payload["toggle_names"] == ["no_chat", "no_thinking"]
    sync_payload = _payload(dispatcher.messages[2])
    assert sync_payload["preset_name"] == "silent"


@pytest.mark.asyncio
async def test_qol_a2a_subscriber_routes_payload_handlers() -> None:
    registry = _RegistryStub()
    subscriber = QoLA2ASubscriber(registry=registry)

    await subscriber.handle_message(
        Message(
            from_id="qol-controller",
            to_id="registry",
            type="qol.toggle_changed",
            payload={"user_id": "u1", "scope": "agent", "scope_id": "agent-1"},
            routing_mode="direct",
        )
    )
    await subscriber.handle_message(
        Message(
            from_id="qol-controller",
            to_id="registry",
            type="qol.preset_bound",
            payload={"user_id": "u1", "agent_id": "agent-1", "preset_name": "silent"},
            routing_mode="direct",
        )
    )
    await subscriber.handle_message(
        Message(
            from_id="qol-controller",
            to_id="registry",
            type="qol.settings_sync",
            payload={"user_id": "u1", "scope": "agent", "scope_id": "agent-1"},
            routing_mode="direct",
        )
    )

    assert registry.invalidations == ["u1", "u1"]
    assert registry.bindings == [("u1", "agent-1", "silent")]
