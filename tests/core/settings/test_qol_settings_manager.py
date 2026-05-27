import pytest
from tortoise import Tortoise

from css.core.settings.qol import QoLSettings, QoLToggle
from css.core.types.qol_settings import QoLSettingsManager


@pytest.mark.asyncio
async def test_qol_settings_manager_save_get_and_cascade_resolution() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["css.core.db.models.qol"]},
    )
    await Tortoise.generate_schemas()

    manager = QoLSettingsManager()
    user_id = "user-1"

    await manager.save_settings(
        user_id=user_id,
        scope="global",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="global"),
    )
    await manager.save_settings(
        user_id=user_id,
        scope="project",
        scope_id="proj-1",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_MARKDOWN}, scope="project"),
    )

    project = await manager.cascade_resolve(user_id=user_id, project_id="proj-1")
    assert project.enabled_toggles == {QoLToggle.NO_MARKDOWN}

    global_only = await manager.cascade_resolve(user_id=user_id, project_id="missing")
    assert global_only.enabled_toggles == {QoLToggle.NO_CHAT}

    await manager.save_settings(
        user_id=user_id,
        scope="session",
        scope_id="sess-1",
        settings=QoLSettings(enabled_toggles={QoLToggle.MINIMAL}, scope="session"),
    )
    session = await manager.cascade_resolve(
        user_id=user_id,
        session_id="sess-1",
        project_id="proj-1",
    )
    assert session.enabled_toggles == {QoLToggle.MINIMAL}

    loaded = await manager.get_for_scope(user_id=user_id, scope="session", scope_id="sess-1")
    assert loaded is not None
    assert loaded.enabled_toggles == {QoLToggle.MINIMAL}

    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_qol_settings_manager_safe_toggle_decode_ignores_unknown_values() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["css.core.db.models.qol"]},
    )
    await Tortoise.generate_schemas()

    manager = QoLSettingsManager()
    model = await manager.save_settings(
        user_id="u",
        scope="global",
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="global"),
    )
    model.enabled_toggles = ["no_chat", "unknown_toggle"]
    await model.save(update_fields=["enabled_toggles"])

    loaded = await manager.get_for_scope(user_id="u", scope="global")
    assert loaded is not None
    assert loaded.enabled_toggles == {QoLToggle.NO_CHAT}

    await Tortoise.close_connections()

