from typing import cast

import pytest
from tortoise import Tortoise

from css.core.events.event_bus import EventBus, event_bus
from css.core.settings.qol import QoLSettings, QoLToggle
from css.core.base.qol_registry import QoLPresetRegistry
from css.core.base.qol_settings import QoLSettingsManager


@pytest.mark.asyncio
async def test_qol_registry_load_override_and_binding_resolution() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["css.core.db.models.qol"]},
    )
    await Tortoise.generate_schemas()

    manager = QoLSettingsManager()
    user_id = "user-registry"

    await manager.save_settings(
        user_id=user_id,
        scope="preset",
        scope_id="silent",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_MARKDOWN}, scope="preset", preset_name="silent"),
    )
    await manager.save_settings(
        user_id=user_id,
        scope="preset",
        scope_id="ops",
        settings=QoLSettings(enabled_toggles={QoLToggle.REDACT_SECRETS}, scope="preset", preset_name="ops"),
    )

    registry = QoLPresetRegistry(settings_manager=manager)
    presets = await registry.list_all(user_id=user_id)
    assert "silent" in presets
    assert "ops" in presets
    assert presets["silent"].enabled_toggles == {QoLToggle.NO_MARKDOWN}
    assert presets["ops"].enabled_toggles == {QoLToggle.REDACT_SECRETS}

    await registry.bind_agent_preset(user_id=user_id, agent_id="agent-1", preset_name="ops")
    resolved = await registry.resolve_agent_preset(user_id=user_id, agent_id="agent-1")
    assert resolved is not None
    assert resolved.enabled_toggles == {QoLToggle.REDACT_SECRETS}

    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_qol_registry_invalidate_on_event() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["css.core.db.models.qol"]},
    )
    await Tortoise.generate_schemas()

    manager = QoLSettingsManager()
    user_id = "user-event"

    await manager.save_settings(
        user_id=user_id,
        scope="preset",
        scope_id="ops",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="preset", preset_name="ops"),
    )

    registry = QoLPresetRegistry(settings_manager=manager)
    first = await registry.get("ops", user_id=user_id)
    assert first is not None
    assert first.enabled_toggles == {QoLToggle.NO_CHAT}

    await manager.save_settings(
        user_id=user_id,
        scope="preset",
        scope_id="ops",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_MARKDOWN}, scope="preset", preset_name="ops"),
    )
    await cast(EventBus, event_bus).emit("qol.preset_saved", {"user_id": user_id})

    second = await registry.get("ops", user_id=user_id)
    assert second is not None
    assert second.enabled_toggles == {QoLToggle.NO_MARKDOWN}

    await Tortoise.close_connections()
