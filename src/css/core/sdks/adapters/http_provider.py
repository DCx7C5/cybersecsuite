"""HttpProviderAdapter — YAML-driven HTTP client adapter.

Supports OpenAI-compatible providers and proprietary APIs via ProviderSpec.
Follows the same adapter pattern as AnthropicNativeAdapter / OpenAINativeAdapter.
"""

import json
import os
from collections.abc import AsyncIterator
from typing import Any

from aiohttp import ClientSession, ClientTimeout

from css.core.logger import getLogger
from css.core.messages.types import LLMResponse, StreamChunk, Tool
from css.core.base.enums import ProviderType
from css.core.base.providers.spec import ProviderSpec

logger = getLogger(__name__)


class HttpProviderAdapter:
    """Generic HTTP adapter driven by ProviderSpec YAML.

    Handles OpenAI-compatible (chat/completions) and Anthropic-format
    (/messages) APIs. Proprietary provider translators extend the
    _parse_response / _parse_stream_chunk methods.
    """

    provider_id: str

    def __init__(
        self,
        provider_name: str,
        spec: ProviderSpec,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.provider_name = provider_name
        self.provider_id = self._map_provider_type(provider_name).value
        self.spec = spec
        self.api_key = api_key or os.environ.get(spec.auth.api_key_env) if spec.auth.api_key_env else None
        self.base_url = base_url or spec.base_url
        self.timeout_seconds: int = 60
        self._session: ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.timeout_seconds)
            self._session = ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_models(self) -> list[Any]:
        return [
            type("ModelInfo", (), {"id": mid})()
            for mid in self.spec.models
        ]

    def supports_feature(self, model: Any, feature: str) -> bool:
        supported: dict[str, bool] = {
            "streaming": self.spec.capabilities.streaming,
            "vision": self.spec.capabilities.vision,
            "tool_use": self.spec.capabilities.tool_use,
        }
        return supported.get(feature, False)

    def builtin_tools(self) -> list[Tool]:
        return []

    async def call_llm(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        if not streaming:
            response = await self.complete(
                model_id=model_id,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                **kwargs,
            )
            yield response
            return

        async for chunk in self.stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        ):
            yield chunk

    async def call_llm_buffered(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        return await self.complete(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def complete(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        api_type = self.spec.api_type
        max_tokens = max_tokens or 4096

        if api_type == "openai_compatible":
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=False, **kwargs
            )
            headers = self._build_openai_headers()
            url = f"{self.base_url.rstrip('/')}{self.spec.endpoints.completion}"
            data = await self._post(url, headers, payload)
            return self._parse_openai_response(data)
        elif api_type == "anthropic":
            payload = self._build_anthropic_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=False, **kwargs
            )
            headers = self._build_anthropic_headers()
            url = f"{self.base_url.rstrip('/')}/v1/messages"
            data = await self._post(url, headers, payload)
            return self._parse_anthropic_response(data)
        else:
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=False, **kwargs
            )
            headers = self._build_openai_headers()
            url = f"{self.base_url.rstrip('/')}{self.spec.endpoints.completion}"
            data = await self._post(url, headers, payload)
            return self._parse_openai_response(data)

    async def stream(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        api_type = self.spec.api_type
        max_tokens = max_tokens or 4096

        if api_type == "openai_compatible":
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=True, **kwargs
            )
            headers = self._build_openai_headers()
            url = f"{self.base_url.rstrip('/')}{self.spec.endpoints.completion}"
            async for chunk in self._stream_sse(url, headers, payload):
                yield chunk
        elif api_type == "anthropic":
            payload = self._build_anthropic_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=True, **kwargs
            )
            headers = self._build_anthropic_headers()
            url = f"{self.base_url.rstrip('/')}/v1/messages"
            async for chunk in self._stream_sse(url, headers, payload):
                yield chunk
        else:
            payload = self._build_openai_payload(
                messages, model_id, system_prompt, temperature, max_tokens, stream=True, **kwargs
            )
            headers = self._build_openai_headers()
            url = f"{self.base_url.rstrip('/')}{self.spec.endpoints.completion}"
            async for chunk in self._stream_sse(url, headers, payload):
                yield chunk

    async def _post(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        async with self.session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Provider {self.provider_name} returned {resp.status}: {error_text}")
            return await resp.json()

    async def _stream_sse(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        async with self.session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Provider {self.provider_name} returned {resp.status}: {error_text}")

            async for line in resp.content:
                if not line:
                    continue
                line_text = line.decode().strip()
                if not line_text.startswith("data: "):
                    continue
                line_text = line_text[6:]
                if line_text == "[DONE]":
                    break
                try:
                    data = json.loads(line_text)
                    chunk = self._parse_openai_stream_chunk(data)
                    if chunk:
                        yield chunk
                except (json.JSONDecodeError, KeyError):
                    continue

    def _build_openai_payload(
        self,
        messages: list[Any],
        model_id: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        msg_list: list[dict[str, str]] = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        for msg in messages:
            if isinstance(msg, dict):
                msg_list.append(msg)
            else:
                msg_list.append({
                    "role": getattr(msg, "role", "user"),
                    "content": getattr(msg, "content", str(msg)),
                })
        payload: dict[str, Any] = {
            "model": model_id,
            "messages": msg_list,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        payload.update(kwargs)
        return payload

    def _build_openai_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            scheme = self.spec.auth.scheme or "Bearer"
            header_name = self.spec.auth.header or "Authorization"
            headers[header_name] = f"{scheme} {self.api_key}"
        return headers

    def _build_anthropic_payload(
        self,
        messages: list[Any],
        model_id: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        formatted_messages: list[dict[str, str]] = []
        system = system_prompt
        for msg in messages:
            role = getattr(msg, "role", "user")
            if isinstance(role, str):
                role_str: str = role
            elif hasattr(role, "value"):
                role_str = role.value  # type: ignore[union-attr]
            else:
                role_str = "user"
            content = getattr(msg, "content", "") or ""
            if role_str == "system":
                system = (system or "") + content if content else system
            else:
                formatted_messages.append({"role": role_str, "content": content})
        payload: dict[str, Any] = {
            "model": model_id,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }
        if system:
            payload["system"] = [{"type": "text", "text": system}]
        payload.update(kwargs)
        return payload

    def _build_anthropic_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
        return headers

    def _parse_openai_stream_chunk(self, data: dict[str, Any]) -> StreamChunk | None:
        try:
            if "choices" not in data or not data["choices"]:
                return None
            choice = data["choices"][0]
            if "delta" not in choice:
                return None
            delta = choice["delta"]
            content: str | None = delta.get("content")
            stop_reason: str | None = choice.get("finish_reason")
            return StreamChunk(
                type="content_block_delta",
                content=content,
                stop_reason=stop_reason,
                metadata={"usage": data.get("usage", {})},
            )
        except (KeyError, IndexError, TypeError):
            return None

    def _parse_openai_response(self, data: dict[str, Any]) -> LLMResponse:
        try:
            choice = data["choices"][0]
            message = choice["message"]
            text = message.get("content", "") or ""
            stop_reason = choice.get("finish_reason", "stop")
            usage = data.get("usage", {})
        except (KeyError, IndexError):
            text = str(data)
            stop_reason = "parse_error"
            usage = {}
        return LLMResponse(text=text, stop_reason=stop_reason, usage=usage)

    def _parse_anthropic_response(self, data: dict[str, Any]) -> LLMResponse:
        text = ""
        for block in data.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                text += block.get("text", "")
        stop_reason = data.get("stop_reason", "stop") or "stop"
        usage: dict[str, Any] = {}
        if "usage" in data:
            u = data["usage"]
            usage = {
                "prompt_tokens": u.get("input_tokens", 0),
                "completion_tokens": u.get("output_tokens", 0),
            }
        return LLMResponse(text=text, stop_reason=stop_reason, usage=usage)

    @staticmethod
    def _map_provider_type(provider_name: str) -> ProviderType:
        mapping: dict[str, ProviderType] = {
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

