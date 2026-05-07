"""Tool registry and related classes for the tools module."""

import logging
from typing import Optional, Any

from css.core.tools.base import BaseToolRegistry
from css.core.tools.exceptions import ToolNotFoundError, ToolExecutionError
from css.modules.tools.types import ToolSchema

logger = logging.getLogger(__name__)
class ToolRegistry(BaseToolRegistry):
    """Normalizes provider-specific tool definitions to canonical ToolSchema format."""

    def __init__(self):
        self._tools: dict[str, ToolSchema] = {}
        logger.info("ToolRegistry initialized")

    def register_tool(self, tool_id: str, tool_data: dict[str, Any]) -> None:
        """Register a tool with the registry."""
        try:
            tool_schema = ToolSchema.from_dict(tool_data)
            self._tools[tool_id] = tool_schema
            logger.debug(f"Registered tool: {tool_id}")
        except Exception as e:
            raise ToolExecutionError(f"Failed to register tool {tool_id}: {e}")

    def get_tool(self, tool_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a tool's data by its ID."""
        if tool_id not in self._tools:
            raise ToolNotFoundError(tool_id=tool_id)
        return self._tools[tool_id].to_dict()

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [tool.to_dict() for tool in self._tools.values()]


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
