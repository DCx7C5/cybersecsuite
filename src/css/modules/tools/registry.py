"""Tool registry and persistence bridge for builtin and hybrid tools."""

from typing import override

from css.core.logger import getLogger

from css.core.tools.base import BaseToolRegistry
from css.modules.tools.enums import CompositionStrategy
from css.modules.tools.exceptions import ToolExecutionError, ToolNotFoundError
from css.modules.tools.types import HybridToolSchema, ManagedTool, ToolSchema
from css.modules.tools.builtin_catalog import discover_provider_ids, load_builtin_tool_schemas
from css.modules.tools.manager import hybrid_tool_definition_manager

logger = getLogger(__name__)


class ToolRegistry(BaseToolRegistry):
    """Registry for provider builtin tools and database-backed hybrid tools."""

    def __init__(self) -> None:
        super().__init__()
        self.tools: dict[str, ManagedTool] = {}
        self.hybrid_tools: dict[str, ManagedTool] = {}
        self.providers: set[str] = set()
        self._load_builtin_tools()
        logger.info(
            "ToolRegistry initialized with %d builtin tools from %d providers",
            len(self.tools),
            len(self.providers),
        )

    def _load_builtin_tools(self) -> None:
        builtin_tools_map = load_builtin_tool_schemas()
        discovered_providers = discover_provider_ids()
        for provider in discovered_providers:
            builtin_tools_map.setdefault(provider, [])
        self.providers = set(builtin_tools_map.keys())

        for provider_tools in builtin_tools_map.values():
            for schema in provider_tools:
                self.tools[schema.tool_id] = ManagedTool(schema=schema)

    async def initialize_runtime_state(self) -> None:
        await self._load_hybrid_tools_from_db()

    @override
    def register_tool(self, tool_id: str, tool_data: dict[str, object]) -> None:
        try:
            schema = ToolSchema.from_dict(tool_data)
        except Exception as exc:
            raise ToolExecutionError(message=f"Invalid tool schema for {tool_id}: {exc}") from exc
        self.tools[tool_id] = ManagedTool(schema=schema)

    def register_hybrid_tool(self, hybrid_schema: HybridToolSchema) -> None:
        if hybrid_schema.tool_id in self.hybrid_tools:
            raise ValueError(f"Hybrid tool already exists: {hybrid_schema.tool_id}")

        for component_tool in hybrid_schema.component_tools:
            if component_tool not in self.tools:
                raise ValueError(f"Component tool not found: {component_tool}")

        if hybrid_schema.fallback_provider is not None:
            provider_found = any(
                tool.schema.provider == hybrid_schema.fallback_provider
                for tool in self.tools.values()
            )
            if not provider_found:
                raise ValueError(f"Fallback provider not available: {hybrid_schema.fallback_provider}")

        self.hybrid_tools[hybrid_schema.tool_id] = ManagedTool(schema=hybrid_schema)

    @override
    def get_tool(self, tool_id: str) -> ToolSchema:
        if tool_id not in self.tools:
            raise ToolNotFoundError(tool_id=tool_id)
        schema = self.tools[tool_id].schema
        if isinstance(schema, ToolSchema):
            return schema
        raise ToolExecutionError(message=f"Tool {tool_id} has invalid schema type")

    def get_hybrid_tool(self, tool_id: str) -> HybridToolSchema:
        if tool_id not in self.hybrid_tools:
            raise ToolNotFoundError(tool_id=tool_id)
        schema = self.hybrid_tools[tool_id].schema
        if isinstance(schema, HybridToolSchema):
            return schema
        raise ToolExecutionError(message=f"Hybrid tool {tool_id} has invalid schema type")

    @override
    def list_tools(self, filter_by_provider: str | None = None, enabled_only: bool = True) -> list[ToolSchema]:
        result: list[ToolSchema] = []
        for managed in self.tools.values():
            schema = managed.schema
            if not isinstance(schema, ToolSchema):
                continue
            if filter_by_provider is not None and schema.provider != filter_by_provider:
                continue
            if enabled_only and not schema.enabled:
                continue
            result.append(schema)
        return result

    def get_provider_tools(self, provider: str) -> list[ToolSchema]:
        return self.list_tools(filter_by_provider=provider, enabled_only=False)

    def list_hybrid_tools(
        self,
        filter_by_strategy: str | None = None,
        enabled_only: bool = True,
    ) -> list[HybridToolSchema]:
        result: list[HybridToolSchema] = []
        for managed in self.hybrid_tools.values():
            schema = managed.schema
            if not isinstance(schema, HybridToolSchema):
                continue
            if filter_by_strategy is not None and schema.composition_strategy.value != filter_by_strategy:
                continue
            if enabled_only and not schema.enabled:
                continue
            result.append(schema)
        return result

    def resolve_tool(self, tool_id: str) -> ToolSchema | HybridToolSchema:
        if tool_id in self.tools:
            return self.get_tool(tool_id)
        if tool_id in self.hybrid_tools:
            return self.get_hybrid_tool(tool_id)
        raise ToolNotFoundError(tool_id=tool_id)

    async def save_hybrid_tool(self, hybrid_schema: HybridToolSchema) -> None:
        """Persist a hybrid tool definition for registry-backed workflows."""
        from css.modules.tools.models import HybridToolDefinition

        existing = await hybrid_tool_definition_manager.by_name(hybrid_schema.name)
        if existing is None:
            record = HybridToolDefinition.from_schema(hybrid_schema)
            await record.save()
            return

        existing.description = hybrid_schema.description
        existing.component_tools = hybrid_schema.component_tools
        existing.composition_strategy = hybrid_schema.composition_strategy
        existing.fallback_provider = hybrid_schema.fallback_provider
        existing.requires_coordination = hybrid_schema.requires_coordination
        existing.metadata = hybrid_schema.metadata
        existing.enabled = hybrid_schema.enabled
        await existing.save()

    async def _load_hybrid_tools_from_db(self) -> None:
        persisted = await hybrid_tool_definition_manager.all_definitions()
        for orm_record in persisted:
            schema = orm_record.to_schema()
            if not isinstance(schema.composition_strategy, CompositionStrategy):
                schema = HybridToolSchema(
                    name=schema.name,
                    description=schema.description,
                    component_tools=schema.component_tools,
                    composition_strategy=CompositionStrategy(schema.composition_strategy),
                    fallback_provider=schema.fallback_provider,
                    requires_coordination=schema.requires_coordination,
                    metadata=schema.metadata,
                    enabled=schema.enabled,
                    tags=schema.tags,
                )
            if schema.tool_id in self.hybrid_tools:
                self.hybrid_tools[schema.tool_id].schema = schema
                continue
            try:
                self.register_hybrid_tool(schema)
            except ValueError as exc:
                logger.warning("Skipping hybrid tool %s from DB: %s", schema.tool_id, exc)
