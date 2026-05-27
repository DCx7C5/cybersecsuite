"""Concrete message and API value objects — msgspec.Struct."""

from collections.abc import AsyncIterator
from typing import Any

import msgspec

from css.core.types.base_enums import MemorySupportMode, ProviderType


class Tool(msgspec.Struct, frozen=True, kw_only=True):
    """A tool available to the model."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = msgspec.field(default_factory=dict)
    return_schema: dict[str, Any] | None = None


class ModelMetadata(msgspec.Struct, frozen=True, kw_only=True):
    """Metadata about a model with per-model feature flags."""

    id: str
    provider: ProviderType
    display_name: str = ""
    context_window: int = 4096
    max_output_tokens: int = 4096
    streaming: bool = True
    vision: bool = False
    tool_use: bool = False
    prompt_caching: bool = False
    batch_api: bool = False
    structured_output: bool = False
    extended_thinking: bool = False
    files_api: bool = False
    tool_use_caching: bool = False
    memory_support_mode: MemorySupportMode = MemorySupportMode.PLATFORM_EMULATED
    input_cost_per_mtok: float = 0.0
    output_cost_per_mtok: float = 0.0


class StreamChunk(msgspec.Struct, frozen=True, kw_only=True):
    """A chunk from a streaming response."""

    type: str = "content_block_delta"
    content: str | None = None
    stop_reason: str | None = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)


class LLMResponse(msgspec.Struct, frozen=True, kw_only=True):
    """A complete LLM response (buffered)."""

    text: str = ""
    stop_reason: str = "stop"
    usage: dict[str, Any] = msgspec.field(default_factory=dict)


class ExecutorResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result from an execution/api call to a provider."""

    status_code: int = 200
    headers: dict[str, str] = msgspec.field(default_factory=dict)
    body: dict[str, Any] | None = None
    stream: AsyncIterator[bytes] | None = None
    error: str | None = None
    latency_ms: float = 0.0
    provider_id: str = ""
    model_id: str = ""
    request_id: str | None = None

    @property
    def ok(self) -> bool:
        """Check if status code is successful (2xx range)."""
        return 200 <= self.status_code < 300
