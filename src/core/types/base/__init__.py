"""Layer 0: Minimal abstract base classes (foundational contracts)."""

from .base_header import BaseHeader
from .base_client import (
    ProviderType,
    MessageRole,
    Message,
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
from .protocols import BaseCommunicator


__all__ = [
    # base_header
    "BaseHeader",
    # base_client (enums and types)
    "ProviderType",
    "MessageRole",
    "Message",
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
]
