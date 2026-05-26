"""Browser relay adapter backed by the local browser-plugin request store."""

from collections.abc import AsyncIterator
from typing import Any

from css.core.types.base_messages import LLMResponse, StreamChunk
from css.modules.llm_proxy.browser_plugin import get_browser_plugin_session_store

_BROWSER_RELAY_PROVIDER = "browser-relay"
_DEFAULT_BROWSER_RELAY_MODEL = "browser-relay/default"


class BrowserRelayAdapter:
    """Adapter for extension-backed browser relay execution."""

    provider_id: str = _BROWSER_RELAY_PROVIDER
    api_key: str | None = None
    base_url: str | None = None

    def __init__(self) -> None:
        self._session_store = get_browser_plugin_session_store()

    async def get_models(self) -> list[Any]:
        return [
            type("ModelInfo", (), {"id": _DEFAULT_BROWSER_RELAY_MODEL})(),
        ]

    def supports_feature(self, model: Any, feature: str) -> bool:
        supported = {
            "streaming": False,
            "vision": True,
            "tool_use": False,
        }
        return supported.get(feature, False)

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
        if streaming:
            raise NotImplementedError(
                "Browser relay streaming is not implemented yet; use buffered calls and polling endpoints"
            )

        response = await self.call_llm_buffered(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        )

        async def _single_response() -> AsyncIterator[StreamChunk]:
            if response.text:
                yield StreamChunk(
                    type="content_block_delta",
                    content=response.text,
                    metadata={"usage": response.usage},
                )
            yield StreamChunk(
                type="message_stop",
                stop_reason=response.stop_reason,
                metadata={"usage": response.usage},
            )

        return _single_response()

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
        session_id_obj = kwargs.get("browser_plugin_session_id", kwargs.get("session_id"))
        if not isinstance(session_id_obj, str) or not session_id_obj.strip():
            raise ValueError("browser_plugin_session_id is required for browser-relay calls")
        session_id = session_id_obj.strip()

        prompt = self._extract_prompt(messages)
        if not prompt:
            raise ValueError("no user prompt found for browser-relay call")

        request_id = kwargs.get("request_id")
        ttl_seconds = kwargs.get("request_ttl_seconds")
        metadata_obj = kwargs.get("metadata")
        metadata = metadata_obj if isinstance(metadata_obj, dict) else None

        record = await self._session_store.submit_injection(
            session_id=session_id,
            prompt=prompt,
            provider=self.provider_id,
            model=model_id or _DEFAULT_BROWSER_RELAY_MODEL,
            request_id=request_id if isinstance(request_id, str) else None,
            ttl_seconds=ttl_seconds if isinstance(ttl_seconds, int) else None,
            metadata=metadata,
        )

        result_record = await self._session_store.fetch_result(
            session_id=session_id,
            request_id=record["request_id"],
        )
        if (
            result_record is not None
            and result_record["status"] == "completed"
            and result_record["result"] is not None
        ):
            result = result_record["result"]
            return LLMResponse(
                text=result["content"],
                stop_reason=result["stop_reason"],
                usage=result["usage"],
            )

        return LLMResponse(
            text="",
            stop_reason="relay_pending",
            usage={
                "request_id": record["request_id"],
                "session_id": session_id,
                "provider": self.provider_id,
                "model": model_id or _DEFAULT_BROWSER_RELAY_MODEL,
            },
        )

    @staticmethod
    def _extract_prompt(messages: list[Any]) -> str:
        for message in reversed(messages):
            if isinstance(message, dict):
                role = message.get("role")
                if role != "user":
                    continue
                content = message.get("content", "")
                if isinstance(content, str):
                    return content.strip()
                if isinstance(content, list):
                    chunks: list[str] = []
                    for chunk in content:
                        if isinstance(chunk, dict):
                            text = chunk.get("text")
                            if isinstance(text, str) and text.strip():
                                chunks.append(text.strip())
                    return " ".join(chunks)

            role = getattr(message, "role", None)
            if role != "user" and getattr(role, "value", None) != "user":
                continue
            content = getattr(message, "content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()
        return ""


__all__ = ["BrowserRelayAdapter"]
