"""ModelNameMapper — normalize model aliases across providers.

Each provider uses different naming conventions:
- OpenAI: "gpt-4o"
- OpenRouter: "openai/gpt-4o"
- Fireworks: "accounts/fireworks/models/gpt-4o"
- HuggingFace: "mistralai/Mistral-7B-v0.1"
- Cloudflare: "@cf/meta/llama-3.1-8b-instruct"

Maps provider-specific aliases to canonical names and back.
"""

from css.core.logger import getLogger

logger = getLogger(__name__)

# Canonical model name → per-provider alias map
# canonical_name: lowercased, dashes for spaces, no provider prefix
_CANONICAL_TO_PROVIDER: dict[str, dict[str, str]] = {
    "gpt-4o": {
        "openai": "gpt-4o",
        "openrouter": "openai/gpt-4o",
        "fireworks": "accounts/fireworks/models/gpt-4o",
        "deepinfra": "openai/gpt-4o",
        "cerebras": "gpt-4o",
    },
    "gpt-4o-mini": {
        "openai": "gpt-4o-mini",
        "openrouter": "openai/gpt-4o-mini",
    },
    "gpt-4-turbo": {
        "openai": "gpt-4-turbo",
        "openrouter": "openai/gpt-4-turbo",
    },
    "gpt-3.5-turbo": {
        "openai": "gpt-3.5-turbo",
        "openrouter": "openai/gpt-3.5-turbo",
    },
    "claude-3-5-sonnet": {
        "anthropic": "claude-3-5-sonnet-20241022",
        "openrouter": "anthropic/claude-3.5-sonnet",
    },
    "claude-3-opus": {
        "anthropic": "claude-3-opus-20250219",
        "openrouter": "anthropic/claude-3-opus",
    },
    "claude-3-sonnet": {
        "anthropic": "claude-3-sonnet-20240229",
        "openrouter": "anthropic/claude-3-sonnet",
    },
    "claude-3-haiku": {
        "anthropic": "claude-3-haiku-20240307",
        "openrouter": "anthropic/claude-3-haiku",
    },
    "gemini-1.5-pro": {
        "gemini": "gemini-1.5-pro",
        "openrouter": "google/gemini-1.5-pro",
    },
    "gemini-1.5-flash": {
        "gemini": "gemini-1.5-flash",
        "openrouter": "google/gemini-1.5-flash",
    },
    "deepseek-chat": {
        "deepseek": "deepseek-chat",
        "openrouter": "deepseek/deepseek-chat",
    },
    "mistral-large": {
        "mistral": "mistral-large-latest",
        "openrouter": "mistralai/mistral-large",
    },
    "llama-3.1-8b": {
        "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "fireworks": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "cloudflare": "@cf/meta/llama-3.1-8b-instruct",
        "deepinfra": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "openrouter": "meta-llama/llama-3.1-8b-instruct",
        "groq": "llama-3.1-8b-instant",
    },
    "llama-3.1-70b": {
        "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "fireworks": "accounts/fireworks/models/llama-v3p1-70b-instruct",
        "deepinfra": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "openrouter": "meta-llama/llama-3.1-70b-instruct",
        "groq": "llama-3.1-70b-versatile",
    },
    "mistral-7b": {
        "huggingface": "mistralai/Mistral-7B-Instruct-v0.3",
        "together": "mistralai/Mistral-7B-Instruct-v0.3",
        "deepinfra": "mistralai/Mistral-7B-Instruct-v0.3",
    },
    "codestral": {
        "mistral": "codestral-latest",
        "openrouter": "mistralai/codestral",
    },
    "qwen3-0.6b": {
        "ollama": "qwen3:0.6b",
    },
    "phi4-mini": {
        "ollama": "phi4-mini:3.8b-q4_K_M",
    },
}

# Reverse index: (provider, provider_alias) → canonical_name
_PROVIDER_ALIAS_TO_CANONICAL: dict[tuple[str, str], str] = {}
for canonical, provider_map in _CANONICAL_TO_PROVIDER.items():
    for provider, alias in provider_map.items():
        _PROVIDER_ALIAS_TO_CANONICAL[(provider, alias)] = canonical


class ModelNameMapper:
    """Normalize model aliases across providers.

    Usage:
        mapper = ModelNameMapper()
        canonical = mapper.normalize("openrouter", "openai/gpt-4o")
        # → "gpt-4o"

        alias = mapper.alias("fireworks", "gpt-4o")
        # → "accounts/fireworks/models/gpt-4o"
    """

    @staticmethod
    def normalize(provider: str, model_alias: str) -> str:
        """Convert provider-specific model name to canonical name.

        Args:
            provider: Provider identifier (e.g. "openai", "openrouter")
            model_alias: Provider-specific model name

        Returns:
            Canonical model name, or original alias if not found
        """
        key = (provider, model_alias)
        canonical = _PROVIDER_ALIAS_TO_CANONICAL.get(key)
        if canonical:
            return canonical

        trimmed = model_alias.split("/")[-1].removeprefix("@cf/").strip()
        for canonical_name in _CANONICAL_TO_PROVIDER:
            if trimmed == canonical_name or trimmed.startswith(canonical_name):
                return canonical_name

        logger.debug(f"No canonical mapping for {provider}/{model_alias}, using as-is")
        return model_alias

    @staticmethod
    def alias(provider: str, canonical_name: str) -> str | None:
        """Get provider-specific name for a canonical model.

        Args:
            provider: Target provider identifier
            canonical_name: Canonical model name

        Returns:
            Provider-specific model name, or None if not mapped
        """
        provider_map = _CANONICAL_TO_PROVIDER.get(canonical_name)
        if provider_map:
            return provider_map.get(provider)
        return None

    @staticmethod
    def list_canonical() -> list[str]:
        """List all known canonical model names."""
        return sorted(_CANONICAL_TO_PROVIDER.keys())

    @staticmethod
    def providers_for(canonical_name: str) -> list[str]:
        """List providers that offer a given canonical model."""
        provider_map = _CANONICAL_TO_PROVIDER.get(canonical_name, {})
        return sorted(provider_map.keys())

    @staticmethod
    def register_alias(canonical_name: str, provider: str, alias: str) -> None:
        """Register a new alias mapping at runtime.

        Args:
            canonical_name: Canonical model name
            provider: Provider identifier
            alias: Provider-specific model name
        """
        if canonical_name not in _CANONICAL_TO_PROVIDER:
            _CANONICAL_TO_PROVIDER[canonical_name] = {}
        _CANONICAL_TO_PROVIDER[canonical_name][provider] = alias
        _PROVIDER_ALIAS_TO_CANONICAL[(provider, alias)] = canonical_name


__all__ = ["ModelNameMapper"]
