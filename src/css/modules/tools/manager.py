"""Read/write manager surface for tools persistence."""

from css.modules.tools.models import HybridToolDefinition


class HybridToolDefinitionManager:
    """Read-side manager for registry bootstrap and lookup."""

    async def all_definitions(self) -> list[HybridToolDefinition]:
        return await HybridToolDefinition.all().order_by("name", "id")

    async def by_name(self, name: str) -> HybridToolDefinition | None:
        return await HybridToolDefinition.get_or_none(name=name)


hybrid_tool_definition_manager = HybridToolDefinitionManager()

