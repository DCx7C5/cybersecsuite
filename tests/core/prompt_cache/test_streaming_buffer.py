import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from css.core.prompt_cache.exact_match_cache import ExactMatchPromptCache
from css.core.prompt_cache.manager import PromptCacheManager
from css.core.prompt_cache.streaming_buffer import PromptCacheStreamingBuffer
from css.core.prompt_cache.types import CachingCapability
from css.core.types.base_messages import LLMResponse, StreamChunk


class _DummyAdapter:
    @property
    def cache_capability(self) -> CachingCapability:
        return CachingCapability.EXACT_ONLY


class _FakeExactCache:
    def __init__(self, preloaded: LLMResponse | None = None) -> None:
        self.preloaded = preloaded
        self.saved_key: str | None = None
        self.saved_response: LLMResponse | None = None
        self.set_calls = 0

    async def get(self, cache_key: str) -> LLMResponse | None:
        if self.preloaded is None:
            return None
        if cache_key != "cache-key":
            return None
        return self.preloaded

    async def set(self, cache_key: str, response: LLMResponse) -> bool:
        self.saved_key = cache_key
        self.saved_response = response
        self.set_calls += 1
        return True


def _provider_stream_complete() -> AsyncIterator[StreamChunk]:
    async def _iterator() -> AsyncIterator[StreamChunk]:
        yield StreamChunk(
            type="content_block_delta",
            content="answer ",
            metadata={"tool_call": {"name": "search"}},
        )
        yield StreamChunk(
            type="content_block_delta",
            content="ready",
        )
        yield StreamChunk(
            type="message_stop",
            stop_reason="stop",
            metadata={"usage": {"input_tokens": 11, "output_tokens": 5}},
        )

    return _iterator()


def _provider_stream_error() -> AsyncIterator[StreamChunk]:
    async def _iterator() -> AsyncIterator[StreamChunk]:
        yield StreamChunk(type="content_block_delta", content="partial")
        raise RuntimeError("provider error")

    return _iterator()


def _provider_stream_cancelled() -> AsyncIterator[StreamChunk]:
    async def _iterator() -> AsyncIterator[StreamChunk]:
        yield StreamChunk(type="content_block_delta", content="partial")
        raise asyncio.CancelledError()

    return _iterator()


@pytest.mark.asyncio
async def test_stream_and_yield_buffers_and_stores_completed_stream() -> None:
    cache = _FakeExactCache()
    pipeline = PromptCacheStreamingBuffer(exact_match_cache=cache)

    forwarded = [
        chunk
        async for chunk in pipeline.stream_and_yield(
            _provider_stream_complete(),
            cache_key="cache-key",
            store_in_cache=True,
        )
    ]

    assert [chunk.type for chunk in forwarded] == [
        "content_block_delta",
        "content_block_delta",
        "message_stop",
    ]
    assert cache.saved_key == "cache-key"
    assert cache.saved_response is not None
    assert cache.saved_response.text == "answer ready"
    assert cache.saved_response.stop_reason == "stop"
    assert cache.saved_response.usage["input_tokens"] == 11
    assert cache.saved_response.usage["output_tokens"] == 5
    assert cache.saved_response.usage["stream_metadata"]["tool_call"]["name"] == "search"


@pytest.mark.asyncio
async def test_stream_and_yield_no_store_on_provider_error() -> None:
    cache = _FakeExactCache()
    pipeline = PromptCacheStreamingBuffer(exact_match_cache=cache)

    with pytest.raises(RuntimeError, match="provider error"):
        _ = [chunk async for chunk in pipeline.stream_and_yield(_provider_stream_error(), cache_key="cache-key")]

    assert cache.set_calls == 0


@pytest.mark.asyncio
async def test_stream_and_yield_no_store_on_cancellation() -> None:
    cache = _FakeExactCache()
    pipeline = PromptCacheStreamingBuffer(exact_match_cache=cache)

    with pytest.raises(asyncio.CancelledError):
        _ = [
            chunk
            async for chunk in pipeline.stream_and_yield(
                _provider_stream_cancelled(),
                cache_key="cache-key",
            )
        ]

    assert cache.set_calls == 0


@pytest.mark.asyncio
async def test_stream_and_buffer_preserves_usage_and_tool_metadata() -> None:
    cache = _FakeExactCache()
    pipeline = PromptCacheStreamingBuffer(exact_match_cache=cache)

    response = await pipeline.stream_and_buffer(
        _provider_stream_complete(),
        cache_key="cache-key",
        store_in_cache=True,
    )

    assert response.text == "answer ready"
    assert response.usage["input_tokens"] == 11
    assert response.usage["output_tokens"] == 5
    assert response.usage["stream_metadata"]["tool_call"]["name"] == "search"
    assert cache.saved_response is not None
    assert cache.saved_response.text == "answer ready"


@pytest.mark.asyncio
async def test_manager_stream_from_exact_cache_and_cacheable_stream_contract() -> None:
    manager = PromptCacheManager(adapter=_DummyAdapter())
    cached_response = LLMResponse(
        text="cached result",
        stop_reason="stop",
        usage={"input_tokens": 3, "output_tokens": 4},
    )
    cache = _FakeExactCache(preloaded=cached_response)

    stream_hit = await manager.stream_from_exact_cache(cache, "cache-key")
    assert stream_hit is not None
    hit_chunks = [chunk async for chunk in stream_hit]

    assert len(hit_chunks) == 2
    assert hit_chunks[0].type == "content_block_delta"
    assert hit_chunks[0].content == "cached result"
    assert hit_chunks[1].type == "message_stop"
    assert hit_chunks[1].metadata["usage"]["output_tokens"] == 4

    stream = await manager.stream(
        chunk_iterator=_provider_stream_complete(),
        exact_match_cache=cache,
        cache_key="cache-key",
        store_in_cache=True,
    )
    streamed = [chunk async for chunk in stream]
    assert len(streamed) == 3
    assert cache.saved_response is not None
    assert cache.saved_response.text == "answer ready"


@pytest.mark.asyncio
async def test_exact_match_cache_serde_roundtrip_without_struct_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    class _StubBackend:
        def __init__(self) -> None:
            self.raw: bytes | None = None

        async def get(self, key: str) -> bytes | None:
            return self.raw

        async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
            if isinstance(value, bytes):
                self.raw = value
            else:
                self.raw = str(value).encode()
            return True

        async def delete(self, key: str) -> bool:
            self.raw = None
            return True

        async def clear(self) -> bool:
            self.raw = None
            return True

        @property
        def stats(self) -> dict[str, Any]:
            return {}

    cache = ExactMatchPromptCache()
    stub = _StubBackend()
    monkeypatch.setattr(cache, "backend", stub)

    original = LLMResponse(text="serialized", stop_reason="stop", usage={"x": 1})
    assert await cache.set("cache-key", original) is True
    restored = await cache.get("cache-key")
    assert restored is not None
    assert restored.text == "serialized"
    assert restored.usage["x"] == 1
