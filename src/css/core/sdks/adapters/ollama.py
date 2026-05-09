"""OllamaAdapter — local HTTP client for Ollama.

Manages Ollama model lifecycle: list, pull, delete, generate, chat.
Connects to local Ollama server via ollama.AsyncClient.
"""

from collections.abc import AsyncIterator
from typing import Any

from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse, StreamChunk, Tool
from css.core.types.enums import ProviderType

logger = getLogger(__name__)


class OllamaAdapter:
    """Local adapter for Ollama — wraps ollama.AsyncClient.

    Supports:
    - Chat completion (streaming + buffered)
    - Model management (list, pull, delete)
    - All Ollama-supported model architectures
    """

    provider_id: str = ProviderType.OLLAMA.value

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url or "http://localhost:11434"
        self._client: Any = None

    @property
    def client(self) -> Any:
        if self._client is None:
            try:
                from ollama import AsyncClient
            except ImportError:
                raise ImportError("ollama package required: pip install ollama")
            self._client = AsyncClient(host=self.base_url)
        return self._client

    async def get_models(self) -> list[Any]:
        try:
            resp = await self.client.list()
            return resp.get("models", [])
        except Exception:
            return [
                type("ModelInfo", (), {"id": "qwen3:0.6b"})(),
                type("ModelInfo", (), {"id": "phi4-mini:3.8b-q4_K_M"})(),
                type("ModelInfo", (), {"id": "qwen3:4b-q4_K_M"})(),
            ]

    def supports_feature(self, model: Any, feature: str) -> bool:
        supported: dict[str, bool] = {
            "streaming": True,
            "vision": True,
            "tool_use": False,
            "structured_output": False,
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
        formatted = self._format_messages(messages, system_prompt)
        options = self._build_options(temperature, max_tokens, **kwargs)

        response = await self.client.chat(
            model=model_id,
            messages=formatted,
            stream=False,
            options=options,
        )
        return self._parse_response(response)

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
        formatted = self._format_messages(messages, system_prompt)
        options = self._build_options(temperature, max_tokens, **kwargs)

        async for part in await self.client.chat(
            model=model_id,
            messages=formatted,
            stream=True,
            options=options,
        ):
            if part.get("done"):
                yield StreamChunk(
                    type="message_stop",
                    stop_reason="stop",
                    metadata={"usage": part.get("eval_count", 0)},
                )
                return
            content = part.get("message", {}).get("content", "")
            if content:
                yield StreamChunk(
                    type="content_block_delta",
                    content=content,
                )

    async def pull_model(self, model_name: str) -> dict[str, Any]:
        return await self.client.pull(model=model_name)

    async def list_local_models(self) -> list[dict[str, Any]]:
        return await self.client.list()

    async def delete_model(self, model_name: str) -> dict[str, Any]:
        return await self.client.delete(model=model_name)

    def _format_messages(
        self,
        messages: list[Any],
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        formatted: list[dict[str, str]] = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            role = getattr(msg, "role", "user")
            if isinstance(role, str):
                role_str: str = role
            elif hasattr(role, "value"):
                role_str = role.value  # type: ignore[union-attr]
            else:
                role_str = "user"
            content = getattr(msg, "content", "") or ""
            formatted.append({"role": role_str, "content": content})
        return formatted

    def _build_options(
        self,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        options.update(kwargs)
        return options

    def _parse_response(self, response: Any) -> LLMResponse:
        if isinstance(response, dict):
            message = response.get("message", {})
            text = message.get("content", "") if isinstance(message, dict) else ""
            stop_reason = "stop"
            eval_count = response.get("eval_count", 0)
            usage = {"completion_tokens": eval_count}
            return LLMResponse(text=text, stop_reason=stop_reason, usage=usage)
        return LLMResponse(text=str(response), stop_reason="stop")


__all__ = ["OllamaAdapter"]
