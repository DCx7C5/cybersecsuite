"""Tools service layer — persistence and business logic for tool operations."""

from typing import TypedDict

from css.core.logger import getLogger
from css.modules.tools.exceptions import ToolNotFoundError
from css.modules.tools.manager import hybrid_tool_definition_manager
from css.modules.tools.enums import CompositionStrategy
from css.modules.tools.types import HybridToolSchema

logger = getLogger(__name__)


class HybridToolPayload(TypedDict, total=False):
    name: str
    description: str
    component_tools: list[str]
    composition_strategy: str
    fallback_provider: str | None
    requires_coordination: bool
    metadata: dict[str, object]
    enabled: bool
    tags: list[str]


def _registry():
    from css.modules.tools.registry import ToolRegistry

    return ToolRegistry()


def _coerce_schema(schema_payload: HybridToolPayload) -> HybridToolSchema:
    strategy_raw = schema_payload.get("composition_strategy", CompositionStrategy.SEQUENTIAL.value)
    strategy = CompositionStrategy(str(strategy_raw))
    fallback_provider_raw = schema_payload.get("fallback_provider")
    metadata_raw = schema_payload.get("metadata")
    return HybridToolSchema(
        name=str(schema_payload.get("name", "")),
        description=str(schema_payload.get("description", "")),
        component_tools=[str(item) for item in schema_payload.get("component_tools", [])],
        composition_strategy=strategy,
        fallback_provider=str(fallback_provider_raw) if fallback_provider_raw is not None else None,
        requires_coordination=bool(schema_payload.get("requires_coordination", False)),
        metadata=metadata_raw if isinstance(metadata_raw, dict) else {},
        enabled=bool(schema_payload.get("enabled", True)),
        tags=[str(tag) for tag in schema_payload.get("tags", [])],
    )


def list_tools(*, provider: str | None = None, enabled_only: bool = True) -> list[dict[str, object]]:
    """List regular tools as serialized dictionaries."""
    registry = _registry()
    return [tool.to_dict() for tool in registry.list_tools(filter_by_provider=provider, enabled_only=enabled_only)]


def list_hybrid_tools(*, strategy: str | None = None, enabled_only: bool = True) -> list[dict[str, object]]:
    """List hybrid tools as serialized dictionaries."""
    registry = _registry()
    tools = registry.list_hybrid_tools(filter_by_strategy=strategy, enabled_only=enabled_only)
    return [tool.to_dict() for tool in tools]


def get_tool(tool_id: str) -> dict[str, object]:
    """Get one regular tool and serialize it."""
    registry = _registry()
    tool = registry.get_tool(tool_id)
    return tool.to_dict()


def get_hybrid_tool(tool_id: str) -> dict[str, object]:
    """Get one hybrid tool and serialize it."""
    registry = _registry()
    tool = registry.get_hybrid_tool(tool_id)
    return tool.to_dict()


def resolve_tool(tool_id: str) -> dict[str, object]:
    """Resolve either regular or hybrid tool and serialize it."""
    registry = _registry()
    tool = registry.resolve_tool(tool_id)
    return tool.to_dict()


async def save_hybrid_tool(hybrid_schema: HybridToolSchema) -> None:
    """Persist a hybrid tool definition to the database."""
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


async def create_hybrid_tool(schema_payload: HybridToolPayload) -> str:
    """Create/register/persist a hybrid tool from request payload."""
    hybrid_schema = _coerce_schema(schema_payload)
    registry = _registry()
    registry.register_hybrid_tool(hybrid_schema)
    await save_hybrid_tool(hybrid_schema)
    return hybrid_schema.tool_id


async def update_hybrid_tool(tool_id: str, schema_payload: HybridToolPayload) -> str:
    """Update a hybrid tool in registry and persistence."""
    registry = _registry()
    existing = registry.hybrid_tools.get(tool_id)
    if existing is None:
        raise ToolNotFoundError(tool_id=tool_id)

    hybrid_schema = _coerce_schema(schema_payload)
    existing.schema = hybrid_schema
    await save_hybrid_tool(hybrid_schema)
    return tool_id


async def delete_hybrid_tool(tool_id: str) -> bool:
    """Delete a hybrid tool from registry and persistence."""
    registry = _registry()
    existing = registry.hybrid_tools.pop(tool_id, None)
    if existing is None:
        return False
    await hybrid_tool_definition_manager.delete_by_name(existing.schema.name)
    return True
