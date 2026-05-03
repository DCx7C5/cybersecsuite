"""LLM model enumerations."""

from enum import Enum
from pathlib import Path
import sys


def _discover_providers():
    """Dynamically discover available providers from api_services."""
    api_services_path = Path(__file__).parent.parent.parent / "api_services"
    if not api_services_path.exists():
        return {}
    
    providers = {}
    for provider_dir in api_services_path.iterdir():
        if provider_dir.is_dir() and not provider_dir.name.startswith("_"):
            provider_name = provider_dir.name.upper()
            provider_key = provider_dir.name.lower()
            providers[provider_name] = provider_key
    
    return providers


# Dynamically generate ModelProvider enum from discovered providers
_discovered = _discover_providers()

if _discovered:
    ModelProvider = Enum('ModelProvider', {k: v for k, v in _discovered.items()})
else:
    # Fallback if discovery fails
    class ModelProvider(str, Enum):
        """LLM model providers (fallback)."""
        ANTHROPIC = "anthropic"
        OPENAI = "openai"
        GOOGLE = "google"


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

