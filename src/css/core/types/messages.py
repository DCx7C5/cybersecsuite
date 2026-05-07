"""Message types and API service base — msgspec.Struct (Phase 6 P1).

Replaces @dataclass BaseMessage, Tool, ModelMetadata, StreamChunk, LLMResponse, ExecutorResult.
Uses msgspec.Struct for 10-40× faster serialization.
"""

import logging
from typing import Any, AsyncIterator, Optional
from enum import Enum

import msgspec




logger = logging.getLogger(__name__)


class MessageRole(str, Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ProviderType(str, Enum):
    """Provider types for LLM services."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    MISTRAL = "mistral"
    XAI = "xai"
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"
    CEREBRAS = "cerebras"
    TOGETHER = "together"
    GITHUB = "github"
    CLOUDFLARE = "cloudflare"
    FIREWORKS = "fireworks"
    OPENCODE = "opencode"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"
    SAMBANOVA = "sambanova"
    DEEPINFRA = "deepinfra"
    AI21 = "ai21"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    NSCALE = "nscale"
    LAMBDA = "lambda"
    # Legacy/deprecated
    GOOGLE = "google"
    LOCAL = "local"


class BaseMessage(msgspec.Struct, frozen=True):
    """A message in the conversation."""
    role: MessageRole
    content: str = ""
    name: Optional[str] = None
    tool_calls: list[dict] = msgspec.field(default_factory=list)
    tool_call_id: Optional[str] = None


class Tool(msgspec.Struct, frozen=True):
    """A tool available to the model."""
    name: str
    description: str = ""
    input_schema: dict[str, Any] = msgspec.field(default_factory=dict)
    return_schema: Optional[dict[str, Any]] = None


class ModelMetadata(msgspec.Struct, frozen=True):
    """Metadata about a model with per-model feature flags."""
    id: str
    provider: ProviderType
    display_name: str = ""
    context_window: int = 4096
    max_output_tokens: int = 4096
    # Per-model feature flags (not provider-wide)
    streaming: bool = True
    vision: bool = False
    tool_use: bool = False
    prompt_caching: bool = False
    batch_api: bool = False
    structured_output: bool = False
    extended_thinking: bool = False
    files_api: bool = False
    tool_use_caching: bool = False
    # Cost
    input_cost_per_mtok: float = 0.0
    output_cost_per_mtok: float = 0.0


class StreamChunk(msgspec.Struct, frozen=True):
    """A chunk from a streaming response."""
    type: str = "content_block_delta"  # "content_block_delta", "message_stop", "error"
    content: Optional[str] = None
    stop_reason: Optional[str] = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)


class LLMResponse(msgspec.Struct, frozen=True):
    """A complete LLM response (buffered)."""
    text: str = ""
    stop_reason: str = "stop"
    usage: dict[str, Any] = msgspec.field(default_factory=dict)


class ExecutorResult(msgspec.Struct, frozen=True):
    """Result from an execution/API call to a provider."""
    status_code: int = 200
    headers: dict[str, str] = msgspec.field(default_factory=dict)
    body: Optional[dict[str, Any]] = None
    stream: Optional[AsyncIterator[bytes]] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    provider_id: str = ""
    model_id: str = ""
    request_id: Optional[str] = None

    @property
    def ok(self) -> bool:
        """Check if status code is successful (2xx range)."""
        return 200 <= self.status_code < 300


class ErrorStrategy(str, Enum):
    """Strategy for handling errors in hook and service execution."""
    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"
