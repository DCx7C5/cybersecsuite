"""Tool registry that auto-discovers and normalizes tools from all LLM providers.

Scans the 26 API providers (api_services/) for builtin tools and normalizes them
to a canonical ToolSchema format for unified access and discovery.
"""

import logging
import pkgutil
from pathlib import Path
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
        self.hybrid_tools: dict[str, ManagedTool] = {}
        self._load_builtin_tools()
        logger.info(
            "Tool registry initialized with %d tools from %d providers",
            len(self.tools),
            self._provider_count,
        )

    @property
    def _provider_count(self) -> int:
        """Count unique providers in registry."""
        return len(set(tool.schema.provider for tool in self.tools.values()))

    def _load_builtin_tools(self) -> None:
        """Scan all api_services providers and load their builtin tools.
        
        For each provider, extract available tools and normalize to ToolSchema.
        Handles provider-specific tool naming/structure conventions.
        """
        self.tools.clear()
        loaded = 0
        for provider in self._discover_providers():
            for tool_schema in self._builtin_schemas_for_provider(provider):
                self.tools[tool_schema.tool_id] = ManagedTool(schema=tool_schema)
                logger.debug("Registered tool: %s", tool_schema.tool_id)
                loaded += 1
        logger.info("Loaded %d builtin tools from %d providers", loaded, self._provider_count)

    @staticmethod
    def _discover_providers() -> list[str]:
        """Auto-discover provider package names under css.api_services."""
        api_services_dir = Path(__file__).resolve().parents[2] / "api_services"
        providers = [
            svc_name
            for _, svc_name, ispkg in pkgutil.iter_modules([str(api_services_dir)])
            if ispkg
        ]
        return sorted(set(providers))

    @staticmethod
    def _builtin_schemas_for_provider(provider: str) -> list[ToolSchema]:
        """Return normalized builtin tool schemas for one provider."""
        builtin_tools_map: dict[str, list[ToolSchema]] = {
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
        }
        return builtin_tools_map.get(provider, [])

    def register_tool(self, tool_schema: ToolSchema, **kwargs) -> None:
        """Register a new tool in the registry.
        
        Args:
            tool_schema: ToolSchema instance to register
            
        Raises:
            ValueError: If tool already exists
            :param tool_schema:
            :param **kwargs:
        """
        if tool_schema.tool_id in self.tools:
            raise ValueError(f"Tool {tool_schema.tool_id} already registered")
        
        managed_tool = ManagedTool(schema=tool_schema)
        self.tools[tool_schema.tool_id] = managed_tool
        logger.info("Registered tool: %s", tool_schema.tool_id)

    def register_hybrid_tool(self, hybrid_schema) -> None:
        """Register a new hybrid tool in the registry.
        
        Validates that all component tools exist before registration.
        
        Args:
            hybrid_schema: HybridToolSchema instance to register
            
        Raises:
            ValueError: If hybrid tool already exists or component tools missing
        """
        from css.modules.tools.enums import CompositionStrategy
        
        if hybrid_schema.tool_id in self.hybrid_tools:
            raise ValueError(f"Hybrid tool {hybrid_schema.tool_id} already registered")
        
        # Validate composition strategy
        valid_strategies = {s.value for s in CompositionStrategy}
        if hybrid_schema.composition_strategy not in valid_strategies:
            raise ValueError(f"Invalid composition_strategy: {hybrid_schema.composition_strategy}")
        
        # Validate all component tools exist
        for tool_id in hybrid_schema.component_tools:
            if tool_id not in self.tools:
                raise ValueError(f"Component tool not found: {tool_id}")
        
        # Validate fallback provider if specified — use ModelRegistry for
        # filesystem-based provider existence check (works without seeding).
        if hybrid_schema.fallback_provider:
            from css.modules.llm_models.registry import get_model_registry
            model_reg = get_model_registry()
            if not model_reg.is_known_provider(hybrid_schema.fallback_provider):
                raise ValueError(
                    f"Fallback provider not available: {hybrid_schema.fallback_provider}"
                )
        
        managed_tool = ManagedTool(schema=hybrid_schema)
        self.hybrid_tools[hybrid_schema.tool_id] = managed_tool
        logger.info("Registered hybrid tool: %s", hybrid_schema.tool_id)

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

    def get_hybrid_tool(self, tool_id: str):
        """Get a specific hybrid tool by ID.
        
        Args:
            tool_id: Hybrid tool identifier in format "hybrid:name"
            
        Returns:
            HybridToolSchema instance
            
        Raises:
            ToolNotFoundError: If hybrid tool not found
        """
        if tool_id not in self.hybrid_tools:
            raise ToolNotFoundError(f"Hybrid tool not found: {tool_id}")
        
        return self.hybrid_tools[tool_id].schema

    def list_hybrid_tools(self, filter_by_strategy: Optional[str] = None, enabled_only: bool = True) -> list:
        """List all registered hybrid tools.
        
        Args:
            filter_by_strategy: Optional strategy filter (sequential, parallel, etc.)
            enabled_only: If True, only return enabled hybrid tools
            
        Returns:
            List of HybridToolSchema instances
        """
        tools = list(self.hybrid_tools.values())
        
        if filter_by_strategy:
            tools = [t for t in tools if t.schema.composition_strategy == filter_by_strategy]
        
        if enabled_only:
            tools = [t for t in tools if t.schema.enabled]
        
        return [t.schema for t in tools]

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

    def resolve_tool(self, tool_id: str):
        """Smart resolver: returns either ToolSchema or HybridToolSchema.
        
        Checks both regular and hybrid tools to find a tool by ID.
        
        Args:
            tool_id: Tool identifier (format: "provider:name" or "hybrid:name")
            
        Returns:
            ToolSchema or HybridToolSchema instance
            
        Raises:
            ToolNotFoundError: If tool not found in either registry
        """
        if tool_id in self.tools:
            return self.tools[tool_id].schema
        elif tool_id in self.hybrid_tools:
            return self.hybrid_tools[tool_id].schema
        else:
            raise ToolNotFoundError(f"Tool not found: {tool_id} (checked regular and hybrid)")

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
        logger.info("Disabled tool: %s%s", tool_id, f" ({reason})" if reason else "")

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
        logger.info("Enabled tool: %s", tool_id)

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

    async def _load_hybrid_tools_from_db(self) -> None:
        """Load persisted hybrid tools from database on startup (async).
        
        Called during app initialization to restore hybrid tool definitions.
        """
        try:
            from css.modules.tools.models import HybridToolDefinition

            self.hybrid_tools.clear()
            hybrids = await HybridToolDefinition.all()
            for hybrid_orm in hybrids:
                hybrid_schema = hybrid_orm.to_schema()
                try:
                    self.register_hybrid_tool(hybrid_schema)
                except ValueError as e:
                    logger.warning("Failed to load hybrid tool %s: %s", hybrid_orm.name, e)

            logger.info("Loaded %d hybrid tools from database", len(hybrids))
        except Exception as e:
            logger.error("Failed to load hybrid tools from database: %s", e)

    async def save_hybrid_tool(self, hybrid_schema) -> None:
        """Persist hybrid tool to database (async).
        
        Args:
            hybrid_schema: HybridToolSchema instance to persist
        """
        try:
            from css.modules.tools.models import HybridToolDefinition

            hybrid_orm = HybridToolDefinition.from_schema(hybrid_schema)
            await hybrid_orm.save()
            logger.info("Persisted hybrid tool: %s", hybrid_schema.tool_id)
        except Exception as e:
            logger.error("Failed to persist hybrid tool %s: %s", hybrid_schema.name, e)
            raise

    async def initialize_runtime_state(self) -> None:
        """Initialize async runtime state required at ASGI startup."""
        await self._load_hybrid_tools_from_db()

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
        logger.info("Unregistered tool: %s", tool_id)

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
