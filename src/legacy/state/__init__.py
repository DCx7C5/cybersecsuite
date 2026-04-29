"""State management — async-safe, scope-aware registry for settings and app state."""

from .registry import StateRegistry, ScopeLevel, get_state_registry

__all__ = ["StateRegistry", "ScopeLevel", "get_state_registry"]
