"""Base classes for the tools module."""

import logging
from typing import Any

from css.core.tools.base import BaseToolRegistry


class ToolRegistry(BaseToolRegistry):
    """Tool registry implementation for the tools module."""

    def __init__(self):
        self._tools: dict[str, Any] = {}


    def register_tool(self, tool_id: str, tool_data: dict[str, Any]) -> None:
        """Register a tool with the registry."""
        self._tools[tool_id] = tool_data
        logger.debug(f"Registered tool: {tool_id}")

    def get_tool(self, tool_id: str) -> dict[str, Any] | None:
        """Retrieve a tool's data by its ID."""
        return self._tools.get(tool_id)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return list(self._tools.values())


logger = logging.getLogger(__name__)
