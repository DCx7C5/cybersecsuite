"""Layer 0: Minimal abstract base classes (foundational contracts)."""

from .base_header import BaseHeader
from .base_client import (
    ProviderType,
    MessageRole,
    BaseMessage,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ExecutorResult,
    ErrorStrategy,
    StreamingHandler,
    BaseApiServiceClient,
)
from .base_context import BaseContext
from .base_protocols import BaseCommunicator
from .base_registry import BaseRegistry
from .base_entity import (
    BaseEntity,
    BaseAgent,
    BaseTool,
    BaseSkill,
    BaseRole,
)


__all__ = [
    # base_header
    "BaseHeader",
    # base_client (enums and types)
    "ProviderType",
    "MessageRole",
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    "ErrorStrategy",
    "StreamingHandler",
    # base_client (abstract base)
    "BaseApiServiceClient",
    # base_context
    "BaseContext",
    # protocols
    "BaseCommunicator",
    # base_registry
    "BaseRegistry",
    # base_entity
    "BaseEntity",
    "BaseAgent",
    "BaseTool",
    "BaseSkill",
    "BaseRole",
]
