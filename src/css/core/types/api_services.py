"""Base types and models for API services — LLM providers, messages, tools, streaming.

Includes:
- Base abstractions (BaseApiServiceClient, BaseMessage, Tool, etc.)
- UniversalLLMClient: Registry + lazy-load router for all LLM providers
- SDK registry for custom providers
"""

from .base import (
    BaseApiServiceClient,
    ErrorStrategy,
    ExecutorResult,
    LLMResponse,
    BaseMessage,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
)

from .universal_client import (
    UniversalLLMClient,
    SDKRegistry,
    register_sdk,
    get_sdk,
    clear_sdk_cache,
    list_registered_sdks,
)


__all__ = [
    # Base types
    "BaseApiServiceClient",
    "ErrorStrategy",
    "ExecutorResult",
    "LLMResponse",
    "BaseMessage",
    "MessageRole",
    "ModelMetadata",
    "ProviderType",
    "StreamChunk",
    "StreamingHandler",
    "Tool",
    # Universal client (registry + lazy-load)
    "UniversalLLMClient",
    "SDKRegistry",
    "register_sdk",
    "get_sdk",
    "clear_sdk_cache",
    "list_registered_sdks",
]

