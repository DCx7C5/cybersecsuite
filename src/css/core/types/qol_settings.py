"""QoL settings persistence and resolution manager."""

from css.core.db.models.qol import QoLSettingsModel
from css.core.settings.qol import QoLSettings


class QoLSettingsManager:
    """CRUD and scope-resolution service for QoL settings."""

    async def get_for_scope(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str | None = None,
    ) -> QoLSettings | None:
        record = await QoLSettingsModel.get_or_none(
            user_id=user_id,
            scope=scope,
            scope_id=scope_id or "",
        )
        if record is None:
            return None
        return record.to_settings()

    async def save_settings(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str | None = None,
        settings: QoLSettings,
    ) -> QoLSettingsModel:
        normalized_scope_id = scope_id or ""
        record = await QoLSettingsModel.get_or_none(
            user_id=user_id,
            scope=scope,
            scope_id=normalized_scope_id,
        )
        if record is None:
            record = QoLSettingsModel.from_settings(
                user_id=user_id,
                scope=scope,
                scope_id=normalized_scope_id,
                settings=settings,
            )
            await record.save()
            return record

        record.enabled_toggles = sorted(toggle.value for toggle in settings.enabled_toggles)
        record.preset_name = settings.preset_name
        await record.save(update_fields=["enabled_toggles", "preset_name", "updated_at"])
        return record

    async def cascade_resolve(
        self,
        *,
        user_id: str,
        session_id: str | None = None,
        project_id: str | None = None,
    ) -> QoLSettings:
        if session_id:
            session_settings = await self.get_for_scope(
                user_id=user_id,
                scope="session",
                scope_id=session_id,
            )
            if session_settings is not None:
                return session_settings

        if project_id:
            project_settings = await self.get_for_scope(
                user_id=user_id,
                scope="project",
                scope_id=project_id,
            )
            if project_settings is not None:
                return project_settings

        global_settings = await self.get_for_scope(
            user_id=user_id,
            scope="global",
            scope_id="",
        )
        if global_settings is not None:
            return global_settings
        return QoLSettings(enabled_toggles=set(), scope="session")

    async def list_scope_models(
        self,
        *,
        user_id: str,
        scope: str,
    ) -> list[QoLSettingsModel]:
        """Return persisted QoL rows for one user and scope."""
        return await QoLSettingsModel.filter(user_id=user_id, scope=scope).order_by("scope_id", "id")
