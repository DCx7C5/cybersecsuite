"""Redis streaming buffer for prompt response accumulation.

Buffers streaming chunks from provider LLMs and stores the complete,
accumulated response back into Redis for exact-match cache hits.

Used when:
  - Provider response is streamed (incrementally generated)
  - Want to cache the final accumulated response for future exact-match lookups
  - Need to track intermediate chunk statistics (latency, token count)
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, Protocol

from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse, StreamChunk

logger = getLogger(__name__)


class SupportsExactMatchPromptCache(Protocol):
    """Cache interface required by PromptCacheStreamingBuffer."""

    async def set(self, cache_key: str, response: LLMResponse) -> bool:
        """Store finalized buffered response."""
        ...


class StreamingBuffer:
    """Accumulates streaming chunks into a complete LLM response."""

    def __init__(self) -> None:
        """Initialize streaming buffer."""
        self.chunks: list[StreamChunk] = []
        self._text_parts: list[str] = []
        self.stop_reason: str | None = None
        self.usage: dict[str, Any] = {}
        self.stream_metadata: dict[str, Any] = {}
        self.started_at = datetime.now(UTC)
        self.ended_at: datetime | None = None
        self.completed_normally = False

    async def append_chunk(self, chunk: StreamChunk) -> None:
        """Buffer a single streaming chunk.

        Args:
            chunk: StreamChunk from provider LLM
        """
        self.chunks.append(chunk)

        if chunk.content:
            self._text_parts.append(chunk.content)

        if chunk.stop_reason:
            self.stop_reason = chunk.stop_reason

        metadata = chunk.metadata
        usage_obj = metadata.get("usage")
        if isinstance(usage_obj, dict):
            self.usage = dict(usage_obj)

        for key, value in metadata.items():
            if key == "usage" or value is None:
                continue
            self.stream_metadata[key] = value

        if chunk.type == "message_stop" and self.stop_reason is None:
            metadata_stop_reason = metadata.get("stop_reason")
            if isinstance(metadata_stop_reason, str) and metadata_stop_reason:
                self.stop_reason = metadata_stop_reason

    async def finalize(self, completed_normally: bool = True) -> LLMResponse:
        """Finalize buffered chunks into complete LLMResponse.

        Args:
            completed_normally: Whether the stream iterator completed without
                provider cancellation/error.

        Returns:
            LLMResponse with accumulated content and metadata
        """
        self.completed_normally = completed_normally
        self.ended_at = datetime.now(UTC)
        duration_seconds = (self.ended_at - self.started_at).total_seconds()

        resolved_stop_reason = self.stop_reason
        if resolved_stop_reason is None:
            if completed_normally and self.chunks:
                resolved_stop_reason = "stop"
            elif completed_normally:
                resolved_stop_reason = "eof"
            else:
                resolved_stop_reason = "cancelled"

        usage_payload = dict(self.usage)
        if self.stream_metadata:
            usage_payload["stream_metadata"] = dict(self.stream_metadata)
        usage_payload.setdefault("buffer_chunk_count", len(self.chunks))
        usage_payload.setdefault("buffer_duration_seconds", duration_seconds)

        return LLMResponse(
            text="".join(self._text_parts),
            stop_reason=resolved_stop_reason,
            usage=usage_payload,
        )

    @property
    def is_complete(self) -> bool:
        """Whether a stream completed normally and is eligible for caching."""
        return self.completed_normally and self.ended_at is not None and bool(self.chunks)

    @property
    def has_chunks(self) -> bool:
        """Whether any chunks were observed."""
        return bool(self.chunks)

    def reset(self) -> None:
        """Clear buffer for reuse."""
        self.chunks = []
        self._text_parts = []
        self.stop_reason = None
        self.usage = {}
        self.stream_metadata = {}
        self.started_at = datetime.now(UTC)
        self.ended_at = None
        self.completed_normally = False


class PromptCacheStreamingBuffer:
    """Manages streaming buffer + Redis storage pipeline.

    Orchestrates:
      1. Buffer streaming chunks from provider
      2. Finalize into complete LLMResponse
      3. Store in Redis for exact-match cache hits
    """

    def __init__(self, exact_match_cache: SupportsExactMatchPromptCache):
        """Initialize streaming buffer with cache backend.

        Args:
            exact_match_cache: ExactMatchPromptCache instance
        """
        self.cache = exact_match_cache
        self.buffer = StreamingBuffer()

    async def _store_final_response(
        self,
        cache_key: str,
        response: LLMResponse,
    ) -> None:
        """Store final response in cache; logs warning on non-store."""
        stored = await self.cache.set(cache_key, response)
        if not stored:
            logger.warning(
                "Prompt cache stream final response was not stored for key prefix %s",
                cache_key[:16],
            )

    async def stream_and_buffer(
        self,
        chunk_iterator: AsyncIterator[StreamChunk],
        cache_key: str | None = None,
        store_in_cache: bool = True,
    ) -> LLMResponse:
        """Consume streaming iterator, buffer chunks, optionally store in cache.

        Args:
            chunk_iterator: AsyncIterator[StreamChunk] from provider LLM
            cache_key: Redis key for storage (from PromptCacheManager.compute_exact_match_key)
            store_in_cache: Whether to store finalized response in Redis

        Yields/Returns:
            Complete LLMResponse after consuming all chunks
        """
        self.buffer.reset()

        async for chunk in chunk_iterator:
            await self.buffer.append_chunk(chunk)

        response = await self.buffer.finalize(completed_normally=True)
        if store_in_cache and cache_key and self.buffer.is_complete:
            await self._store_final_response(cache_key, response)

        return response

    async def stream_and_yield(
        self,
        chunk_iterator: AsyncIterator[StreamChunk],
        cache_key: str | None = None,
        store_in_cache: bool = True,
    ) -> AsyncIterator[StreamChunk]:
        """Stream chunks while buffering for cache storage.

        Yields streaming chunks to caller while accumulating in buffer.
        After iteration complete, stores finalized response in cache.

        Args:
            chunk_iterator: AsyncIterator[StreamChunk] from provider LLM
            cache_key: Redis key for storage
            store_in_cache: Whether to store finalized response in Redis

        Yields:
            StreamChunk for each iteration (pass-through to caller)
        """
        self.buffer.reset()

        async for chunk in chunk_iterator:
            await self.buffer.append_chunk(chunk)
            yield chunk

        if not (store_in_cache and cache_key and self.buffer.has_chunks):
            return

        response = await self.buffer.finalize(completed_normally=True)
        if self.buffer.is_complete:
            await self._store_final_response(cache_key, response)

    def reset(self) -> None:
        """Reset buffer for next streaming session."""
        self.buffer.reset()
