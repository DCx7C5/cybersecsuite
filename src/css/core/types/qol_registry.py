"""In-memory QoL preset registry with event-driven invalidation."""

import asyncio
from typing import cast

from css.core.events.event_bus import EventBus, event_bus
from css.core.settings.qol import BUILTIN_PRESETS, QoLSettings
from css.core.types.qol_settings import QoLSettingsManager


class QoLPresetRegistry:
    """Load built-in and user presets with per-agent binding resolution."""

    def __init__(
        self,
        settings_manager: QoLSettingsManager | None = None,
        bus: EventBus | None = None,
    ) -> None:
        self._settings_mgr = settings_manager or QoLSettingsManager()
        self._bus: EventBus = bus if bus is not None else cast(EventBus, event_bus)
        self._user_overrides: dict[str, dict[str, QoLSettings]] = {}
        self._agent_bindings: dict[str, dict[str, str]] = {}
        self._loaded_users: set[str] = set()
        self._lock = asyncio.Lock()
        self._subscribed = False

    def _ensure_subscription(self) -> None:
        if self._subscribed:
            return
        self._bus.register("qol.preset_saved", self._on_preset_saved)
        self._subscribed = True

    async def _on_preset_saved(self, _event_type: str, payload: object) -> None:
        if isinstance(payload, dict):
            user_id_obj = payload.get("user_id")
            if isinstance(user_id_obj, str):
                await self.invalidate(user_id_obj)
                return
        await self.invalidate()

    @staticmethod
    def _normalized_user(user_id: str | None) -> str:
        return user_id or "__global__"

    async def _ensure_loaded(self, user_id: str) -> None:
        if user_id in self._loaded_users:
            return
        await self.reload(user_id)

    async def reload(self, user_id: str | None = None) -> None:
        """Reload persisted user presets and per-agent preset bindings."""
        self._ensure_subscription()
        normalized_user = self._normalized_user(user_id)
        async with self._lock:
            preset_rows = await self._settings_mgr.list_scope_models(
                user_id=normalized_user,
                scope="preset",
            )
            binding_rows = await self._settings_mgr.list_scope_models(
                user_id=normalized_user,
                scope="agent_preset",
            )

            overrides: dict[str, QoLSettings] = {}
            for row in preset_rows:
                preset_key = row.scope_id.strip()
                if not preset_key:
                    continue
                settings = row.to_settings()
                overrides[preset_key] = QoLSettings(
                    enabled_toggles=settings.enabled_toggles,
                    scope="preset",
                    preset_name=preset_key,
                )

            merged = dict(BUILTIN_PRESETS)
            merged.update(overrides)

            bindings: dict[str, str] = {}
            for row in binding_rows:
                agent_id = row.scope_id.strip()
                preset_name = (row.preset_name or "").strip()
                if not agent_id or not preset_name:
                    continue
                if preset_name in merged:
                    bindings[agent_id] = preset_name

            self._user_overrides[normalized_user] = overrides
            self._agent_bindings[normalized_user] = bindings
            self._loaded_users.add(normalized_user)

    async def invalidate(self, user_id: str | None = None) -> None:
        """Invalidate one user cache or the whole registry cache."""
        async with self._lock:
            if user_id is None:
                self._user_overrides.clear()
                self._agent_bindings.clear()
                self._loaded_users.clear()
                return
            normalized_user = self._normalized_user(user_id)
            self._user_overrides.pop(normalized_user, None)
            self._agent_bindings.pop(normalized_user, None)
            self._loaded_users.discard(normalized_user)

    async def list_all(self, user_id: str | None = None) -> dict[str, QoLSettings]:
        """Return built-ins merged with user overrides."""
        normalized_user = self._normalized_user(user_id)
        await self._ensure_loaded(normalized_user)
        merged = dict(BUILTIN_PRESETS)
        merged.update(self._user_overrides.get(normalized_user, {}))
        return merged

    async def get(self, preset_name: str, user_id: str | None = None) -> QoLSettings | None:
        """Get one preset by name from built-ins plus user overrides."""
        all_presets = await self.list_all(user_id=user_id)
        return all_presets.get(preset_name)

    async def bind_agent_preset(
        self,
        *,
        user_id: str | None,
        agent_id: str,
        preset_name: str,
    ) -> None:
        """Bind one agent to one preset name."""
        all_presets = await self.list_all(user_id=user_id)
        if preset_name not in all_presets:
            raise ValueError(f"Unknown preset: {preset_name}")
        normalized_user = self._normalized_user(user_id)
        async with self._lock:
            bindings = self._agent_bindings.setdefault(normalized_user, {})
            bindings[agent_id] = preset_name

    async def resolve_agent_preset(
        self,
        *,
        user_id: str | None,
        agent_id: str,
    ) -> QoLSettings | None:
        """Resolve bound preset settings for an agent, if any."""
        normalized_user = self._normalized_user(user_id)
        await self._ensure_loaded(normalized_user)
        preset_name = self._agent_bindings.get(normalized_user, {}).get(agent_id)
        if preset_name is None:
            return None
        return await self.get(preset_name, user_id=user_id)
