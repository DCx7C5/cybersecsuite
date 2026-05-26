"""Core access surface for shared tool ORM models."""

from css.modules.tools.models import (
    HybridToolDefinition as _HybridToolDefinition,
    HybridToolDefinitionTag as _HybridToolDefinitionTag,
)

HybridToolDefinition = _HybridToolDefinition
HybridToolDefinitionTag = _HybridToolDefinitionTag
