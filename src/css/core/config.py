"""Central configuration for the CSS framework.

Hierarchy (lowest → highest priority):
  1. Constants here (framework defaults)
  2. Module-level overrides (modules/__init__.py switches)
  3. Environment variables (CYBERSEC_*)
  4. Runtime config (db/session-scoped options via RuntimeOptionsManager)

Usage:
  from css.core.config import ProviderDefaults, MarketplaceConfig, SystemConfig

Note: db-driven settings live in src/css/core/settings/config.py (Settings model).
"""

import os

class ProviderDefaults:
    """Default settings shared across all LLM provider clients."""

    TIMEOUT_SECONDS: int = int(os.getenv("CSS_PROVIDER_TIMEOUT", "120"))
    MAX_RETRIES: int = int(os.getenv("CSS_PROVIDER_MAX_RETRIES", "3"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("CSS_PROVIDER_MAX_TOKENS", "4096"))
    DEFAULT_TEMPERATURE: float = float(os.getenv("CSS_PROVIDER_TEMPERATURE", "0.7"))


class MarketplaceConfig:
    """Defaults for the marketplace module."""

    CACHE_TTL_SECONDS: int = int(os.getenv("CSS_MARKETPLACE_CACHE_TTL", "300"))
    MAX_RESULTS: int = int(os.getenv("CSS_MARKETPLACE_MAX_RESULTS", "100"))
    PAGE_SIZE: int = int(os.getenv("CSS_MARKETPLACE_PAGE_SIZE", "20"))
    SEEDER_HTTP_TIMEOUT: int = int(os.getenv("CSS_MARKETPLACE_SEEDER_TIMEOUT", "30"))


class SystemConfig:
    """Top-level system configuration."""

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DB_HOST: str = os.getenv("CYBERSEC_DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("CYBERSEC_DB_PORT", "5432"))
    DB_USER: str = os.getenv("CYBERSEC_DB_USER", "cybersec")
    DB_PASSWORD: str = os.getenv("CYBERSEC_DB_PASSWORD", "")
    DB_NAME: str = os.getenv("CYBERSEC_DB_NAME", "cybersec")

    @classmethod
    def db_url(cls) -> str:
        """Build the Tortoise-compatible DB URL from env vars."""
        return (
            f"postgres://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def is_test(cls) -> bool:
        return cls.ENVIRONMENT == "test"

    @classmethod
    def is_production(cls) -> bool:
        return cls.ENVIRONMENT == "production"


# Module-level marketplace config exports for backward compatibility
MARKETPLACE_CACHE_TTL_SECONDS = MarketplaceConfig.CACHE_TTL_SECONDS
MARKETPLACE_MAX_RESULTS = MarketplaceConfig.MAX_RESULTS
MARKETPLACE_PAGE_SIZE = MarketplaceConfig.PAGE_SIZE
MARKETPLACE_SEEDER_HTTP_TIMEOUT = MarketplaceConfig.SEEDER_HTTP_TIMEOUT

