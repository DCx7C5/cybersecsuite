"""LLM model enumerations."""

from enum import Enum


class ModelProvider(str, Enum):
    """LLM model providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    FIREWORKS = "fireworks"
    TOGETHER = "together"


class ModelFamily(str, Enum):
    """LLM model families."""
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    OPUS = "opus"
    SONNET = "sonnet"
    HAIKU = "haiku"
    LLAMA = "llama"
    MISTRAL_MODEL = "mistral"
    DEEPSEEK_MODEL = "deepseek"
    OPEN_SOURCE = "open_source"


class ModelCapability(str, Enum):
    """Model capability flags."""
    VISION = "vision"
    TOOL_USE = "tool_use"
    STREAMING = "streaming"
    BATCH_PROCESSING = "batch_processing"
    FUNCTION_CALLING = "function_calling"
    LONG_CONTEXT = "long_context"  # 100k+ context
    EXTENDED_THINKING = "extended_thinking"  # OpenAI o1-style
    FINE_TUNING = "fine_tuning"
    JSON_MODE = "json_mode"
