"""
Provider Registry — Pydantic-validated provider configurations.

Each provider has a base URL,
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
    BEDROCK = "bedrock"    # AWS Bedrock via AnthropicBedrock SDK
    VERTEX = "vertex"      # Google Vertex AI via AnthropicVertex SDK
    FOUNDRY = "foundry"    # Microsoft Azure AI Foundry via AsyncAnthropicFoundry
    CUSTOM = "custom"      # Custom format requiring a dedicated executor


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


# ── Built-in provider registrations ─────────────────────────────────────────
import ai_proxy.providers._providers  # noqa: F401,E402  # side-effect: registers all built-ins

# ── Auto-load custom providers on module import ──────────────────────────────

load_custom_providers()
load_openai_compatible_from_env()




