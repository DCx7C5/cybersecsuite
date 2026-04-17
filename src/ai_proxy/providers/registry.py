"""
Provider Registry — Pydantic-validated provider configurations.

Mirrors OmniRoute's providerRegistry.ts: each provider has a base URL,
auth scheme, API format, model list, and cost metadata.
Supports custom providers loaded from YAML config or environment,
including Playwright-based browser automation providers.
"""
from __future__ import annotations

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("ai_proxy.registry")


class AuthType(str, Enum):
    API_KEY = "api_key"
    OAUTH = "oauth"
    NONE = "none"
    BROWSER = "browser"  # Playwright-based auth (cookie/session)


class ApiFormat(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    CUSTOM = "custom"  # Custom format requiring a dedicated executor


class ModelCost(BaseModel):
    """Cost per 1M tokens (USD)."""
    input: float = 0.0
    output: float = 0.0
    cached_input: float = 0.0


class ModelConfig(BaseModel):
    id: str
    name: str
    context_window: int = 128_000
    max_output: int = 4096
    cost: ModelCost = Field(default_factory=ModelCost)
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_vision: bool = False
    deprecated: bool = False


class ProviderConfig(BaseModel):
    id: str
    name: str
    base_url: str
    auth_type: AuthType = AuthType.API_KEY
    auth_header: str = "Authorization"
    auth_prefix: str = "Bearer "
    api_format: ApiFormat = ApiFormat.OPENAI
    env_key: str = ""
    models: list[ModelConfig] = Field(default_factory=list)
    is_free: bool = False
    enabled: bool = True
    max_retries: int = 3
    timeout_seconds: int = 120
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 1_000_000
    extra: dict[str, Any] = Field(default_factory=dict)
    # Playwright/browser config
    browser_profile: str | None = None  # Path to browser user data dir
    browser_executable: str | None = None  # Path to browser binary
    headless: bool = True

    def get_api_key(self) -> str | None:
        if self.auth_type in (AuthType.NONE, AuthType.BROWSER):
            return None
        if self.env_key:
            return os.environ.get(self.env_key)
        return os.environ.get(f"{self.id.upper().replace('-', '_')}_API_KEY")

    def get_model(self, model_id: str) -> ModelConfig | None:
        for m in self.models:
            if m.id == model_id:
                return m
        return None

    @property
    def is_available(self) -> bool:
        """Check if provider is usable (has credentials or is free/browser-based)."""
        if not self.enabled:
            return False
        if self.auth_type in (AuthType.NONE, AuthType.BROWSER):
            return True
        return self.get_api_key() is not None


# ── Built-in provider definitions ────────────────────────────────────────────

_PROVIDERS: dict[str, ProviderConfig] = {}


def _register(cfg: ProviderConfig) -> None:
    _PROVIDERS[cfg.id] = cfg


def get_provider(provider_id: str) -> ProviderConfig | None:
    return _PROVIDERS.get(provider_id)


def get_all_providers() -> dict[str, ProviderConfig]:
    return dict(_PROVIDERS)


def get_enabled_providers() -> list[ProviderConfig]:
    """Return providers that are enabled AND have credentials (or are free/browser)."""
    return [p for p in _PROVIDERS.values() if p.is_available]


def get_free_providers() -> list[ProviderConfig]:
    return [p for p in _PROVIDERS.values() if p.is_free and p.enabled]


def get_browser_providers() -> list[ProviderConfig]:
    """Return providers that use Playwright browser automation."""
    return [p for p in _PROVIDERS.values() if p.auth_type == AuthType.BROWSER and p.enabled]


def find_model(model_id: str) -> tuple[ProviderConfig, ModelConfig] | None:
    """Find a model across all providers. Returns (provider, model) or None."""
    for p in _PROVIDERS.values():
        if not p.is_available:
            continue
        m = p.get_model(model_id)
        if m and not m.deprecated:
            return (p, m)
    return None


def find_cheapest_model(
    min_context: int = 0,
    supports_tools: bool = False,
    supports_vision: bool = False,
) -> tuple[ProviderConfig, ModelConfig] | None:
    """Find the cheapest available model matching constraints."""
    best: tuple[ProviderConfig, ModelConfig] | None = None
    best_cost = float("inf")
    for p in _PROVIDERS.values():
        if not p.is_available:
            continue
        for m in p.models:
            if m.deprecated or m.context_window < min_context:
                continue
            if supports_tools and not m.supports_tools:
                continue
            if supports_vision and not m.supports_vision:
                continue
            cost = m.cost.input + m.cost.output
            if cost < best_cost:
                best_cost = cost
                best = (p, m)
    return best


def list_all_models() -> list[dict[str, Any]]:
    """Return OpenAI-compatible model list."""
    models = []
    for p in _PROVIDERS.values():
        if not p.enabled:
            continue
        for m in p.models:
            if m.deprecated:
                continue
            models.append({
                "id": m.id,
                "object": "model",
                "created": 0,
                "owned_by": p.id,
                "context_window": m.context_window,
                "max_output": m.max_output,
            })
    return models


def register_provider(cfg: ProviderConfig) -> None:
    """Register a custom provider at runtime."""
    _PROVIDERS[cfg.id] = cfg
    logger.info("Registered custom provider: %s (%s)", cfg.id, cfg.name)


def unregister_provider(provider_id: str) -> bool:
    """Remove a provider. Returns True if it existed."""
    return _PROVIDERS.pop(provider_id, None) is not None


# ── Custom provider loading ──────────────────────────────────────────────────

def load_custom_providers(config_path: str | Path | None = None) -> int:
    """
    Load custom provider definitions from a YAML file.

    Default path: ~/.cybersecsuite/providers.yaml or
    CYBERSEC_PROVIDERS_CONFIG env var.

    Format:
        providers:
          - id: my-custom
            name: My Custom Provider
            base_url: http://localhost:8080/v1
            auth_type: none
            is_free: true
            models:
              - id: custom-model
                name: Custom Model
                context_window: 32000
          - id: my-browser-provider
            name: Browser LLM
            base_url: https://chat.example.com
            auth_type: browser
            browser_profile: /path/to/profile
            browser_executable: /usr/bin/brave
            models:
              - id: example-chat
                name: Example Chat
    """
    if config_path is None:
        config_path = os.environ.get(
            "CYBERSEC_PROVIDERS_CONFIG",
            os.path.expanduser("~/.cybersecsuite/providers.yaml"),
        )

    path = Path(config_path)
    if not path.exists():
        return 0

    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        logger.warning("Failed to load custom providers from %s: %s", path, exc)
        return 0

    if not isinstance(data, dict) or "providers" not in data:
        return 0

    count = 0
    for entry in data["providers"]:
        try:
            # Convert model dicts to ModelConfig
            models = []
            for m in entry.pop("models", []):
                cost_data = m.pop("cost", {})
                models.append(ModelConfig(cost=ModelCost(**cost_data), **m))
            cfg = ProviderConfig(models=models, **entry)
            register_provider(cfg)
            count += 1
        except Exception as exc:
            logger.warning("Skipping invalid custom provider %s: %s", entry.get("id", "?"), exc)

    logger.info("Loaded %d custom provider(s) from %s", count, path)
    return count


def load_openai_compatible_from_env() -> int:
    """
    Auto-detect OpenAI-compatible providers from environment variables.

    Pattern: CUSTOM_PROVIDER_<NAME>_URL + CUSTOM_PROVIDER_<NAME>_KEY
    Example:
        CUSTOM_PROVIDER_MYHOST_URL=http://myhost:8080/v1
        CUSTOM_PROVIDER_MYHOST_KEY=sk-xxx
        CUSTOM_PROVIDER_MYHOST_MODEL=my-model  (optional, default: "default")
    """
    count = 0
    prefix = "CUSTOM_PROVIDER_"
    seen: set[str] = set()

    for key in os.environ:
        if key.startswith(prefix) and key.endswith("_URL"):
            name = key[len(prefix):-4]
            if name in seen:
                continue
            seen.add(name)

            url = os.environ[key]
            api_key_env = f"{prefix}{name}_KEY"
            model_id = os.environ.get(f"{prefix}{name}_MODEL", "default")
            provider_id = f"custom-{name.lower()}"

            cfg = ProviderConfig(
                id=provider_id,
                name=f"Custom: {name}",
                base_url=url,
                env_key=api_key_env if api_key_env in os.environ else "",
                auth_type=AuthType.NONE if api_key_env not in os.environ else AuthType.API_KEY,
                models=[ModelConfig(id=model_id, name=model_id)],
            )
            register_provider(cfg)
            count += 1

    if count:
        logger.info("Loaded %d custom provider(s) from environment", count)
    return count


# ── Default providers ────────────────────────────────────────────────────────

_register(ProviderConfig(
    id="openai",
    name="OpenAI",
    base_url="https://api.openai.com/v1",
    env_key="OPENAI_API_KEY",
    models=[
        ModelConfig(id="gpt-4o", name="GPT-4o", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=2.5, output=10.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="gpt-4o-mini", name="GPT-4o Mini", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=0.15, output=0.6), supports_tools=True, supports_vision=True),
        ModelConfig(id="gpt-4.1", name="GPT-4.1", context_window=1_047_576, max_output=32_768,
                    cost=ModelCost(input=2.0, output=8.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="gpt-4.1-mini", name="GPT-4.1 Mini", context_window=1_047_576, max_output=32_768,
                    cost=ModelCost(input=0.4, output=1.6), supports_tools=True, supports_vision=True),
        ModelConfig(id="gpt-4.1-nano", name="GPT-4.1 Nano", context_window=1_047_576, max_output=32_768,
                    cost=ModelCost(input=0.1, output=0.4), supports_tools=True, supports_vision=True),
        ModelConfig(id="o3", name="o3", context_window=200_000, max_output=100_000,
                    cost=ModelCost(input=2.0, output=8.0), supports_tools=True),
        ModelConfig(id="o3-mini", name="o3-mini", context_window=200_000, max_output=100_000,
                    cost=ModelCost(input=1.1, output=4.4), supports_tools=True),
        ModelConfig(id="o4-mini", name="o4-mini", context_window=200_000, max_output=100_000,
                    cost=ModelCost(input=1.1, output=4.4), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="anthropic",
    name="Anthropic",
    base_url="https://api.anthropic.com/v1",
    auth_header="x-api-key",
    auth_prefix="",
    api_format=ApiFormat.ANTHROPIC,
    env_key="ANTHROPIC_API_KEY",
    models=[
        ModelConfig(id="claude-sonnet-4-20250514", name="Claude Sonnet 4", context_window=200_000, max_output=16_000,
                    cost=ModelCost(input=3.0, output=15.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="claude-3-7-sonnet-20250219", name="Claude 3.7 Sonnet", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=3.0, output=15.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="claude-3-5-haiku-20241022", name="Claude 3.5 Haiku", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=0.8, output=4.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="claude-3-opus-20240229", name="Claude 3 Opus", context_window=200_000, max_output=4_096,
                    cost=ModelCost(input=15.0, output=75.0), supports_tools=True, supports_vision=True),
    ],
))

_register(ProviderConfig(
    id="gemini",
    name="Google Gemini",
    base_url="https://generativelanguage.googleapis.com/v1beta",
    api_format=ApiFormat.GEMINI,
    env_key="GEMINI_API_KEY",
    models=[
        ModelConfig(id="gemini-2.5-pro-preview-05-06", name="Gemini 2.5 Pro", context_window=1_048_576, max_output=65_536,
                    cost=ModelCost(input=1.25, output=10.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="gemini-2.5-flash-preview-04-17", name="Gemini 2.5 Flash", context_window=1_048_576, max_output=65_536,
                    cost=ModelCost(input=0.15, output=0.6), supports_tools=True, supports_vision=True),
        ModelConfig(id="gemini-2.0-flash", name="Gemini 2.0 Flash", context_window=1_048_576, max_output=8_192,
                    cost=ModelCost(input=0.1, output=0.4), supports_tools=True, supports_vision=True),
    ],
))

_register(ProviderConfig(
    id="deepseek",
    name="DeepSeek",
    base_url="https://api.deepseek.com/v1",
    env_key="DEEPSEEK_API_KEY",
    models=[
        ModelConfig(id="deepseek-chat", name="DeepSeek V3", context_window=64_000, max_output=8_192,
                    cost=ModelCost(input=0.27, output=1.10), supports_tools=True),
        ModelConfig(id="deepseek-reasoner", name="DeepSeek R1", context_window=64_000, max_output=8_192,
                    cost=ModelCost(input=0.55, output=2.19)),
    ],
))

_register(ProviderConfig(
    id="groq",
    name="Groq",
    base_url="https://api.groq.com/openai/v1",
    env_key="GROQ_API_KEY",
    rate_limit_rpm=30,
    models=[
        ModelConfig(id="llama-3.3-70b-versatile", name="Llama 3.3 70B", context_window=128_000, max_output=32_768,
                    cost=ModelCost(input=0.59, output=0.79), supports_tools=True),
        ModelConfig(id="meta-llama/llama-4-scout-17b-16e-instruct", name="Llama 4 Scout", context_window=512_000, max_output=8_192,
                    cost=ModelCost(input=0.11, output=0.34), supports_tools=True),
        ModelConfig(id="meta-llama/llama-4-maverick-17b-128e-instruct", name="Llama 4 Maverick", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.50, output=0.77), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="mistral",
    name="Mistral AI",
    base_url="https://api.mistral.ai/v1",
    env_key="MISTRAL_API_KEY",
    models=[
        ModelConfig(id="mistral-large-latest", name="Mistral Large", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=2.0, output=6.0), supports_tools=True),
        ModelConfig(id="mistral-small-latest", name="Mistral Small", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.1, output=0.3), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="xai",
    name="xAI",
    base_url="https://api.x.ai/v1",
    env_key="XAI_API_KEY",
    models=[
        ModelConfig(id="grok-3", name="Grok 3", context_window=131_072, max_output=16_384,
                    cost=ModelCost(input=3.0, output=15.0), supports_tools=True),
        ModelConfig(id="grok-3-mini", name="Grok 3 Mini", context_window=131_072, max_output=16_384,
                    cost=ModelCost(input=0.3, output=0.5), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="together",
    name="Together AI",
    base_url="https://api.together.xyz/v1",
    env_key="TOGETHER_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct-Turbo", name="Llama 3.3 70B Turbo",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.88, output=0.88)),
        ModelConfig(id="deepseek-ai/DeepSeek-R1", name="DeepSeek R1 (Together)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=3.0, output=7.0)),
    ],
))

_register(ProviderConfig(
    id="openrouter",
    name="OpenRouter",
    base_url="https://openrouter.ai/api/v1",
    env_key="OPENROUTER_API_KEY",
    models=[
        ModelConfig(id="openai/gpt-4o", name="GPT-4o (OpenRouter)", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=2.5, output=10.0), supports_tools=True, supports_vision=True),
        ModelConfig(id="anthropic/claude-sonnet-4-20250514", name="Claude Sonnet 4 (OpenRouter)", context_window=200_000, max_output=16_000,
                    cost=ModelCost(input=3.0, output=15.0), supports_tools=True, supports_vision=True),
    ],
))

# ── Free providers ───────────────────────────────────────────────────────────

_register(ProviderConfig(
    id="pollinations",
    name="Pollinations AI",
    base_url="https://text.pollinations.ai/openai",
    auth_type=AuthType.NONE,
    is_free=True,
    rate_limit_rpm=10,
    models=[
        ModelConfig(id="openai", name="Pollinations OpenAI", context_window=128_000, max_output=4_096),
        ModelConfig(id="mistral", name="Pollinations Mistral", context_window=32_000, max_output=4_096),
    ],
))

_register(ProviderConfig(
    id="cerebras",
    name="Cerebras",
    base_url="https://api.cerebras.ai/v1",
    env_key="CEREBRAS_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b", name="Llama 3.3 70B (Cerebras)", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.85, output=1.20)),
    ],
))

_register(ProviderConfig(
    id="sambanova",
    name="SambaNova",
    base_url="https://api.sambanova.ai/v1",
    env_key="SAMBANOVA_API_KEY",
    models=[
        ModelConfig(id="Meta-Llama-3.3-70B-Instruct", name="Llama 3.3 70B (SambaNova)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.6, output=1.2)),
    ],
))

_register(ProviderConfig(
    id="deepinfra",
    name="DeepInfra",
    base_url="https://api.deepinfra.com/v1/openai",
    env_key="DEEPINFRA_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (DeepInfra)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.35, output=0.40)),
        ModelConfig(id="meta-llama/Llama-4-Maverick-17B-128E-Instruct", name="Llama 4 Maverick (DeepInfra)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.18, output=0.25)),
    ],
))

# ── Additional providers ─────────────────────────────────────────────────────

_register(ProviderConfig(
    id="perplexity",
    name="Perplexity",
    base_url="https://api.perplexity.ai",
    env_key="PERPLEXITY_API_KEY",
    models=[
        ModelConfig(id="sonar-pro", name="Sonar Pro", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=3.0, output=15.0), supports_tools=True),
        ModelConfig(id="sonar", name="Sonar", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.0, output=1.0)),
    ],
))

_register(ProviderConfig(
    id="fireworks",
    name="Fireworks AI",
    base_url="https://api.fireworks.ai/inference/v1",
    env_key="FIREWORKS_API_KEY",
    models=[
        ModelConfig(id="accounts/fireworks/models/llama-v3p3-70b-instruct", name="Llama 3.3 70B (Fireworks)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.9, output=0.9)),
        ModelConfig(id="accounts/fireworks/models/deepseek-r1", name="DeepSeek R1 (Fireworks)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=3.0, output=8.0)),
    ],
))

_register(ProviderConfig(
    id="cohere",
    name="Cohere",
    base_url="https://api.cohere.com/v2",
    env_key="COHERE_API_KEY",
    models=[
        ModelConfig(id="command-r-plus", name="Command R+", context_window=128_000, max_output=4_096,
                    cost=ModelCost(input=2.5, output=10.0), supports_tools=True),
        ModelConfig(id="command-r", name="Command R", context_window=128_000, max_output=4_096,
                    cost=ModelCost(input=0.15, output=0.6), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="nvidia",
    name="NVIDIA NIM",
    base_url="https://integrate.api.nvidia.com/v1",
    env_key="NVIDIA_API_KEY",
    models=[
        ModelConfig(id="meta/llama-3.3-70b-instruct", name="Llama 3.3 70B (NVIDIA)",
                    context_window=128_000, max_output=4_096, cost=ModelCost(input=0.40, output=0.40)),
        ModelConfig(id="nvidia/llama-3.1-nemotron-70b-instruct", name="Nemotron 70B",
                    context_window=128_000, max_output=4_096, cost=ModelCost(input=0.40, output=0.40)),
    ],
))

_register(ProviderConfig(
    id="ai21",
    name="AI21 Labs",
    base_url="https://api.ai21.com/studio/v1",
    env_key="AI21_API_KEY",
    models=[
        ModelConfig(id="jamba-1.5-large", name="Jamba 1.5 Large", context_window=256_000, max_output=4_096,
                    cost=ModelCost(input=2.0, output=8.0), supports_tools=True),
        ModelConfig(id="jamba-1.5-mini", name="Jamba 1.5 Mini", context_window=256_000, max_output=4_096,
                    cost=ModelCost(input=0.2, output=0.4), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="huggingface",
    name="HuggingFace Inference",
    base_url="https://api-inference.huggingface.co/v1",
    env_key="HUGGINGFACE_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (HF)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.35, output=0.40)),
        ModelConfig(id="Qwen/Qwen2.5-72B-Instruct", name="Qwen 2.5 72B (HF)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.35, output=0.40)),
    ],
))

_register(ProviderConfig(
    id="cloudflare",
    name="Cloudflare Workers AI",
    base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
    env_key="CLOUDFLARE_API_KEY",
    extra={"account_id_env": "CLOUDFLARE_ACCOUNT_ID"},
    models=[
        ModelConfig(id="@cf/meta/llama-3.3-70b-instruct-fp8-fast", name="Llama 3.3 70B (CF)",
                    context_window=128_000, max_output=4_096, cost=ModelCost(input=0.0, output=0.0)),
    ],
))

_register(ProviderConfig(
    id="ollama",
    name="Ollama (Local)",
    base_url="http://localhost:11434/v1",
    auth_type=AuthType.NONE,
    is_free=True,
    rate_limit_rpm=120,
    models=[
        ModelConfig(id="llama3.3", name="Llama 3.3 (Ollama)", context_window=128_000, max_output=8_192),
        ModelConfig(id="qwen2.5:72b", name="Qwen 2.5 72B (Ollama)", context_window=128_000, max_output=8_192),
        ModelConfig(id="deepseek-r1:70b", name="DeepSeek R1 70B (Ollama)", context_window=64_000, max_output=8_192),
        ModelConfig(id="gemma2:27b", name="Gemma 2 27B (Ollama)", context_window=8_192, max_output=4_096),
    ],
))

_register(ProviderConfig(
    id="lmstudio",
    name="LM Studio (Local)",
    base_url="http://localhost:1234/v1",
    auth_type=AuthType.NONE,
    is_free=True,
    rate_limit_rpm=120,
    models=[
        ModelConfig(id="local-model", name="Local Model (LM Studio)", context_window=128_000, max_output=8_192),
    ],
))

_register(ProviderConfig(
    id="nscale",
    name="nScale",
    base_url="https://inference.api.nscale.com/v1",
    env_key="NSCALE_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (nScale)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.20, output=0.20)),
        ModelConfig(id="deepseek-ai/DeepSeek-R1-0528", name="DeepSeek R1 (nScale)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=0.50, output=1.50)),
    ],
))

_register(ProviderConfig(
    id="featherless",
    name="Featherless AI",
    base_url="https://api.featherless.ai/v1",
    env_key="FEATHERLESS_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (Featherless)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.20, output=0.20)),
    ],
))

_register(ProviderConfig(
    id="lambda",
    name="Lambda AI",
    base_url="https://api.lambdalabs.com/v1",
    env_key="LAMBDA_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b-instruct", name="Llama 3.3 70B (Lambda)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.40, output=0.40)),
    ],
))

# ── More cloud providers ─────────────────────────────────────────────────────

_register(ProviderConfig(
    id="nebius",
    name="Nebius AI",
    base_url="https://api.studio.nebius.ai/v1",
    env_key="NEBIUS_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (Nebius)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.24, output=0.24)),
        ModelConfig(id="deepseek-ai/DeepSeek-R1", name="DeepSeek R1 (Nebius)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=0.80, output=0.80)),
        ModelConfig(id="Qwen/Qwen2.5-72B-Instruct", name="Qwen 2.5 72B (Nebius)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.30, output=0.30)),
    ],
))

_register(ProviderConfig(
    id="siliconflow",
    name="SiliconFlow",
    base_url="https://api.siliconflow.cn/v1",
    env_key="SILICONFLOW_API_KEY",
    models=[
        ModelConfig(id="deepseek-ai/DeepSeek-R1", name="DeepSeek R1 (SiliconFlow)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=0.55, output=2.19)),
        ModelConfig(id="Qwen/Qwen2.5-72B-Instruct", name="Qwen 2.5 72B (SiliconFlow)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.26, output=0.26)),
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (SiliconFlow)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.28, output=0.28)),
    ],
))

_register(ProviderConfig(
    id="hyperbolic",
    name="Hyperbolic",
    base_url="https://api.hyperbolic.xyz/v1",
    env_key="HYPERBOLIC_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (Hyperbolic)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.40, output=0.40)),
        ModelConfig(id="deepseek-ai/DeepSeek-R1", name="DeepSeek R1 (Hyperbolic)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=2.00, output=2.00)),
        ModelConfig(id="Qwen/Qwen2.5-72B-Instruct", name="Qwen 2.5 72B (Hyperbolic)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.40, output=0.40)),
    ],
))

_register(ProviderConfig(
    id="novita",
    name="Novita AI",
    base_url="https://api.novita.ai/v3/openai",
    env_key="NOVITA_API_KEY",
    models=[
        ModelConfig(id="meta-llama/llama-3.3-70b-instruct", name="Llama 3.3 70B (Novita)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.29, output=0.29)),
        ModelConfig(id="deepseek/deepseek-r1", name="DeepSeek R1 (Novita)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=0.55, output=2.19)),
    ],
))

_register(ProviderConfig(
    id="moonshot",
    name="Moonshot AI",
    base_url="https://api.moonshot.cn/v1",
    env_key="MOONSHOT_API_KEY",
    models=[
        ModelConfig(id="moonshot-v1-128k", name="Moonshot V1 128K", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.82, output=0.82)),
        ModelConfig(id="moonshot-v1-32k", name="Moonshot V1 32K", context_window=32_000, max_output=8_192,
                    cost=ModelCost(input=0.34, output=0.34)),
    ],
))

_register(ProviderConfig(
    id="volcengine",
    name="Volcengine (ByteDance)",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    env_key="VOLCENGINE_API_KEY",
    models=[
        ModelConfig(id="doubao-1.5-pro-32k", name="Doubao 1.5 Pro", context_window=32_000, max_output=4_096,
                    cost=ModelCost(input=0.30, output=0.60)),
    ],
))

_register(ProviderConfig(
    id="alibaba",
    name="Alibaba DashScope",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    env_key="DASHSCOPE_API_KEY",
    models=[
        ModelConfig(id="qwen-max", name="Qwen Max", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.60, output=6.40), supports_tools=True),
        ModelConfig(id="qwen-plus", name="Qwen Plus", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.30, output=1.20), supports_tools=True),
        ModelConfig(id="qwen-turbo", name="Qwen Turbo", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.06, output=0.18), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="venice",
    name="Venice.ai",
    base_url="https://api.venice.ai/api/v1",
    env_key="VENICE_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b", name="Llama 3.3 70B (Venice)", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.35, output=0.40)),
        ModelConfig(id="deepseek-r1-671b", name="DeepSeek R1 (Venice)", context_window=64_000, max_output=8_192,
                    cost=ModelCost(input=1.00, output=3.00)),
    ],
))

_register(ProviderConfig(
    id="scaleway",
    name="Scaleway AI",
    base_url="https://api.scaleway.ai/v1",
    env_key="SCALEWAY_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b-instruct", name="Llama 3.3 70B (Scaleway)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.36, output=0.36)),
        ModelConfig(id="qwen2.5-72b-instruct", name="Qwen 2.5 72B (Scaleway)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.36, output=0.36)),
    ],
))

_register(ProviderConfig(
    id="ovhcloud",
    name="OVHcloud AI",
    base_url="https://llama-3-3-70b-instruct.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1",
    env_key="OVHCLOUD_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b-instruct", name="Llama 3.3 70B (OVH)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.35, output=0.35)),
    ],
))

_register(ProviderConfig(
    id="baseten",
    name="Baseten",
    base_url="https://bridge.baseten.co/v1",
    env_key="BASETEN_API_KEY",
    models=[
        ModelConfig(id="llama-3.3-70b-instruct", name="Llama 3.3 70B (Baseten)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.59, output=0.79)),
    ],
))

_register(ProviderConfig(
    id="friendliai",
    name="FriendliAI",
    base_url="https://inference.friendli.ai/v1",
    env_key="FRIENDLIAI_API_KEY",
    models=[
        ModelConfig(id="meta-llama-3.3-70b-instruct", name="Llama 3.3 70B (FriendliAI)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.28, output=0.28)),
        ModelConfig(id="deepseek-r1", name="DeepSeek R1 (FriendliAI)",
                    context_window=64_000, max_output=8_192, cost=ModelCost(input=0.55, output=2.19)),
    ],
))

_register(ProviderConfig(
    id="databricks",
    name="Databricks",
    base_url="https://adb-0000.0.azuredatabricks.net/serving-endpoints",
    env_key="DATABRICKS_API_KEY",
    extra={"workspace_url_env": "DATABRICKS_WORKSPACE_URL"},
    models=[
        ModelConfig(id="databricks-meta-llama-3-3-70b-instruct", name="Llama 3.3 70B (Databricks)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.60, output=1.80)),
    ],
))

_register(ProviderConfig(
    id="heroku",
    name="Heroku AI",
    base_url="https://us.inference.heroku.com/v1",
    env_key="HEROKU_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (Heroku)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.65, output=0.85)),
    ],
))

_register(ProviderConfig(
    id="upstage",
    name="Upstage",
    base_url="https://api.upstage.ai/v1/solar",
    env_key="UPSTAGE_API_KEY",
    models=[
        ModelConfig(id="solar-pro", name="Solar Pro", context_window=32_000, max_output=4_096,
                    cost=ModelCost(input=1.50, output=4.50), supports_tools=True),
        ModelConfig(id="solar-mini", name="Solar Mini", context_window=32_000, max_output=4_096,
                    cost=ModelCost(input=0.15, output=0.45)),
    ],
))

_register(ProviderConfig(
    id="nanogpt",
    name="NanoGPT",
    base_url="https://nano-gpt.com/api/v1",
    env_key="NANOGPT_API_KEY",
    models=[
        ModelConfig(id="chatgpt-4o-latest", name="GPT-4o (NanoGPT)", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=2.5, output=10.0), supports_tools=True),
        ModelConfig(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet (NanoGPT)", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=3.0, output=15.0)),
    ],
))

_register(ProviderConfig(
    id="aimlapi",
    name="AI/ML API",
    base_url="https://api.aimlapi.com/v1",
    env_key="AIMLAPI_API_KEY",
    models=[
        ModelConfig(id="gpt-4o", name="GPT-4o (AIML)", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=2.5, output=10.0), supports_tools=True),
        ModelConfig(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet (AIML)", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=3.0, output=15.0)),
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct-Turbo", name="Llama 3.3 70B (AIML)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.50, output=0.50)),
    ],
))

_register(ProviderConfig(
    id="wandb",
    name="Weights & Biases",
    base_url="https://api.wandb.ai/proxy/v1",
    env_key="WANDB_API_KEY",
    models=[
        ModelConfig(id="meta-llama/Llama-3.3-70B-Instruct", name="Llama 3.3 70B (W&B)",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.0, output=0.0)),
    ],
))

_register(ProviderConfig(
    id="meta-llama",
    name="Meta Llama API",
    base_url="https://api.llama.com/v1",
    env_key="META_LLAMA_API_KEY",
    models=[
        ModelConfig(id="Llama-4-Maverick-17B-128E-Instruct-FP8", name="Llama 4 Maverick",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.18, output=0.25)),
        ModelConfig(id="Llama-4-Scout-17B-16E-Instruct", name="Llama 4 Scout",
                    context_window=512_000, max_output=8_192, cost=ModelCost(input=0.11, output=0.34)),
        ModelConfig(id="Llama-3.3-70B-Instruct", name="Llama 3.3 70B",
                    context_window=128_000, max_output=8_192, cost=ModelCost(input=0.40, output=0.40)),
    ],
))

_register(ProviderConfig(
    id="galadriel",
    name="Galadriel",
    base_url="https://api.galadriel.com/v1",
    auth_type=AuthType.NONE,
    is_free=True,
    rate_limit_rpm=20,
    models=[
        ModelConfig(id="llama-3.3-70b", name="Llama 3.3 70B (Galadriel)", context_window=128_000, max_output=8_192),
    ],
))

# ── Search providers (OpenAI-compatible) ─────────────────────────────────────

_register(ProviderConfig(
    id="perplexity-search",
    name="Perplexity Search",
    base_url="https://api.perplexity.ai",
    env_key="PERPLEXITY_API_KEY",
    models=[
        ModelConfig(id="sonar-pro", name="Sonar Pro (Search)", context_window=200_000, max_output=8_192,
                    cost=ModelCost(input=3.0, output=15.0)),
        ModelConfig(id="sonar-deep-research", name="Sonar Deep Research", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=2.0, output=8.0)),
    ],
))


