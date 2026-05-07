"""Tool registry base classes and exceptions — shared across all tool modules."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Any

logger = logging.getLogger(__name__)


class BaseToolRegistry(ABC):
    """Abstract base class for tool registries."""

    @abstractmethod
    def register_tool(self, tool_id: str, tool_data: dict[str, Any]) -> None:
        """Register a tool with the registry."""
        ...

    @abstractmethod
    def get_tool(self, tool_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a tool's data by its ID."""
        ...

    @abstractmethod
    def list_tools(self) -> List[dict[str, Any]]:
        """List all registered tools."""
        ...


def get_tool_registry() -> BaseToolRegistry:
    """Get the global tool registry instance."""
    # To be implemented by specific tool modules
    raise NotImplementedError("Tool registry not initialized")
