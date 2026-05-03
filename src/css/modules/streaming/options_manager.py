"""Runtime options manager for dynamic MCP and agents configuration.

Manages three-layer scopes hierarchy (global/app/project) for runtime options
that control MCP servers, sub-agents, permissions, model selection, and hooks.
"""


import asyncio
from typing import Any, Literal

Scope = Literal["global", "app", "project"]


class RuntimeOptionsManager:
    """Singleton manager for runtime options with scopes hierarchy."""

    _instance: RuntimeOptionsManager | None = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._store: dict[str, dict[int | None, dict[str, Any]]] = {
            "global": {},
            "app": {},
            "project": {},
        }

    @classmethod
    def get_instance(cls) -> RuntimeOptionsManager:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def update(
        self,
        scope: Scope,
        scope_id: int | None,
        **kwargs: Any,
    ) -> None:
        """Update options for a specific scopes layer."""
        async with self._lock:
            if scope not in self._store:
                raise ValueError(f"Invalid scopes: {scope}")
            if scope_id not in self._store[scope]:
                self._store[scope][scope_id] = {}
            self._store[scope][scope_id].update(kwargs)

    async def resolve(self, scope_id: int | None = None) -> dict[str, Any]:
        """Merge options from all layers (global → app → project)."""
        async with self._lock:
            # Start with defaults
            merged = {
                "mcps": {"cybersec": True, "dystopian": True},
                "agents": {"filesystem-analyst": True, "memory-analyst": True},
                "allowed_tools": None,
                "permission_mode": None,
                "model": None,
                "hooks": None,
            }

            # Apply layers in order: global → app → project
            for layer_scope in ["global", "app", "project"]:
                layer_data = self._store[layer_scope]
                # Use None key for global/app, scope_id for project
                key = None if layer_scope != "project" else scope_id
                if key in layer_data:
                    merged.update(layer_data[key])

            return merged

    async def get_snapshot(self) -> dict[str, dict[int | None, dict[str, Any]]]:
        """Get raw snapshot of all scopes layers."""
        async with self._lock:
            return self._store.copy()

    async def reset(self, scope: Scope, scope_id: int | None = None) -> None:
        """Reset a scopes layer to empty."""
        async with self._lock:
            if scope_id in self._store[scope]:
                del self._store[scope][scope_id]


# Global singleton
_manager = RuntimeOptionsManager()


def get_manager() -> RuntimeOptionsManager:
    """Get the global RuntimeOptionsManager instance."""
    return _manager


async def load_from_db() -> None:
    """Load project-scoped options from ScopedEntry table."""
    from db.models import ScopedEntry
    entries = await ScopedEntry.filter(entry_type="sdk_options", is_active=True)
    for entry in entries:
        if entry.project_id:
            _manager._store["project"][entry.project_id] = entry.data


async def save_to_db(scope: str, scope_id: int | None, data: dict) -> None:
    """Save options to ScopedEntry table."""
    from db.models import ScopedEntry
    from tortoise import Tortoise
    await Tortoise.init_connections()
    entry = await ScopedEntry.filter(
        entry_type="sdk_options",
        project_id=scope_id,
        is_active=True,
    ).first()
    if entry:
        await entry.update(data=data)
    else:
        await ScopedEntry.create(
            entry_type="sdk_options",
            project_id=scope_id,
            data=data,
        )
