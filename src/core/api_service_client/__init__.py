"""
API Service Client — Base abstraction for all LLM/API service providers.

Core classes are defined in core.types:
- BaseApiServiceClient: Abstract base for all providers
- Message, Tool, ModelMetadata, StreamChunk, LLMResponse: Data models
- ProviderType: Enum of supported providers
- StreamingHandler: Mixin for streaming response parsing

This module re-exports for backward compatibility.
"""

from core.types import (
    BaseApiServiceClient,
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
    "StreamingHandler",
    "Message",
    "MessageRole",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ProviderType",
]
