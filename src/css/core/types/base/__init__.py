"""Layer 0: Minimal abstract base classes (foundational contracts)."""

from .base_header import BaseHeader
from .messages import (  # Phase 6 P1: msgspec.Struct versions
    ProviderType,
    MessageRole,
    BaseMessage,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ExecutorResult,
    ErrorStrategy,
)
from .base_client import (
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
    # messages (Phase 6 P1: msgspec.Struct)
    "ProviderType",
    "MessageRole",
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    "ErrorStrategy",
    # base_client (abstract base)
    "StreamingHandler",
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
