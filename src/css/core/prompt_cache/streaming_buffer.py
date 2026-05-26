"""Redis streaming buffer for prompt response accumulation.

Buffers streaming chunks from provider LLMs and stores the complete,
accumulated response back into Redis for exact-match cache hits.

Used when:
  - Provider response is streamed (incrementally generated)
  - Want to cache the final accumulated response for future exact-match lookups
  - Need to track intermediate chunk statistics (latency, token count)
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse, StreamChunk

logger = getLogger(__name__)


class StreamingBuffer:
    """Accumulates streaming chunks into a complete LLM response."""

    def __init__(self):
        """Initialize streaming buffer."""
        self.chunks: list[StreamChunk] = []
        self.accumulated_content = ""
        self.finish_reason: str | None = None
        self.usage: dict[str, Any] | None = None
        self.started_at = datetime.now(UTC)
        self.ended_at: datetime | None = None

    async def append_chunk(self, chunk: StreamChunk) -> None:
        """Buffer a single streaming chunk.

        Args:
            chunk: StreamChunk from provider LLM
        """
        self.chunks.append(chunk)

        if hasattr(chunk, "content") and chunk.content:
            self.accumulated_content += chunk.content

        if hasattr(chunk, "finish_reason") and chunk.finish_reason:
            self.finish_reason = chunk.finish_reason

        if hasattr(chunk, "usage") and chunk.usage:
            self.usage = chunk.usage

    async def finalize(self) -> LLMResponse:
        """Finalize buffered chunks into complete LLMResponse.

        Returns:
            LLMResponse with accumulated content and metadata
        """
        self.ended_at = datetime.now(UTC)
        duration_seconds = (self.ended_at - self.started_at).total_seconds()

        return LLMResponse(
            content=self.accumulated_content,
            finish_reason=self.finish_reason or "stop",
            usage={
                "input_tokens": self.usage.get("input_tokens", 0) if self.usage else 0,
                "output_tokens": self.usage.get("output_tokens", 0) if self.usage else 0,
            },
            timestamp=self.started_at,
            metadata={
                "buffer_chunk_count": len(self.chunks),
                "duration_seconds": duration_seconds,
                "streaming": True,
            },
        )

    @property
    def is_complete(self) -> bool:
        """Whether streaming is complete."""
        return self.finish_reason is not None or self.ended_at is not None

    def reset(self) -> None:
        """Clear buffer for reuse."""
        self.chunks = []
        self.accumulated_content = ""
        self.finish_reason = None
        self.usage = None
        self.started_at = datetime.now(UTC)
        self.ended_at = None


class PromptCacheStreamingBuffer:
    """Manages streaming buffer + Redis storage pipeline.

    Orchestrates:
      1. Buffer streaming chunks from provider
      2. Finalize into complete LLMResponse
      3. Store in Redis for exact-match cache hits
    """

    def __init__(self, exact_match_cache: Any):
        """Initialize streaming buffer with cache backend.

        Args:
            exact_match_cache: ExactMatchPromptCache instance
        """
        self.cache = exact_match_cache
        self.buffer = StreamingBuffer()

    async def stream_and_buffer(
        self,
        chunk_iterator,
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

        try:
            async for chunk in chunk_iterator:
                await self.buffer.append_chunk(chunk)
                if hasattr(chunk, "end_turn") and chunk.end_turn:
                    break
        except Exception as e:
            logger.error(f"Error streaming chunks: {e}")
            raise

        response = await self.buffer.finalize()

        if store_in_cache and cache_key:
            try:
                await self.cache.set(cache_key, response)
            except Exception as e:
                logger.warning(f"Failed to store buffered response in cache: {e}")

        return response

    async def stream_and_yield(
        self,
        chunk_iterator,
        cache_key: str | None = None,
        store_in_cache: bool = True,
    ):
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

        try:
            async for chunk in chunk_iterator:
                await self.buffer.append_chunk(chunk)
                yield chunk
                if hasattr(chunk, "end_turn") and chunk.end_turn:
                    break
        except Exception as e:
            logger.error(f"Error streaming chunks: {e}")
            raise
        finally:
            response = await self.buffer.finalize()
            if store_in_cache and cache_key:
                try:
                    await self.cache.set(cache_key, response)
                except Exception as e:
                    logger.warning(f"Failed to store buffered response in cache: {e}")

    def reset(self) -> None:
        """Reset buffer for next streaming session."""
        self.buffer.reset()
