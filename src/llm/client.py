"""AsyncLLMClient — session-aware AsyncAnthropic wrapper with OTEL tracing.

Usage::

    client = AsyncLLMClient(model="claude-sonnet-4-5", sid="abc123def456")

    # Streaming
    async for chunk in await client.chat(messages):
        print(chunk, end="")

    # Non-streaming (returns anthropic.types.Message)
    msg = await client.chat(messages, stream=False)
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

log = logging.getLogger("llm.client")


class AsyncLLMClient:
    """Thin session-aware wrapper around AsyncAnthropic."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-5",
        sid: str = "global",
        log_prompts: bool = False,
        db_persist_fn: Any = None,
        oo_index_fn: Any = None,
    ) -> None:
        self.model = model
        self.sid = sid
        self.log_prompts = log_prompts
        self._persist = db_persist_fn   # async callable(*, sid, model, ...) or None
        self._oo_index = oo_index_fn    # async callable(stream_name, [docs]) or None
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        self._client = self._make_client(base_url)

    @staticmethod
    def _make_client(base_url: str | None):
        from anthropic import AsyncAnthropic
        return AsyncAnthropic(base_url=base_url) if base_url else AsyncAnthropic()

    async def chat(
        self,
        messages: list[dict],
        *,
        max_tokens: int = 4096,
        stream: bool = True,
        tools: list[dict] | None = None,
        system: str | None = None,
        **kwargs: Any,
    ):
        """Start a chat completion.

        Returns:
            AsyncIterator[str] when stream=True
            anthropic.types.Message when stream=False
        """
        kwargs.update({"max_tokens": max_tokens})
        if system is not None:
            kwargs["system"] = system
        if tools is not None:
            kwargs["tools"] = tools
        if stream:
            return self._stream(messages, **kwargs)
        return await self._complete(messages, **kwargs)

    async def _stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        from llm.otel import get_tracer
        from llm.pricing import cost_usd as _cost_usd

        tracer = get_tracer()
        t0 = time.perf_counter()
        input_tokens = output_tokens = cache_read = cache_write = 0
        error: str | None = None

        with tracer.start_as_current_span("llm.stream") as span:
            span.set_attribute("worktree.sid", self.sid)
            span.set_attribute("llm.model", self.model)
            try:
                async with self._client.messages.stream(
                    model=self.model, messages=messages, **kwargs
                ) as stream_ctx:
                    async for text in stream_ctx.text_stream:
                        yield text
                    final = await stream_ctx.get_final_message()
                    u = final.usage
                    input_tokens  = u.input_tokens
                    output_tokens = u.output_tokens
                    cache_read    = getattr(u, "cache_read_input_tokens", 0) or 0
                    cache_write   = getattr(u, "cache_creation_input_tokens", 0) or 0
            except Exception as exc:
                error = str(exc)
                span.record_exception(exc)
                raise
            finally:
                latency = (time.perf_counter() - t0) * 1000
                cost = _cost_usd(self.model, input_tokens, output_tokens, cache_write, cache_read)
                span.set_attribute("llm.input_tokens",  input_tokens)
                span.set_attribute("llm.output_tokens", output_tokens)
                span.set_attribute("llm.cost_usd",      float(cost))
                span.set_attribute("llm.latency_ms",    latency)
                asyncio.create_task(
                    self._bg_persist(
                        input_tokens, output_tokens, cache_read, cache_write,
                        cost, latency, stream=True, error=error,
                    )
                )

    async def _complete(self, messages: list[dict], **kwargs):
        from llm.otel import get_tracer
        from llm.pricing import cost_usd as _cost_usd

        tracer = get_tracer()
        t0 = time.perf_counter()
        with tracer.start_as_current_span("llm.complete") as span:
            span.set_attribute("worktree.sid", self.sid)
            span.set_attribute("llm.model", self.model)
            try:
                msg = await self._client.messages.create(
                    model=self.model, messages=messages, **kwargs
                )
                u = msg.usage
                cost = _cost_usd(
                    self.model,
                    u.input_tokens,
                    u.output_tokens,
                    getattr(u, "cache_creation_input_tokens", 0) or 0,
                    getattr(u, "cache_read_input_tokens", 0) or 0,
                )
                latency = (time.perf_counter() - t0) * 1000
                span.set_attribute("llm.input_tokens",  u.input_tokens)
                span.set_attribute("llm.output_tokens", u.output_tokens)
                span.set_attribute("llm.cost_usd",      float(cost))
                span.set_attribute("llm.latency_ms",    latency)
                asyncio.create_task(
                    self._bg_persist(
                        u.input_tokens,
                        u.output_tokens,
                        getattr(u, "cache_read_input_tokens", 0) or 0,
                        getattr(u, "cache_creation_input_tokens", 0) or 0,
                        cost,
                        latency,
                        stream=False,
                        error=None,
                    )
                )
                return msg
            except Exception as exc:
                span.record_exception(exc)
                raise

    async def _bg_persist(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_read: int,
        cache_write: int,
        cost: Decimal,
        latency_ms: float,
        stream: bool,
        error: str | None,
    ) -> None:
        try:
            if self._persist:
                await self._persist(
                    sid=self.sid,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_read_tokens=cache_read,
                    cache_write_tokens=cache_write,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                    stream=stream,
                    success=error is None,
                    error=error,
                    request_id=None,
                )
            if self._oo_index:
                await self._oo_index("llm-calls", [{
                    "worktree_sid": self.sid,
                    "model": self.model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": float(cost),
                    "latency_ms": latency_ms,
                    "stream": stream,
                    "success": error is None,
                }])
        except Exception:
            log.exception("Background persist failed (non-fatal)")
