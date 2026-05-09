"""Base hook data contract."""

import fnmatch

import msgspec


class BaseHookClass(msgspec.Struct, frozen=True):
    """Canonical hook registration record."""

    pattern: str
    priority: int = 50
    stage: str = "all"
    enabled: bool = True

    def matches(self, event_type: str) -> bool:
        """Return True when this hook pattern matches the event type."""
        return self.enabled and fnmatch.fnmatch(event_type, self.pattern)
