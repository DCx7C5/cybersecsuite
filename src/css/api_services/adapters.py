"""HttpProviderAdapter — generic adapter driven by ProviderSpec (Phase 6 P2).

Replaces ~4800 LOC of provider boilerplate with declarative YAML specs.
Adapter uses aiohttp for async HTTP calls (never httpx).

Usage::
    from css.api_services.adapters import HttpProviderAdapter, get_adapter
    
    adapter = get_adapter("openai")
    result = await adapter.complete(prompt="Hello", model="gpt-4")
"""

from typing import Any
import logging
from aiohttp import ClientSession, ClientTimeout

from css.core.exceptions import ProviderRegistryError
from css.core.types.providers import ProviderSpec


logger = logging.getLogger(__name__)

# Module-level singleton cache
_adapters: dict[str, HttpProviderAdapter] = {}


class HttpProviderAdapter:
    """Generic provider adapter driven by ProviderSpec.
    
    Attributes:
        provider_name: Provider identifier (openai, anthropic, etc.)
        spec: ProviderSpec with endpoint, auth, and model config
        session: Shared aiohttp ClientSession
    """
    
    def __init__(self, provider_name: str, spec: ProviderSpec):
        """Initialize adapter with provider spec.
        
        Args:
            provider_name: Provider identifier
            spec: ProviderSpec loaded from YAML or registry
        """
        self.provider_name = provider_name
        self.spec = spec
        self._session: ClientSession | None = None
    
    async def _get_session(self) -> ClientSession:
        """Lazily initialize aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=60)
            self._session = ClientSession(timeout=timeout)
        return self._session
    
    async def complete(
        self,
        prompt: str,
        model: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Complete a prompt via the provider's API.
        
        Args:
            prompt: User prompt text
            model: Model identifier (gpt-4, claude-3-opus, etc.)
            system: Optional system message
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            **kwargs: Provider-specific options
        
        Returns:
            Dict with keys: response, input_tokens, output_tokens, 
            stop_reason, duration_ms
        
        Raises:
            ProviderRegistryError: If API call fails
        """
        import time
        
        session = await self._get_session()
        
        # Build request payload based on provider type
        if self.spec.api_type == "openai_compatible":
            payload = self._build_openai_payload(
                prompt, model, system, temperature, max_tokens, stream, **kwargs
            )
            headers = self._build_openai_headers()
        else:
            # Default to OpenAI-compatible format
            payload = self._build_openai_payload(
                prompt, model, system, temperature, max_tokens, stream, **kwargs
            )
            headers = self._build_openai_headers()
        
        url = f"{self.spec.base_url.rstrip('/')}/{self.spec.completion_endpoint.lstrip('/')}"
        
        start = time.time()
        
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise ProviderRegistryError(
                        f"Provider {self.provider_name} returned {resp.status}: {error_text}"
                    )
                
                data = await resp.json()
        
        except Exception as e:
            logger.error(f"Provider {self.provider_name} API call failed: {e}")
            raise ProviderRegistryError(
                f"Provider {self.provider_name} call failed: {e}"
            ) from e
        
        duration_ms = (time.time() - start) * 1000
        
        # Parse response (OpenAI format)
        result = self._parse_openai_response(data)
        result["duration_ms"] = duration_ms
        result["provider"] = self.provider_name
        result["model"] = model
        
        return result
    
    def _build_openai_payload(
        self,
        prompt: str,
        model: str,
        system: str | None,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs,
    ) -> dict:
        """Build OpenAI-compatible request payload."""
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        payload.update(kwargs)
        return payload
    
    def _build_openai_headers(self) -> dict:
        """Build OpenAI-compatible request headers."""
        headers = {"Content-Type": "application/json"}
        
        if self.spec.api_key_env:
            import os
            api_key = os.environ.get(self.spec.api_key_env)
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    def _parse_openai_response(self, data: dict) -> dict:
        """Parse OpenAI-format response."""
        try:
            choice = data["choices"][0]
            message = choice["message"]
            
            return {
                "response": message.get("content", ""),
                "stop_reason": choice.get("finish_reason", "unknown"),
                "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": data.get("usage", {}).get("completion_tokens", 0),
            }
        except (KeyError, IndexError) as e:
            logger.warning(f"Failed to parse provider response: {e}")
            return {
                "response": str(data),
                "stop_reason": "parse_error",
                "input_tokens": 0,
                "output_tokens": 0,
            }
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


def get_adapter(provider_name: str, spec: ProviderSpec | None = None) -> HttpProviderAdapter:
    """Get or create HttpProviderAdapter for provider.
    
    Args:
        provider_name: Provider identifier
        spec: Optional ProviderSpec (loads from registry if None)
    
    Returns:
        HttpProviderAdapter instance
    """
    if provider_name not in _adapters:
        if spec is None:
            # Load from ProviderRegistry
            from css.api_services.registry import ProviderRegistry
            registry = ProviderRegistry()
            spec = registry.get_spec(provider_name)
            if spec is None:
                raise ProviderRegistryError(
                    f"Provider {provider_name} not found in registry"
                )
        
        _adapters[provider_name] = HttpProviderAdapter(provider_name, spec)
    
    return _adapters[provider_name]


async def close_all_adapters() -> None:
    """Close all cached adapter sessions."""
    for name, adapter in _adapters.items():
        await adapter.close()
    _adapters.clear()


__all__ = ["HttpProviderAdapter", "get_adapter", "close_all_adapters", "ProviderSpec"]