# ── Browser-based providers (Playwright + Brave stealth) ─────────────────────

_BRAVE_PATH = os.environ.get("BRAVE_BROWSER_PATH", "/usr/bin/brave-browser")
_BRAVE_PROFILE = os.environ.get(
    "BRAVE_PROFILE_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "mcps" / "brave_stealth_profile"),
)

_register(ProviderConfig(
    id="grok-web",
    name="Grok (x.com)",
    base_url="https://x.com/i/grok",
    auth_type=AuthType.BROWSER,
    api_format=ApiFormat.CUSTOM,
    is_free=True,
    rate_limit_rpm=5,
    browser_profile=_BRAVE_PROFILE,
    browser_executable=_BRAVE_PATH,
    headless=True,
    models=[
        ModelConfig(id="grok-3", name="Grok 3 (x.com Web)", context_window=128_000, max_output=16_384),
        ModelConfig(id="grok-3-mini", name="Grok 3 Mini (x.com Web)", context_window=128_000, max_output=16_384),
    ],
    extra={
        "input_selector": 'div[data-testid="grokInput"] textarea, textarea[placeholder*="Ask"], div[contenteditable="true"]',
        "submit_selector": 'button[data-testid="grokSubmitButton"], button[aria-label="Submit"], button[type="submit"]',
        "output_selector": 'div[data-testid="grokResponse"], div[class*="response"], div[class*="message"]',
        "wait_selector": 'div[data-testid="grokResponse"], div[class*="response"]',
        "wait_timeout_ms": 120_000,
        "pre_auth_url": "https://x.com/i/grok",
    },
))

