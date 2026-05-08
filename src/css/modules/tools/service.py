"""Tools service layer — persistence and business logic for tool operations."""

from css.core.logger import getLogger
from css.modules.tools.types import HybridToolSchema

logger = getLogger(__name__)


async def save_hybrid_tool(hybrid_schema: HybridToolSchema) -> None:
    """Persist a hybrid tool definition to the database."""
    from css.modules.tools.models import HybridToolDefinition

    existing = await HybridToolDefinition.get_or_none(name=hybrid_schema.name)
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
