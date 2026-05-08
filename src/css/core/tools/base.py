"""Core tool registry contracts and singleton access."""

from abc import abstractmethod
from css.core.types.meta import AsyncSafeSingletonMeta


class BaseToolRegistry(metaclass=AsyncSafeSingletonMeta):
    """Abstract contract for tool registries."""

    @abstractmethod
    def register_tool(self, tool_id: str, tool_data: dict[str, object]) -> None:
        """Register a tool definition under `tool_id`."""

    @abstractmethod
    def get_tool(self, tool_id: str) -> object:
        """Return a single tool by identifier."""

    @abstractmethod
    def list_tools(
        self,
        filter_by_provider: str | None = None,
        enabled_only: bool = True,
    ) -> list[object]:
        """List tools, optionally filtered by provider and availability."""


def get_tool_registry() -> BaseToolRegistry:
    """Return shared tool registry instance."""
    from css.modules.tools.registry import ToolRegistry
    return ToolRegistry()