_register(ProviderConfig(
    id="grok-com",
    name="Grok (grok.com)",
    base_url="https://grok.com",
    auth_type=AuthType.BROWSER,
    api_format=ApiFormat.CUSTOM,
    is_free=True,
    rate_limit_rpm=5,
    browser_profile=_BRAVE_PROFILE,
    browser_executable=_BRAVE_PATH,
    headless=True,
    models=[
        ModelConfig(id="grok-3", name="Grok 3 (grok.com)", context_window=128_000, max_output=16_384),
        ModelConfig(id="grok-3-mini", name="Grok 3 Mini (grok.com)", context_window=128_000, max_output=16_384),
    ],
    extra={
        "input_selector": 'textarea, div[contenteditable="true"], input[type="text"]',
        "submit_selector": 'button[type="submit"], button[aria-label*="Send"], button[aria-label*="submit"]',
        "output_selector": 'div[class*="message"][class*="assistant"], div[class*="response"], div[data-role="assistant"]',
        "wait_selector": 'div[class*="message"][class*="assistant"], div[class*="response"]',
        "wait_timeout_ms": 120_000,
        "pre_auth_url": "https://grok.com",
    },
))

_register(ProviderConfig(
    id="kimi",
    name="Kimi",
    base_url="https://api.moonshot.cn/v1",
    env_key="KIMI_API_KEY",
    models=[
        ModelConfig(id="kimi-k2.5", name="Kimi K2.5", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.00, output=4.00)),
        ModelConfig(id="kimi-k2.5-thinking", name="Kimi K2.5 Thinking", context_window=128_000, max_output=16_384,
                    cost=ModelCost(input=1.00, output=4.00)),
        ModelConfig(id="kimi-latest", name="Kimi Latest", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.00, output=4.00)),
    ],
))

_register(ProviderConfig(
    id="qwen",
    name="Qwen",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    env_key="QWEN_API_KEY",
    models=[
        ModelConfig(id="qwen3-coder-plus", name="Qwen3 Coder Plus", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.50, output=2.00), supports_tools=True),
        ModelConfig(id="qwen3-max", name="Qwen3 Max", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.60, output=6.40), supports_tools=True),
        ModelConfig(id="qwen3-235b", name="Qwen3 235B", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=1.60, output=6.40), supports_tools=True),
    ],
))

_register(ProviderConfig(
    id="chutes",
    name="Chutes",
    base_url="https://api.chutes.ai/v1",
    env_key="CHUTES_API_KEY",
    models=[
        ModelConfig(id="deepseek-r1", name="DeepSeek R1 (Chutes)", context_window=64_000, max_output=8_192,
                    cost=ModelCost(input=0.55, output=2.19)),
        ModelConfig(id="llama-3.3-70b", name="Llama 3.3 70B (Chutes)", context_window=128_000, max_output=8_192,
                    cost=ModelCost(input=0.35, output=0.40)),
    ],
))


# ── Auto-load custom providers on module import ──────────────────────────────

load_custom_providers()
load_openai_compatible_from_env()




