"""Read/write manager surface for tools persistence."""

from css.modules.tools.models import HybridToolDefinition


class HybridToolDefinitionManager:
    """Read-side manager for registry bootstrap and lookup."""

    async def all_definitions(self) -> list[HybridToolDefinition]:
        return await HybridToolDefinition.all().order_by("name", "id")

    async def by_name(self, name: str) -> HybridToolDefinition | None:
        return await HybridToolDefinition.get_or_none(name=name)

    async def delete_by_name(self, name: str) -> bool:
        record = await HybridToolDefinition.get_or_none(name=name)
        if record is None:
            return False
        await record.delete()
        return True


hybrid_tool_definition_manager = HybridToolDefinitionManager()
