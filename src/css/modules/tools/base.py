"""Base classes for the tools module."""

import logging
from typing import Dict, List, Optional, Any

from css.core.tools.base import BaseToolRegistry


class ToolRegistry(BaseToolRegistry):
    """Tool registry implementation for the tools module."""

    def __init__(self):
        self._tools: Dict[str, Any] = {}
        logger = logging.getLogger(__name__)

    def register_tool(self, tool_id: str, tool_data: Dict[str, Any]) -> None:
        """Register a tool with the registry."""
        self._tools[tool_id] = tool_data
        self.logger.debug(f"Registered tool: {tool_id}")

    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a tool's data by its ID."""
        return self._tools.get(tool_id)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return list(self._tools.values())


logger = logging.getLogger(__name__)
