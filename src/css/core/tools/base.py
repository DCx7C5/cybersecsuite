"""Core tool registry contracts and singleton access."""

from abc import ABC, abstractmethod

from css.core.types.meta import SingletonMetaClass


class BaseToolRegistry(ABC):
    """Abstract contract for tool registries."""

    @abstractmethod
    def register_tool(self, tool_id: str, tool_data: dict[str, object]) -> None:
        """Register a tool definition under *tool_id*."""

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

    async def initialize_runtime_state(self) -> None:
        """Optional async startup hook for registry backends."""


class _ToolRegistryProvider(metaclass=SingletonMetaClass):
    """Singleton provider for the process-wide tool registry instance."""

    def __init__(self) -> None:
        self._registry: BaseToolRegistry | None = None

    def get_registry(self) -> BaseToolRegistry:
        if self._registry is None:
            from css.modules.tools.registry import ToolRegistry

            self._registry = ToolRegistry()
        return self._registry


def get_tool_registry() -> BaseToolRegistry:
    """Return shared tool registry instance."""

    return _ToolRegistryProvider().get_registry()
