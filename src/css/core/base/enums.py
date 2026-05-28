"""All type-related enums for css.core.base.

Single source of truth for enums used across the type system.
All type-related enums live here; other modules re-export if needed.
"""

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

class MessageRole(str, Enum):
    """Role of a message sender in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


def _normalize_provider_slug(slug: str) -> str:
    """Normalize provider slugs to canonical runtime IDs."""
    normalized = slug.strip().lower()
    alias_map = {
        "lambda_api": "lambda",
    }
    return alias_map.get(normalized, normalized)


def _read_provider_slug_from_spec(spec_file: Path) -> str | None:
    """Read top-level `name:` from spec.yaml safely."""
    try:
        for line in spec_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("name:"):
                value = stripped.split(":", 1)[1].strip().strip("'\"")
                if value:
                    return _normalize_provider_slug(value)
                return None
    except OSError:
        return None
    return None


def _provider_slug_from_path(provider_dir: Path) -> str:
    """Resolve runtime provider slug from directory and optional spec.yaml."""
    spec_file = provider_dir / "spec.yaml"
    if spec_file.exists():
        spec_slug = _read_provider_slug_from_spec(spec_file)
        if spec_slug:
            return spec_slug
    return _normalize_provider_slug(provider_dir.name.lower())


def _discover_provider_type_members() -> dict[str, str]:
    """Build ProviderType enum members from api_services directories."""
    api_services_path = Path(__file__).resolve().parents[2] / "api_services"
    providers = {
        _provider_slug_from_path(provider_dir)
        for provider_dir in api_services_path.iterdir()
        if provider_dir.is_dir() and not provider_dir.name.startswith("_")
    }
    if not providers:
        providers = {"openai"}
    return {slug.upper().replace("-", "_"): slug for slug in sorted(providers)}


if TYPE_CHECKING:
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
else:
    ProviderType = Enum("ProviderType", _discover_provider_type_members(), type=str)


class CapabilityType(str, Enum):
    """Capability types supported across LLM providers."""

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
    MEMORY_PERSISTENCE = "memory_persistence"


class MemorySupportMode(str, Enum):
    """How provider/model memory is supported at runtime."""

    NONE = "none"
    PLATFORM_EMULATED = "platform_emulated"
    NATIVE_TOOL = "native_tool"
    NATIVE_MANAGED = "native_managed"


class HookErrorStrategy(str, Enum):
    """How to handle errors in hook and service execution.

    PRESERVE_EXISTING: Don't break on hook failure (default, safest).
    LOG: Log errors to audit but don't propagate.
    WARN: Log warnings to audit but don't propagate.
    """

    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"

