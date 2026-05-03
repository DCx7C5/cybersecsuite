"""Base provider classes for API and Local LLM providers."""

from typing import Optional


from ..base import BaseApiServiceClient, ErrorStrategy, ProviderType


class RateLimitConfig:
    """Rate limiting configuration for providers."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 90000,
    ):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute


class AuthRefreshStrategy:
    """Strategy for refreshing authentication tokens."""

    def __init__(self, auto_refresh: bool = False, refresh_before_expiry: int = 60):
        self.auto_refresh = auto_refresh
        self.refresh_before_expiry = refresh_before_expiry


class APIProviderBase(BaseApiServiceClient):
    """Base class for cloud-based API providers (OpenAI, Anthropic, etc.)."""

    def __init__(
        self,
        provider_id: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
        error_strategy: ErrorStrategy = ErrorStrategy.LOG,
        rate_limit_config: Optional[RateLimitConfig] = None,
        auth_refresh: Optional[AuthRefreshStrategy] = None,
    ):
        super().__init__(
            provider_id=provider_id,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self.error_strategy = error_strategy
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.auth_refresh = auth_refresh or AuthRefreshStrategy()
        self._last_request_time: float = 0.0

    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        import time
        import asyncio

        current_time = time.time()
        elapsed = current_time - self._last_request_time

        if self.rate_limit_config.requests_per_minute > 0:
            min_interval = 60 / self.rate_limit_config.requests_per_minute
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

        self._last_request_time = time.time()

    async def _refresh_auth(self) -> None:
        """Refresh authentication token if needed. Override in subclass."""
        if self.auth_refresh.auto_refresh:
            # Subclass should override this to implement actual refresh logic
            pass

    def _default_base_url(self) -> str:
        """Override in provider subclass."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _default_base_url()"
        )


class LocalProviderBase(BaseApiServiceClient):
    """Base class for local LLM providers (Ollama, local Llama.cpp, etc.)."""

    def __init__(
        self,
        provider_id: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
        local_model_path: Optional[str] = None,
        check_binary_on_init: bool = True,
    ):
        super().__init__(
            provider_id=provider_id,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self.local_model_path = local_model_path
        self.check_binary_on_init = check_binary_on_init
        self._binary_available = False

        if self.check_binary_on_init:
            self._verify_binary_available()

    def _verify_binary_available(self) -> None:
        """Check if local binary/service is available."""
        import shutil
        import os

        # Check if binary is in PATH or at specified path
        if self.local_model_path:
            self._binary_available = os.path.exists(self.local_model_path)
        else:
            # Try to find common binary names
            binary_name = self._get_binary_name()
            self._binary_available = shutil.which(binary_name) is not None

    def _get_binary_name(self) -> str:
        """Get the binary name to check for. Override in subclass."""
        return "ollama"  # Default for Ollama

    @property
    def binary_available(self) -> bool:
        """Check if local binary is available."""
        return self._binary_available

    def _default_base_url(self) -> str:
        """Default base URL for local providers."""
        return "http://localhost:11434"  # Ollama default


__all__ = [
    "RateLimitConfig",
    "AuthRefreshStrategy",
    "APIProviderBase",
    "LocalProviderBase",
]
