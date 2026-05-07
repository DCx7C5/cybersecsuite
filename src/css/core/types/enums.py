"""All type-related enums for css.core.types.

Single source of truth for enums used across the type system.
All type-related enums live here; other modules re-export if needed.
"""

from enum import Enum


class MessageRole(str, Enum):
    """Role of a message sender in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ProviderType(str, Enum):
    """LLM provider identifiers."""

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


class CapabilityType(str, Enum):
    """11 capability types supported across LLM providers."""

    STREAMING = "streaming"
    VISION = "vision"
    TOOL_USE = "tool_use"
    VISION_AND_TOOL = "vision_and_tool"
    JSON_MODE = "json_mode"
    LONG_CONTEXT = "long_context"
    BATCH_PROCESSING = "batch_processing"
    EMBEDDINGS = "embeddings"
    RETRIEVAL = "retrieval"
    FINE_TUNING = "fine_tuning"
    REASONING = "reasoning"


class HookErrorStrategy(str, Enum):
    """How to handle errors in hook and service execution.

    PRESERVE_EXISTING: Don't break on hook failure (default, safest).
    LOG: Log errors to audit but don't propagate.
    WARN: Log warnings to audit but don't propagate.
    """

    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"


__all__ = [
    "MessageRole",
    "ProviderType",
    "CapabilityType",
    "HookErrorStrategy",
]
