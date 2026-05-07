"""HttpProviderAdapter — generic adapter driven by ProviderSpec (Phase 6 P2).

Replaces ~4800 LOC of provider boilerplate with declarative YAML specs.
Adapter uses aiohttp for async HTTP calls (never httpx).

Usage::
    from css.api_services.adapters import HttpProviderAdapter, get_adapter
    
    adapter = get_adapter("openai")
    async for chunk in await adapter.call_llm(
        model_id="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
    ):
        print(chunk.content)
"""

from typing import Any
from collections.abc import AsyncIterator
import logging
import os
import time
from aiohttp import ClientSession, ClientTimeout

from css.core.exceptions import ProviderRegistryError
from css.core.types.providers import ProviderSpec
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import BaseMessage, ModelMetadata, StreamChunk
from css.core.types.enums import ProviderType


logger = logging.getLogger(__name__)

# Module-level singleton cache
_adapters: dict[str, HttpProviderAdapter] = {}


class HttpProviderAdapter(BaseApiServiceClient):
    """Generic provider adapter driven by ProviderSpec.
    
    Implements BaseApiServiceClient interface using declarative YAML specs.
    Supports streaming and buffered responses via async generators.
    
    Attributes:
        spec: ProviderSpec with endpoint, auth, and model config
    """
    
    def __init__(self, provider_name: str, spec: ProviderSpec):
        """Initialize adapter with provider spec.
        
        Args:
            provider_name: Provider identifier (openai, anthropic, etc.)
            spec: ProviderSpec loaded from YAML or registry
        """
        # Map provider name to ProviderType enum
        provider_type = self._get_provider_type(provider_name)
        
        # Initialize base class with spec's base_url as default
        super().__init__(
            provider_id=provider_type,
            api_key=os.environ.get(spec.auth.api_key_env) if spec.auth.api_key_env else None,
            base_url=spec.base_url,
        )
        
        self.provider_name = provider_name
        self.spec = spec
    
    def _default_base_url(self) -> str:
        """Use spec's base_url as default."""
        return self.spec.base_url
    
    @staticmethod
    def _get_provider_type(provider_name: str) -> ProviderType:
        """Map provider name to ProviderType enum."""
        mapping = {
            "openai": ProviderType.OPENAI,
            "anthropic": ProviderType.ANTHROPIC,
            "gemini": ProviderType.GEMINI,
            "deepseek": ProviderType.DEEPSEEK,
            "groq": ProviderType.GROQ,
            "mistral": ProviderType.MISTRAL,
            "xai": ProviderType.XAI,
            "nvidia": ProviderType.NVIDIA,
            "openrouter": ProviderType.OPENROUTER,
            "cerebras": ProviderType.CEREBRAS,
            "together": ProviderType.TOGETHER,
            "github": ProviderType.GITHUB,
            "cloudflare": ProviderType.CLOUDFLARE,
            "fireworks": ProviderType.FIREWORKS,
            "opencode": ProviderType.OPENCODE,
            "cohere": ProviderType.COHERE,
            "perplexity": ProviderType.PERPLEXITY,
            "sambanova": ProviderType.SAMBANOVA,
            "deepinfra": ProviderType.DEEPINFRA,
            "ai21": ProviderType.AI21,
            "huggingface": ProviderType.HUGGINGFACE,
            "ollama": ProviderType.OLLAMA,
            "nscale": ProviderType.NSCALE,
            "lambda": ProviderType.LAMBDA,
        }
        return mapping.get(provider_name.lower(), ProviderType.OPENAI)
    
    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider with capability flags.
        
        Returns:
            List of ModelMetadata objects from spec.models
        """
        models = []
        for model_id in self.spec.models:
            model = ModelMetadata(
                id=model_id,
                provider=self.provider_id,
                display_name=model_id,
                streaming=self.spec.streaming,
                vision=self.spec.vision,
                tool_use=self.spec.tool_use,
            )
            models.append(model)
        return models
    
    async def call_llm(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Call LLM with streaming support.
        
        Args:
            model_id: Model identifier
            messages: List of BaseMessage objects
            tools: Optional tools for the LLM
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response (default from spec)
            system_prompt: Optional system message
            streaming: Whether to stream response
            **kwargs: Provider-specific options
        
        Yields:
            StreamChunk objects with content, stop_reason, and metadata
        
        Raises:
            ProviderRegistryError: If API call fails
        """
        if max_tokens is None:
            max_tokens = 4096
        
        session = self._get_session()
        if session is None or session.closed:
            timeout = ClientTimeout(total=self.timeout_seconds)
            session = ClientSession(timeout=timeout)
        
        # Build request payload based on provider type
        if self.spec.api_type == "openai_compatible":
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, streaming, **kwargs
            )
            headers = self._build_openai_headers()
        else:
            # Default to OpenAI-compatible format
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, streaming, **kwargs
            )
            headers = self._build_openai_headers()
        
        url = f"{self.base_url.rstrip('/')}{self.spec.completion_endpoint}"
        
        start = time.time()
        chunks_received = 0
        
        try:
            if streaming:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise ProviderRegistryError(
                            f"Provider {self.provider_name} returned {resp.status}: {error_text}"
                        )
                    
                    async for line in resp.content:
                        if not line:
                            continue
                        
                        line_text = line.decode().strip()
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]
                        
                        if line_text == "[DONE]":
                            break
                        
                        try:
                            import json
                            data = json.loads(line_text)
                            chunk = self._parse_openai_stream_chunk(data)
                            if chunk:
                                chunks_received += 1
                                yield chunk
                        except (json.JSONDecodeError, KeyError):
                            continue
            else:
                # Buffered response
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise ProviderRegistryError(
                            f"Provider {self.provider_name} returned {resp.status}: {error_text}"
                        )
                    
                    data = await resp.json()
                    result = self._parse_openai_response(data)
                    yield StreamChunk(
                        type="content_block_delta",
                        content=result["response"],
                        stop_reason=result.get("stop_reason", "stop"),
                        metadata={
                            "input_tokens": result.get("input_tokens", 0),
                            "output_tokens": result.get("output_tokens", 0),
                            "usage": {
                                "prompt_tokens": result.get("input_tokens", 0),
                                "completion_tokens": result.get("output_tokens", 0),
                            }
                        },
                    )
        
        except Exception as e:
            logger.error(f"Provider {self.provider_name} API call failed: {e}")
            raise ProviderRegistryError(
                f"Provider {self.provider_name} call failed: {e}"
            ) from e
        
        duration_ms = (time.time() - start) * 1000
        logger.debug(
            f"Provider {self.provider_name} completed in {duration_ms:.1f}ms, "
            f"chunks: {chunks_received}"
        )
    
    
    def _build_openai_payload(
        self,
        messages: list[BaseMessage],
        model_id: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs,
    ) -> dict:
        """Build OpenAI-compatible request payload."""
        # Convert BaseMessage objects to dict format if needed
        msg_list = []
        
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            if isinstance(msg, dict):
                msg_list.append(msg)
            else:
                # Assume it's a BaseMessage with role and content
                msg_list.append({
                    "role": getattr(msg, "role", "user"),
                    "content": getattr(msg, "content", str(msg)),
                })
        
        payload = {
            "model": model_id,
            "messages": msg_list,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        payload.update(kwargs)
        return payload
    
    def _build_openai_headers(self) -> dict:
        """Build OpenAI-compatible request headers."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            scheme = self.spec.auth.scheme or "Bearer"
            headers[self.spec.auth.header or "Authorization"] = f"{scheme} {self.api_key}"
        
        return headers
    
    
    def _parse_openai_stream_chunk(self, data: dict) -> StreamChunk | None:
        """Parse OpenAI-format streaming chunk."""
        try:
            if "choices" not in data or not data["choices"]:
                return None
            
            choice = data["choices"][0]
            if "delta" not in choice:
                return None
            
            delta = choice["delta"]
            content = delta.get("content", "")
            stop_reason = choice.get("finish_reason")
            
            return StreamChunk(
                type="content_block_delta",
                content=content if content else None,
                stop_reason=stop_reason,
                metadata={"usage": data.get("usage", {})},
            )
        except (KeyError, IndexError, TypeError):
            return None
    
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
