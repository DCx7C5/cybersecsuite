"""Read/write manager surface for tools persistence."""

import inspect
from collections.abc import Awaitable
from typing import TypeVar, cast

from css.modules.tools import models as tools_models

T = TypeVar("T")


async def _await_if_needed(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value
    return value


class HybridToolDefinitionManager:
    """Read-side manager for registry bootstrap and lookup."""

    async def all_definitions(self) -> list[tools_models.HybridToolDefinition]:
        all_result = await _await_if_needed(tools_models.HybridToolDefinition.all())
        if isinstance(all_result, list):
            return all_result

        ordered_result = all_result.order_by("name", "id")
        resolved = await _await_if_needed(ordered_result)
        if isinstance(resolved, list):
            return resolved
        return cast(list[tools_models.HybridToolDefinition], resolved)

    async def by_name(self, name: str) -> tools_models.HybridToolDefinition | None:
        return await _await_if_needed(tools_models.HybridToolDefinition.get_or_none(name=name))

    async def delete_by_name(self, name: str) -> bool:
        record = await _await_if_needed(tools_models.HybridToolDefinition.get_or_none(name=name))
        if record is None:
            return False
        await _await_if_needed(record.delete())
        return True


hybrid_tool_definition_manager = HybridToolDefinitionManager()
