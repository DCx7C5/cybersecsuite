"""Browser relay adapter backed by the local browser-plugin request store."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from css.core.messages.types import LLMResponse, StreamChunk
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
        relay_provider_id_obj = kwargs.get("relay_provider_id")
        relay_provider_id = (
            relay_provider_id_obj.strip()
            if isinstance(relay_provider_id_obj, str) and relay_provider_id_obj.strip()
            else self.provider_id
        )
        metadata_obj = kwargs.get("metadata")
        metadata: dict[str, str] = {}
        if isinstance(metadata_obj, dict):
            for key_obj, value_obj in metadata_obj.items():
                if isinstance(key_obj, str) and isinstance(value_obj, str):
                    metadata[key_obj] = value_obj
        metadata["relay_provider_id"] = relay_provider_id

        record = await self._session_store.submit_injection(
            session_id=session_id,
            prompt=prompt,
            provider=relay_provider_id,
            model=model_id or _DEFAULT_BROWSER_RELAY_MODEL,
            request_id=request_id if isinstance(request_id, str) else None,
            ttl_seconds=ttl_seconds if isinstance(ttl_seconds, int) else None,
            metadata=metadata,
        )

        poll_interval_obj = kwargs.get("poll_interval_seconds")
        poll_timeout_obj = kwargs.get("poll_timeout_seconds")
        cancel_event_obj = kwargs.get("cancel_event")

        poll_interval = (
            float(poll_interval_obj)
            if isinstance(poll_interval_obj, (int, float)) and float(poll_interval_obj) > 0
            else 1.0
        )
        poll_timeout = (
            float(poll_timeout_obj)
            if isinstance(poll_timeout_obj, (int, float)) and float(poll_timeout_obj) > 0
            else 30.0
        )
        cancel_event = cancel_event_obj if isinstance(cancel_event_obj, asyncio.Event) else None
        deadline = asyncio.get_running_loop().time() + poll_timeout

        while True:
            if cancel_event is not None and cancel_event.is_set():
                return LLMResponse(
                    text="",
                    stop_reason="relay_cancelled",
                    usage=self._relay_usage(record["request_id"], session_id, model_id, record["provider"]),
                )

            result_record = await self._session_store.get_result(
                session_id=session_id,
                request_id=record["request_id"],
            )
            if result_record is None:
                return LLMResponse(
                    text="",
                    stop_reason="relay_unknown_request",
                    usage=self._relay_usage(record["request_id"], session_id, model_id, record["provider"]),
                )

            if (
                result_record["status"] == "completed"
                and result_record["result"] is not None
            ):
                result = result_record["result"]
                usage: dict[str, Any] = dict(result["usage"])
                usage["request_id"] = record["request_id"]
                usage["session_id"] = session_id
                usage["provider"] = record["provider"]
                usage["model"] = model_id or _DEFAULT_BROWSER_RELAY_MODEL
                return LLMResponse(
                    text=result["content"],
                    stop_reason=result["stop_reason"],
                    usage=usage,
                )

            if (
                result_record["status"] == "failed"
                and result_record["result"] is not None
            ):
                result = result_record["result"]
                usage = self._relay_usage(record["request_id"], session_id, model_id, record["provider"])
                if result["error_code"] is not None:
                    usage["error_code"] = result["error_code"]
                if result["error_message"] is not None:
                    usage["error_message"] = result["error_message"]
                return LLMResponse(
                    text=result["content"],
                    stop_reason=result["error_code"] or "relay_failed",
                    usage=usage,
                )

            if result_record["status"] == "expired":
                return LLMResponse(
                    text="",
                    stop_reason="relay_timeout",
                    usage=self._relay_usage(record["request_id"], session_id, model_id, record["provider"]),
                )

            if asyncio.get_running_loop().time() >= deadline:
                return LLMResponse(
                    text="",
                    stop_reason="relay_timeout",
                    usage=self._relay_usage(record["request_id"], session_id, model_id, record["provider"]),
                )
            await asyncio.sleep(poll_interval)

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

    def _relay_usage(
        self,
        request_id: str,
        session_id: str,
        model_id: str,
        provider_id: str,
    ) -> dict[str, Any]:
        return {
            "request_id": request_id,
            "session_id": session_id,
            "provider": provider_id,
            "model": model_id or _DEFAULT_BROWSER_RELAY_MODEL,
        }

