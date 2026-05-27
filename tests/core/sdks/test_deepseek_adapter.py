from collections.abc import AsyncIterator
from typing import Any

import pytest

from css.core.sdks import CSSLLMClient, SDKRegistry
from css.core.sdks.adapters.deepseek import DeepSeekAdapter
from css.core.types.base_messages import BaseMessage
from css.core.messages.types import StreamChunk
from css.core.types.base_enums import MessageRole


@pytest.mark.asyncio
async def test_deepseek_adapter_buffered_reasoning_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = DeepSeekAdapter(api_key="test-key")

    async def _fake_call_llm(
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        assert model_id == "deepseek-chat"
        assert streaming is False
        assert len(messages) == 1
        assert messages[0].role == MessageRole.USER
        assert messages[0].content == "hello"
        assert tools is None
        assert temperature == 0.7
        assert max_tokens is None
        assert system_prompt is None
        assert kwargs == {}

        async def _stream() -> AsyncIterator[StreamChunk]:
            yield StreamChunk(
                type="content_block_delta",
                content="answer body",
            )
            yield StreamChunk(
                type="message_stop",
                stop_reason="stop",
                metadata={"usage": {"prompt_tokens": 11, "completion_tokens": 6, "reasoning": "r1-trace"}},
            )

        return _stream()

    monkeypatch.setattr(adapter._service, "call_llm", _fake_call_llm)
    response = await adapter.call_llm_buffered(
        model_id="deepseek-chat",
        messages=[{"role": "user", "content": "hello"}],
    )
    assert response.text == "answer body"
    assert response.stop_reason == "stop"
    assert response.usage["prompt_tokens"] == 11
    assert response.usage["completion_tokens"] == 6
    assert response.usage["reasoning"] == "r1-trace"


@pytest.mark.asyncio
async def test_deepseek_adapter_streaming_reasoning_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = DeepSeekAdapter(api_key="test-key")

    async def _fake_call_llm(
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        assert model_id == "deepseek-chat"
        assert streaming is True
        assert len(messages) == 1
        assert messages[0].role == MessageRole.USER
        assert messages[0].content == "stream this"
        assert tools is None
        assert temperature == 0.7
        assert max_tokens is None
        assert system_prompt is None
        assert kwargs == {}

        async def _stream() -> AsyncIterator[StreamChunk]:
            yield StreamChunk(
                type="content_block_delta",
                content="think",
                metadata={"content_type": "reasoning"},
            )
            yield StreamChunk(
                type="content_block_delta",
                content="final",
            )
            yield StreamChunk(
                type="message_stop",
                stop_reason="stop",
                metadata={"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
            )

        return _stream()

    monkeypatch.setattr(adapter._service, "call_llm", _fake_call_llm)
    stream = await adapter.call_llm(
        model_id="deepseek-chat",
        messages=[{"role": "user", "content": "stream this"}],
        streaming=True,
    )
    chunks = [chunk async for chunk in stream]
    assert len(chunks) == 3
    assert chunks[0].metadata["content_type"] == "reasoning"
    assert chunks[1].content == "final"
    assert chunks[2].type == "message_stop"
    assert chunks[2].metadata["usage"]["completion_tokens"] == 5


@pytest.mark.asyncio
async def test_deepseek_registry_and_css_client_lookup() -> None:
    registry = SDKRegistry()
    registry.clear_cache("deepseek")
    registry.register("deepseek", DeepSeekAdapter)
    deepseek_adapter = await registry.get("deepseek")
    assert isinstance(deepseek_adapter, DeepSeekAdapter)

    client = CSSLLMClient()
    resolved = await client.get_sdk("deepseek-ai")
    assert isinstance(resolved, DeepSeekAdapter)
