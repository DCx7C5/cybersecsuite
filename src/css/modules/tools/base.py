from abc import ABC

from css.core.types.base_registry import BaseRegistry


class BaseToolRegistry(BaseRegistry, ABC):
    """Abstract base class for tool registries."""

    def register_tool(self, tool_id: str, tool_data: dict) -> None:
        """Register a tool with the registry."""
        raise NotImplementedError("Subclasses must implement register_tool method.")

    def get_tool(self, tool_id: str) -> dict:
        """Retrieve a tool's data by its ID."""
        raise NotImplementedError("Subclasses must implement get_tool method.")

    def list_tools(self) -> list[dict]:
        """List all registered tools."""
        raise NotImplementedError("Subclasses must implement list_tools method.")
