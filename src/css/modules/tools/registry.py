"""Tool registry that auto-discovers and normalizes tools from all LLM providers.

Scans the 26 API providers (api_services/) for builtin tools and normalizes them
to a canonical ToolSchema format for unified access and discovery.
"""

import logging
from typing import Optional

from css.modules.tools.base import BaseToolRegistry
from css.modules.tools.types import ToolSchema, ManagedTool, ToolParameter, ToolReturnType
from css.modules.tools.enums import ParameterType
from css.modules.tools.exceptions import ToolNotFoundError

logger = logging.getLogger(__name__)


class ToolRegistry(BaseToolRegistry):
    """Registry for all builtin tools from all LLM providers.
    
    Auto-discovers tools from each provider in api_services/ on startup.
    Normalizes provider-specific tool definitions to canonical ToolSchema format.
    """

    def __init__(self):
        """Initialize registry and load builtin tools from all providers."""
        super().__init__()
        self.tools: dict[str, ManagedTool] = {}
        self._load_builtin_tools()
        logger.info(f"Tool registry initialized with {len(self.tools)} tools from {self._provider_count} providers")

    @property
    def _provider_count(self) -> int:
        """Count unique providers in registry."""
        return len(set(tool.schema.provider for tool in self.tools.values()))

    def _load_builtin_tools(self) -> None:
        """Scan all api_services providers and load their builtin tools.
        
        For each provider, extract available tools and normalize to ToolSchema.
        Handles provider-specific tool naming/structure conventions.
        """
        # Provider-specific tool definitions (hardcoded for now, can be migrated to provider plugins)
        builtin_tools_map = {
            # OpenAI: code_interpreter, file_search, retrieval
            "openai": [
                ToolSchema(
                    provider="openai",
                    name="code_interpreter",
                    description="Execute Python code and get results (in Code Interpreter mode)",
                    parameters=[
                        ToolParameter(
                            name="code",
                            type=ParameterType.STRING,
                            description="Python code to execute",
                            required=True,
                        )
                    ],
                    returns=ToolReturnType(
                        type="object",
                        description="Code execution result with stdout, stderr, and artifacts",
                    ),
                    tags=["code", "execution", "python"],
                    requires_auth=False,
                    timeout_seconds=60,
                ),
                ToolSchema(
                    provider="openai",
                    name="file_search",
                    description="Search through files and retrieve relevant content",
                    parameters=[
                        ToolParameter(
                            name="query",
                            type=ParameterType.STRING,
                            description="Search query",
                            required=True,
                        ),
                    ],
                    returns=ToolReturnType(
                        type="array",
                        description="List of matching files and excerpts",
                    ),
                    tags=["search", "retrieval"],
                    timeout_seconds=30,
                ),
            ],
            # Anthropic: computer_use (vision-based tool use)
            "anthropic": [
                ToolSchema(
                    provider="anthropic",
                    name="computer_use",
                    description="Use computer vision and interaction tools to accomplish tasks",
                    parameters=[
                        ToolParameter(
                            name="action",
                            type=ParameterType.STRING,
                            description="Action to perform (screenshot, click, type, etc.)",
                            required=True,
                            enum=["screenshot", "click", "type", "scroll", "key_press"],
                        ),
                        ToolParameter(
                            name="coordinates",
                            type=ParameterType.ARRAY,
                            description="[x, y] coordinates for mouse actions",
                            required=False,
                        ),
                        ToolParameter(
                            name="text",
                            type=ParameterType.STRING,
                            description="Text to type",
                            required=False,
                        ),
                    ],
                    returns=ToolReturnType(
                        type="object",
                        description="Result of the action (screenshot data, click result, etc.)",
                    ),
                    tags=["computer_vision", "interaction"],
                    requires_auth=False,
                    timeout_seconds=30,
                ),
            ],
            # Groq: OpenAI-compatible (no builtin tools at provider level, uses function calling)
            "groq": [],
            # Ollama: Local model runner (no builtin tools)
            "ollama": [],
            # Google Gemini: function calling support
            "gemini": [],
            # Mistral: function calling support
            "mistral": [],
            # Together: function calling support
            "together": [],
            # All other providers: empty by default (can be extended)
        }

        # Load tools for each provider
        loaded = 0
        for provider, tools in builtin_tools_map.items():
            for tool_schema in tools:
                managed_tool = ManagedTool(schema=tool_schema)
                self.tools[tool_schema.tool_id] = managed_tool
                logger.debug(f"Registered tool: {tool_schema.tool_id}")
                loaded += 1

        logger.info(f"Loaded {loaded} builtin tools from {len(builtin_tools_map)} providers")

    def register_tool(self, tool_schema: ToolSchema) -> None:
        """Register a new tool in the registry.
        
        Args:
            tool_schema: ToolSchema instance to register
            
        Raises:
            ValueError: If tool already exists
        """
        if tool_schema.tool_id in self.tools:
            raise ValueError(f"Tool {tool_schema.tool_id} already registered")
        
        managed_tool = ManagedTool(schema=tool_schema)
        self.tools[tool_schema.tool_id] = managed_tool
        logger.info(f"Registered tool: {tool_schema.tool_id}")

    def get_tool(self, tool_id: str) -> ToolSchema:
        """Get a specific tool by ID.
        
        Args:
            tool_id: Tool identifier in format "provider:name"
            
        Returns:
            ToolSchema instance
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_id}")
        
        return self.tools[tool_id].schema

    def get_provider_tools(self, provider: str) -> list[ToolSchema]:
        """Get all tools available for a specific provider.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            
        Returns:
            List of ToolSchema instances for the provider
        """
        return [
            tool.schema for tool in self.tools.values()
            if tool.schema.provider == provider
        ]

    def list_tools(self, filter_by_provider: Optional[str] = None, enabled_only: bool = True) -> list[ToolSchema]:
        """List all registered tools.
        
        Args:
            filter_by_provider: Optional provider filter
            enabled_only: If True, only return enabled tools
            
        Returns:
            List of ToolSchema instances
        """
        tools = list(self.tools.values())
        
        if filter_by_provider:
            tools = [t for t in tools if t.schema.provider == filter_by_provider]
        
        if enabled_only:
            tools = [t for t in tools if t.schema.enabled]
        
        return [t.schema for t in tools]

    def disable_tool(self, tool_id: str, reason: Optional[str] = None) -> None:
        """Disable a tool (prevent execution but keep registration).
        
        Args:
            tool_id: Tool identifier
            reason: Optional reason for disabling
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_id}")
        
        managed_tool = self.tools[tool_id]
        managed_tool.schema.enabled = False
        managed_tool.disabled_reason = reason
        logger.info(f"Disabled tool: {tool_id}" + (f" ({reason})" if reason else ""))

    def enable_tool(self, tool_id: str) -> None:
        """Re-enable a previously disabled tool.
        
        Args:
            tool_id: Tool identifier
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_id}")
        
        managed_tool = self.tools[tool_id]
        managed_tool.schema.enabled = True
        managed_tool.disabled_reason = None
        logger.info(f"Enabled tool: {tool_id}")

    def get_tool_stats(self, tool_id: str) -> dict:
        """Get execution statistics for a tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Dictionary with call_count, last_called, last_error, etc.
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_id}")
        
        managed_tool = self.tools[tool_id]
        return {
            "tool_id": tool_id,
            "call_count": managed_tool.call_count,
            "last_called": managed_tool.last_called,
            "last_error": managed_tool.last_error,
            "available": managed_tool.is_available,
        }

    # Implement abstract methods from BaseRegistry
    async def register(self, tool_id: str, tool_schema: ToolSchema) -> None:
        """Register a tool (async wrapper for register_tool).
        
        Args:
            tool_id: Tool identifier
            tool_schema: ToolSchema instance
        """
        self.register_tool(tool_schema)

    async def unregister(self, tool_id: str) -> None:
        """Unregister a tool (remove from registry).
        
        Args:
            tool_id: Tool identifier
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_id}")
        del self.tools[tool_id]
        logger.info(f"Unregistered tool: {tool_id}")

    async def get(self, tool_id: str) -> ToolSchema:
        """Get a tool (async wrapper for get_tool).
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            ToolSchema instance
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        return self.get_tool(tool_id)

    async def list_all(self, filter_by_provider: Optional[str] = None) -> list[ToolSchema]:
        """List all tools (async wrapper for list_tools).
        
        Args:
            filter_by_provider: Optional provider filter
            
        Returns:
            List of ToolSchema instances
        """
        return self.list_tools(filter_by_provider=filter_by_provider, enabled_only=False)


# Global registry instance (singleton)
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance.
    
    Returns:
        ToolRegistry singleton
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
