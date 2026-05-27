"""DeepSeek SDK adapter using the existing DeepSeek API service implementation."""

import os
from collections.abc import AsyncIterator
from typing import Any, override

from css.api_services.deepseek.service import DeepSeekApiService
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import BaseMessage
from css.core.messages.types import LLMResponse, ModelMetadata, StreamChunk, Tool
from css.core.types.base_enums import MessageRole, ProviderType

_DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


class DeepSeekAdapter(BaseApiServiceClient):
    """Adapter that normalizes DeepSeek reasoning output into SDK contracts."""

    provider_id: ProviderType = ProviderType.DEEPSEEK

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        resolved_api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        resolved_base_url = base_url or self._default_base_url()
        super().__init__(
            provider_id=ProviderType.DEEPSEEK,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self._service = DeepSeekApiService(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    @override
    def _default_base_url(self) -> str:
        return "https://api.deepseek.com/v1"

    async def close(self) -> None:
        service_session = getattr(self._service, "_session", None)
        if service_session is not None and not service_session.closed:
            await service_session.close()
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    @override
    async def get_models(self) -> list[ModelMetadata]:
        return await self._service.get_models()

    @override
    def supports_feature(self, model_metadata: ModelMetadata, feature: str) -> bool:
        return super().supports_feature(model_metadata, feature)

    @override
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
    ) -> AsyncIterator[StreamChunk]:
        normalized_messages = self._normalize_messages(messages)
        normalized_tools = self._normalize_tools(tools)
        return await self._service.call_llm(
            model_id=model_id or _DEFAULT_DEEPSEEK_MODEL,
            messages=normalized_messages,
            tools=normalized_tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            streaming=streaming,
            **kwargs,
        )

    @override
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
        stream = await self.call_llm(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            streaming=False,
            **kwargs,
        )
        chunks: list[str] = []
        reasoning_chunks: list[str] = []
        stop_reason = "stop"
        usage: dict[str, Any] = {}

        async for chunk in stream:
            if chunk.type == "content_block_delta" and chunk.content:
                if chunk.metadata.get("content_type") == "reasoning":
                    reasoning_chunks.append(chunk.content)
                    continue
                chunks.append(chunk.content)
                continue

            if chunk.type == "message_stop":
                stop_reason = chunk.stop_reason or "stop"
                usage_obj = chunk.metadata.get("usage")
                if isinstance(usage_obj, dict):
                    usage = dict(usage_obj)

        if reasoning_chunks and "reasoning" not in usage:
            usage["reasoning"] = "".join(reasoning_chunks)

        return LLMResponse(
            text="".join(chunks),
            stop_reason=stop_reason,
            usage=usage,
        )

    @staticmethod
    def _normalize_messages(messages: list[Any]) -> list[BaseMessage]:
        normalized: list[BaseMessage] = []
        for message in messages:
            if isinstance(message, BaseMessage):
                normalized.append(message)
                continue

            if isinstance(message, dict):
                role = DeepSeekAdapter._coerce_role(message.get("role"))
                content = DeepSeekAdapter._coerce_content(message.get("content", ""))
                normalized.append(BaseMessage(role=role, content=content))
                continue

            role = DeepSeekAdapter._coerce_role(getattr(message, "role", MessageRole.USER))
            content = DeepSeekAdapter._coerce_content(getattr(message, "content", ""))
            normalized.append(BaseMessage(role=role, content=content))
        return normalized

    @staticmethod
    def _normalize_tools(tools: list[Any] | None) -> list[Tool] | None:
        if not tools:
            return None

        normalized: list[Tool] = []
        for tool in tools:
            if isinstance(tool, Tool):
                normalized.append(tool)
                continue

            if isinstance(tool, dict):
                function_obj = tool.get("function")
                if isinstance(function_obj, dict):
                    normalized.append(
                        Tool(
                            name=str(function_obj.get("name", "")),
                            description=str(function_obj.get("description", "")),
                            input_schema=function_obj.get("parameters", {}) if isinstance(function_obj.get("parameters"), dict) else {},
                        )
                    )
                    continue

                input_schema_obj = tool.get("input_schema")
                normalized.append(
                    Tool(
                        name=str(tool.get("name", "")),
                        description=str(tool.get("description", "")),
                        input_schema=input_schema_obj if isinstance(input_schema_obj, dict) else {},
                    )
                )
                continue

            normalized.append(
                Tool(
                    name=str(getattr(tool, "name", "")),
                    description=str(getattr(tool, "description", "")),
                    input_schema=getattr(tool, "input_schema", {}) if isinstance(getattr(tool, "input_schema", {}), dict) else {},
                )
            )

        return normalized

    @staticmethod
    def _coerce_role(role_obj: Any) -> MessageRole:
        if isinstance(role_obj, MessageRole):
            return role_obj

        if hasattr(role_obj, "value"):
            value_obj = getattr(role_obj, "value")
            if isinstance(value_obj, str):
                role_str = value_obj.strip().lower()
            else:
                role_str = "user"
        elif isinstance(role_obj, str):
            role_str = role_obj.strip().lower()
        else:
            role_str = "user"

        if role_str == MessageRole.ASSISTANT.value:
            return MessageRole.ASSISTANT
        if role_str == MessageRole.SYSTEM.value:
            return MessageRole.SYSTEM
        return MessageRole.USER

    @staticmethod
    def _coerce_content(content_obj: Any) -> str:
        if isinstance(content_obj, str):
            return content_obj
        if isinstance(content_obj, list):
            chunks: list[str] = []
            for chunk in content_obj:
                if isinstance(chunk, dict):
                    text = chunk.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
                    continue
                if isinstance(chunk, str):
                    chunks.append(chunk)
            return " ".join(chunks).strip()
        return str(content_obj)


__all__ = ["DeepSeekAdapter"]
