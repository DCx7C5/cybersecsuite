"""
StateRegistry — async-safe, scope-aware file-backed settings management.

Manages settings across three scope levels:
- GLOBAL: in-code defaults (read-only)
- APP: ~/.cybersecsuite/settings.json (R/W) + ~/.claude/settings.json (read-only)
- PROJECT: ~/.cybersecsuite/data/projects/<id>/settings.json (R/W)

Provides atomic writes, per-scope locking, and scope-chain merging with formal fallthrough semantics.
"""

import asyncio
import json
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Tuple
from logging import getLogger

logger = getLogger(__name__)

# Sentinel value for distinguishing missing keys from explicit None
_UNSET = object()


class ScopeLevel(str, Enum):
    """Scope hierarchy for settings resolution."""
    GLOBAL = "global"
    APP = "app"
    PROJECT = "project"


class StateRegistry:
    """
    Async-safe, file-backed, scope-aware registry over ~/.claude (read-only) + ~/.cybersecsuite (R/W).

    All operations are async to prevent event loop blocking.
    Concurrent access protected by per-scope asyncio.Lock.
    All writes are atomic (temp → fsync → rename).
    """

    def __init__(self, cybersecsuite_home: Optional[Path] = None, claude_home: Optional[Path] = None):
        """
        Initialize StateRegistry.

        Args:
            cybersecsuite_home: Path to ~/.cybersecsuite (defaults to $HOME/.cybersecsuite)
            claude_home: Path to ~/.claude (defaults to $HOME/.claude)
        """
        if cybersecsuite_home is None:
            cybersecsuite_home = Path.home() / ".cybersecsuite"
        if claude_home is None:
            claude_home = Path.home() / ".claude"

        self._cybersecsuite_home = Path(cybersecsuite_home)
        self._claude_home = Path(claude_home)

        # Per-scope locks for concurrent access safety
        self._locks: dict[ScopeLevel, asyncio.Lock] = {
            scope: asyncio.Lock() for scope in ScopeLevel
        }

        # In-memory cache (GLOBAL → APP → PROJECT, per-scope)
        self._cache: dict[ScopeLevel, dict[str, Any]] = {}
        self._loaded: bool = False

    # --- Path resolution ---

    def claude_dir(self) -> Path:
        """Return ~/.claude (read-only)."""
        return self._claude_home

    def cybersecsuite_dir(self) -> Path:
        """Return ~/.cybersecsuite."""
        return self._cybersecsuite_home

    def project_dir(self, project_id: str) -> Path:
        """Return ~/.cybersecsuite/data/projects/<id>."""
        self._validate_path_param(project_id)
        return self._cybersecsuite_home / "data" / "projects" / project_id

    def memory_dir(self, scope: ScopeLevel) -> Path:
        """Return ~/.cybersecsuite/memory/<scope>."""
        if scope == ScopeLevel.GLOBAL:
            return self._cybersecsuite_home / "memory" / "system"
        elif scope == ScopeLevel.PROJECT:
            # Note: PROJECT memory is accessed via get_project_memory with project_id
            return self._cybersecsuite_home / "memory" / "project"
        else:  # APP
            return self._cybersecsuite_home / "memory" / "system"

    # --- Validation ---

    @staticmethod
    def _validate_path_param(param: str) -> None:
        """Validate project_id or memory name — reject .., absolute paths, separators."""
        if not param or "/" in param or "\\" in param or param.startswith("."):
            raise ValueError(f"Invalid path parameter: {param}")
        if ".." in param:
            raise ValueError(f"Path traversal not allowed: {param}")

    # --- Atomic write helper ---

    async def _atomic_write(self, path: Path, data: dict) -> None:
        """Write to path atomically (temp → fsync → rename)."""
        path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            delete=False,
            suffix=".json",
            encoding="utf-8",
        ) as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
            temp_path = f.name

        try:
            os.replace(temp_path, path)
        except Exception:
            Path(temp_path).unlink(missing_ok=True)
            raise

    # --- Load all scopes ---

    async def _load_all_scopes(self) -> None:
        """Load GLOBAL, APP, and PROJECT scopes into memory cache."""
        if self._loaded:
            return

        # GLOBAL scope (in-code defaults)
        self._cache[ScopeLevel.GLOBAL] = self._get_global_defaults()

        # APP scope (claude + cybersecsuite)
        async with self._locks[ScopeLevel.APP]:
            self._cache[ScopeLevel.APP] = await self._load_app_scope()

        # PROJECT scope is loaded per-project on demand (no global cache)
        # self._cache[ScopeLevel.PROJECT] = {}  # Initialize empty

        self._loaded = True

    def _get_global_defaults(self) -> dict[str, Any]:
        """Return GLOBAL scope defaults (in-code)."""
        return {
            "env": {},
            "hooks": {},
            "mcpServers": {},
            "skills": {},
            "enabledPlugins": {},
            "extraKnownMarketplaces": {},
            "effortLevel": "medium",
            "lifecycle": {
                "first_setup_completed": False,
                "first_setup_timestamp": None,
                "initialized_version": None,
            },
        }

    async def _load_app_scope(self) -> dict[str, Any]:
        """Load APP scope: claude (read) + cybersecsuite (read+write), right-most wins."""
        result = self._get_global_defaults().copy()

        # Load ~/.claude/settings.json (read-only, lower priority)
        claude_settings = await self._read_json(self._claude_home / "settings.json")
        if claude_settings:
            result = self._deep_merge(result, claude_settings)

        # Load ~/.cybersecsuite/settings.json (read+write, higher priority)
        cybersecsuite_settings = await self._read_json(
            self._cybersecsuite_home / "settings.json"
        )
        if cybersecsuite_settings:
            result = self._deep_merge(result, cybersecsuite_settings)

        return result

    async def _load_project_scope(self, project_id: str) -> dict[str, Any]:
        """Load PROJECT scope for given project_id."""
        self._validate_path_param(project_id)
        path = self.project_dir(project_id) / "settings.json"
        settings = await self._read_json(path)
        return settings or {}

    # --- JSON I/O ---

    async def _read_json(self, path: Path) -> Optional[dict[str, Any]]:
        """Read JSON file safely (missing files return None, invalid JSON logs warning)."""
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error reading {path}: {e}")
            return None

    # --- Scope merging with formal fallthrough semantics ---

    @staticmethod
    def _deep_merge(base: dict, overlay: dict) -> dict:
        """Deep merge overlay into base (overlay values win)."""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = StateRegistry._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    async def _merge_scopes(
        self,
        key: str,
        project_id: Optional[str] = None,
    ) -> Tuple[Any, ScopeLevel]:
        """
        Merge scopes for a top-level key (PROJECT > APP > GLOBAL).

        Returns (value, winning_scope). Falls through to next scope if key is missing.
        Explicit None values mask (don't cascade).

        Fallthrough rules:
        - If key is missing from a scope, cascade to next broader scope
        - If key is explicitly None, mask (return None without cascading)
        """
        if not self._loaded:
            await self._load_all_scopes()

        # PROJECT scope (if project_id provided)
        if project_id:
            self._validate_path_param(project_id)
            async with self._locks[ScopeLevel.PROJECT]:
                project_data = await self._load_project_scope(project_id)
                if key in project_data:
                    return (project_data[key], ScopeLevel.PROJECT)

        # APP scope
        async with self._locks[ScopeLevel.APP]:
            app_data = self._cache[ScopeLevel.APP]
            if key in app_data:
                return (app_data[key], ScopeLevel.APP)

        # GLOBAL scope (always has defaults)
        async with self._locks[ScopeLevel.GLOBAL]:
            global_data = self._cache[ScopeLevel.GLOBAL]
            if key in global_data:
                return (global_data[key], ScopeLevel.GLOBAL)

        return (None, ScopeLevel.GLOBAL)

    # --- Public API: Scoped key/value (R/W to ~/.cybersecsuite only) ---

    async def get(
        self,
        key: str,
        *,
        scope: Optional[ScopeLevel] = None,
        project_id: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get a top-level key value, optionally scoped.

        If scope is None, resolves via scope chain (PROJECT > APP > GLOBAL).
        If scope is specified, reads only that scope.
        """
        if not self._loaded:
            await self._load_all_scopes()

        if scope is None:
            # Resolve via scope chain
            value, _ = await self._merge_scopes(key, project_id)
            return value if value is not None else default

        if scope == ScopeLevel.PROJECT:
            if not project_id:
                raise ValueError("project_id required for PROJECT scope")
            self._validate_path_param(project_id)
            async with self._locks[ScopeLevel.PROJECT]:
                project_data = await self._load_project_scope(project_id)
                return project_data.get(key, default)

        elif scope == ScopeLevel.APP:
            async with self._locks[ScopeLevel.APP]:
                app_data = self._cache[ScopeLevel.APP]
                return app_data.get(key, default)

        elif scope == ScopeLevel.GLOBAL:
            async with self._locks[ScopeLevel.GLOBAL]:
                global_data = self._cache[ScopeLevel.GLOBAL]
                return global_data.get(key, default)

        return default

    async def set(
        self,
        key: str,
        value: Any,
        *,
        scope: ScopeLevel,
        project_id: Optional[str] = None,
    ) -> None:
        """
        Set a top-level key in the specified scope (writes to ~/.cybersecsuite only).

        Cannot write to GLOBAL or read-only ~/.claude.
        """
        if scope == ScopeLevel.GLOBAL:
            raise ValueError("Cannot write to GLOBAL scope")

        if not self._loaded:
            await self._load_all_scopes()

        if scope == ScopeLevel.PROJECT:
            if not project_id:
                raise ValueError("project_id required for PROJECT scope")
            self._validate_path_param(project_id)
            async with self._locks[ScopeLevel.PROJECT]:
                project_settings_path = self.project_dir(project_id) / "settings.json"
                project_data = await self._read_json(project_settings_path) or {}
                project_data[key] = value
                await self._atomic_write(project_settings_path, project_data)

        elif scope == ScopeLevel.APP:
            async with self._locks[ScopeLevel.APP]:
                app_settings_path = self._cybersecsuite_home / "settings.json"
                app_data = await self._read_json(app_settings_path) or {}
                app_data[key] = value
                await self._atomic_write(app_settings_path, app_data)
                # Update in-memory cache
                self._cache[ScopeLevel.APP][key] = value

    async def delete(
        self,
        key: str,
        *,
        scope: ScopeLevel,
        project_id: Optional[str] = None,
    ) -> None:
        """Delete a top-level key from the specified scope (removes from disk)."""
        if scope == ScopeLevel.GLOBAL:
            raise ValueError("Cannot delete from GLOBAL scope")

        if not self._loaded:
            await self._load_all_scopes()

        if scope == ScopeLevel.PROJECT:
            if not project_id:
                raise ValueError("project_id required for PROJECT scope")
            self._validate_path_param(project_id)
            async with self._locks[ScopeLevel.PROJECT]:
                project_settings_path = self.project_dir(project_id) / "settings.json"
                project_data = await self._read_json(project_settings_path) or {}
                project_data.pop(key, None)
                await self._atomic_write(project_settings_path, project_data)

        elif scope == ScopeLevel.APP:
            async with self._locks[ScopeLevel.APP]:
                app_settings_path = self._cybersecsuite_home / "settings.json"
                app_data = await self._read_json(app_settings_path) or {}
                app_data.pop(key, None)
                await self._atomic_write(app_settings_path, app_data)
                # Update in-memory cache
                self._cache[ScopeLevel.APP].pop(key, None)

    # --- Settings access (direct scope reading) ---

    async def get_claude_settings(self) -> dict[str, Any]:
        """Get ~/.claude/settings.json (read-only)."""
        settings = await self._read_json(self._claude_home / "settings.json")
        return settings or {}

    async def get_app_settings(self) -> dict[str, Any]:
        """Get merged APP settings (claude + cybersecsuite, cybersecsuite wins)."""
        if not self._loaded:
            await self._load_all_scopes()
        async with self._locks[ScopeLevel.APP]:
            return self._cache[ScopeLevel.APP].copy()

    async def save_app_settings(self, data: dict[str, Any]) -> None:
        """Save entire APP settings to ~/.cybersecsuite/settings.json."""
        if not self._loaded:
            await self._load_all_scopes()
        async with self._locks[ScopeLevel.APP]:
            app_settings_path = self._cybersecsuite_home / "settings.json"
            await self._atomic_write(app_settings_path, data)
            # Update in-memory cache
            self._cache[ScopeLevel.APP] = data.copy()

    async def get_project_settings(self, project_id: str) -> dict[str, Any]:
        """Get PROJECT settings (reads from disk each time)."""
        self._validate_path_param(project_id)
        async with self._locks[ScopeLevel.PROJECT]:
            return await self._load_project_scope(project_id)

    async def save_project_settings(self, project_id: str, data: dict[str, Any]) -> None:
        """Save entire PROJECT settings."""
        self._validate_path_param(project_id)
        async with self._locks[ScopeLevel.PROJECT]:
            project_settings_path = self.project_dir(project_id) / "settings.json"
            await self._atomic_write(project_settings_path, data)

    # --- Memory access (app + project scopes) ---

    async def get_app_memory(self, name: str) -> Optional[str]:
        """Get app-level memory file (~/.cybersecsuite/memory/system/<name>)."""
        self._validate_path_param(name)
        memory_path = self.memory_dir(ScopeLevel.APP) / name
        try:
            if memory_path.exists():
                return memory_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Error reading app memory {name}: {e}")
        return None

    async def set_app_memory(self, name: str, content: str) -> None:
        """Set app-level memory file."""
        self._validate_path_param(name)
        memory_path = self.memory_dir(ScopeLevel.APP) / name
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            memory_path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Error writing app memory {name}: {e}")
            raise

    async def get_project_memory(self, project_id: str, name: str) -> Optional[str]:
        """Get project-level memory file."""
        self._validate_path_param(project_id)
        self._validate_path_param(name)
        memory_path = (
            self._cybersecsuite_home / "memory" / "project" / project_id / name
        )
        try:
            if memory_path.exists():
                return memory_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Error reading project memory {project_id}/{name}: {e}")
        return None

    async def set_project_memory(
        self, project_id: str, name: str, content: str
    ) -> None:
        """Set project-level memory file."""
        self._validate_path_param(project_id)
        self._validate_path_param(name)
        memory_path = (
            self._cybersecsuite_home / "memory" / "project" / project_id / name
        )
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            memory_path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Error writing project memory {project_id}/{name}: {e}")
            raise

    # --- Reload ---

    async def reload(self) -> None:
        """Reload all scopes from disk (for externally modified files)."""
        self._loaded = False
        await self._load_all_scopes()


# Global singleton instance
_state_registry: Optional[StateRegistry] = None


async def get_state_registry() -> StateRegistry:
    """Get or initialize the global StateRegistry singleton (async-safe)."""
    global _state_registry
    if _state_registry is None:
        _state_registry = StateRegistry()
        await _state_registry._load_all_scopes()
    return _state_registry
