"""Base types and models for API services — LLM providers, messages, tools, streaming.

DEPRECATED: This module is kept for backward compatibility. New code should import from:
- core.types.base.base_client (for BaseApiServiceClient, Message, etc.)
- core.types (for re-exports)
"""

from .base import (
    BaseApiServiceClient,
    ErrorStrategy,
    ExecutorResult,
    LLMResponse,
    Message,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
)


__all__ = [
    "BaseApiServiceClient",
    "ErrorStrategy",
    "ExecutorResult",
    "LLMResponse",
    "Message",
    "MessageRole",
    "ModelMetadata",
    "ProviderType",
    "StreamChunk",
    "StreamingHandler",
    "Tool",
]

