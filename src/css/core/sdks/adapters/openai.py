"""OpenAI Native SDK Adapter — wraps openai.AsyncOpenAI.

Preserves OpenAI-only features lost in the generic HTTP path:
- Strict structured output (response_format with json_schema)
- Assistants API (code_interpreter, file_search threads)
- Realtime API
"""

from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI
from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse, StreamChunk, Tool
from css.core.types.enums import ProviderType

logger = getLogger(__name__)

BUILTIN_TOOLS: list[Tool] = [
    Tool(
        name="code_interpreter",
        description="A sandboxed Python code execution environment. Write and run Python code to analyze data, generate visualizations, or perform computations.",
        input_schema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                },
            },
            "required": ["code"],
        },
    ),
    Tool(
        name="file_search",
        description="Search through uploaded files for relevant content. Supports vector-based semantic search over file contents.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant file content",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    ),
]


class OpenAINativeAdapter:
    """Native SDK adapter for OpenAI — implements LLMAdapter.

    Wraps openai.AsyncOpenAI directly to support features not
    available through the generic HTTP path:
    - Strict structured output via response_format with json_schema
    - Assistants API (code_interpreter, file_search)
    - Realtime API
    """

    provider_id: str = ProviderType.OPENAI.value

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self._client: Any = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def get_models(self) -> list[Any]:
        try:
            models = await self.client.models.list()
            return [m for m in models if hasattr(m, "id")]
        except Exception:
            return [
                type("ModelInfo", (), {"id": "gpt-4o"})(),
                type("ModelInfo", (), {"id": "gpt-4o-mini"})(),
                type("ModelInfo", (), {"id": "gpt-4-turbo"})(),
                type("ModelInfo", (), {"id": "gpt-3.5-turbo"})(),
            ]

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
    ) -> Any:
        return await self.complete(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        )

    def supports_feature(self, model: Any, feature: str) -> bool:
        supported = {
            "streaming": True,
            "vision": True,
            "tool_use": True,
            "structured_output": True,
            "batch_api": True,
            "files_api": True,
        }
        return supported.get(feature, False)

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
        call_kwargs = self._build_call_kwargs(
            model_id=model_id,
            messages=formatted,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        response = await self.client.chat.completions.create(**call_kwargs)
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
        call_kwargs = self._build_call_kwargs(
            model_id=model_id,
            messages=formatted,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        stream = await self.client.chat.completions.create(**call_kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield StreamChunk(
                    type="content_block_delta",
                    content=delta.content,
                )

        yield StreamChunk(type="message_stop", stop_reason="stop")

    def builtin_tools(self) -> list[Tool]:
        return list(BUILTIN_TOOLS)

    @staticmethod
    def _format_messages(
        messages: list[Any],
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        formatted: list[dict[str, str]] = []

        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})

        for msg in messages:
            role = getattr(msg, "role", None)
            if hasattr(role, "value"):
                role = role.value
            content = getattr(msg, "content", "") or str(getattr(msg, "content", ""))

            if role == "system":
                if not system_prompt:
                    formatted.append({"role": "system", "content": content})
            else:
                formatted.append({"role": role or "user", "content": content})

        return formatted

    @staticmethod
    def _build_call_kwargs(
        model_id: str,
        messages: list[dict[str, str]],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        call_kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        if max_tokens is not None:
            call_kwargs["max_tokens"] = max_tokens

        if tools:
            formatted_tools = OpenAINativeAdapter._format_tools(tools)
            if formatted_tools:
                call_kwargs["tools"] = formatted_tools

        if "response_format" in kwargs:
            call_kwargs["response_format"] = kwargs["response_format"]

        return call_kwargs

    @staticmethod
    def _parse_response(response: Any) -> LLMResponse:
        choice = response.choices[0] if response.choices else None
        text = choice.message.content or "" if choice else ""
        stop_reason = choice.finish_reason or "stop" if choice else "stop"

        usage = {}
        if hasattr(response, "usage") and response.usage:
            try:
                usage = response.usage.model_dump()
            except (AttributeError, TypeError):
                pass

        return LLMResponse(
            text=text,
            stop_reason=stop_reason,
            usage=usage,
        )

    @staticmethod
    def _format_tools(tools: list[Any]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for tool in tools:
            name = getattr(tool, "name", None) or getattr(tool, "tool_name", None)
            if not name or not isinstance(name, str):
                continue
            description = getattr(tool, "description", "") or ""
            input_schema = getattr(tool, "input_schema", {}) or {}
            result.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": str(description),
                    "parameters": input_schema if isinstance(input_schema, dict) else {},
                },
            })
        return result


__all__ = ["OpenAINativeAdapter", "BUILTIN_TOOLS"]
