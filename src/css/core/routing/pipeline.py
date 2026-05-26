"""
Async generator pipeline infrastructure for composable message processing (Phase 6 T6.5).

Convention — a "stage" is an async generator that yields results of type T_out,
consuming inputs of type T_in. Multiple stages can be piped together to form a
processing chain with type safety and backpressure support.

Example:

    async def source() -> AsyncGenerator[Message]:
        for item in items:
            yield item

    async def classify_stage(messages: AsyncGenerator[Message]):
        async for msg in messages:
            msg.classification = await classifier.predict(msg.text)
            yield msg

    async def route_stage(messages: AsyncGenerator[Message]):
        async for msg in messages:
            msg.route = determine_route(msg.classification)
            yield msg

    pipeline = pipe(source(), classify_stage, route_stage)
    async for result in pipeline:
        print(result)
"""

from collections.abc import Callable as ABCCallable

from css.core.logger import getLogger
from typing import AsyncGenerator, Callable, TypeVar, Any, override

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


StageCallable = Callable[[AsyncGenerator[T_in, None]], AsyncGenerator[T_out, None]]


async def pipe(
    source: AsyncGenerator[Any, None],
    *stages: StageCallable[Any, Any],
) -> AsyncGenerator[Any, None]:
    """Compose async generator stages into a pipeline."""
    current = source

    for stage in stages:
        current = stage(current)

    async for item in current:
        yield item


class Stage:
    """Base class for reusable pipeline stages with async generator contract."""

    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        if False:
            yield
        raise NotImplementedError


class PassthroughStage(Stage):
    """Stage that passes items through unchanged."""

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for item in stream:
            yield item


class BufferStage(Stage):
    """Stage that buffers items and yields them in batches.

    Args:
        batch_size: Number of items to buffer before yielding
    """

    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[list[Any], None]:
        batch = []
        async for item in stream:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []

        if batch:
            yield batch


class FilterStage(Stage):
    """Stage that filters items based on a predicate.

    Args:
        predicate: Async callable that returns True to keep an item, False to drop it
    """

    def __init__(self, predicate: Callable[[Any], Any]):
        self.predicate = predicate

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for item in stream:
            if await self.predicate(item):
                yield item


class MapStage(Stage):
    """Stage that applies an async transformation to each item.

    Args:
        transform: Async callable that transforms an item
    """

    def __init__(self, transform: Callable[[Any], Any]):
        self.transform = transform

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for item in stream:
            yield await self.transform(item)


class ExecuteStage(Stage):
    """Execute/dispatch stage for calling external services.

    Invokes a handler function on each message and enriches it with execution
    results. Used for LLM provider calls, database operations, etc.
    """

    def __init__(self, handler: Callable[[Any], Any] | None = None):
        self.default_handler = handler

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for message in stream:
            try:
                handler = (
                    message.get("handler")
                    if isinstance(message, dict)
                    else getattr(message, "handler", None)
                ) or self.default_handler

                if not handler:
                    if isinstance(message, dict):
                        message["execution_error"] = "No handler specified"
                    yield message
                    continue

                result = (
                    await handler(message)
                    if isinstance(handler, ABCCallable)
                    else handler
                )

                if isinstance(message, dict):
                    message["execution_result"] = result
                else:
                    if hasattr(message, "__dict__"):
                        message.execution_result = result

                yield message

            except Exception as e:
                log = getLogger(__name__)
                log.error(f"Execute stage error: {e}")

                if isinstance(message, dict):
                    message["execution_error"] = str(e)
                yield message


class ObserveStage(Stage):
    """Observability/logging stage for OpenTelemetry instrumentation.

    Pass-through stage that emits telemetry events without blocking the stream.
    Useful for cross-cutting concerns like logging, tracing, metrics.
    """

    def __init__(self, emit_span: Callable[[Any], Any] | None = None, emit_log: Callable[[Any], Any] | None = None):
        self.emit_span = emit_span or self._default_emit_span
        self.emit_log = emit_log or self._default_emit_log

    async def _default_emit_span(self, message: Any) -> None:
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            message_type = (
                message.get("type")
                if isinstance(message, dict)
                else getattr(message, "type", "unknown")
            )
            with tracer.start_as_current_span(f"message.{message_type}") as span:
                msg_id = message.get("id") if isinstance(message, dict) else getattr(message, "id", "unknown")
                span.set_attribute("message.id", str(msg_id))
        except Exception as e:
            log = getLogger(__name__)
            log.debug(f"Span emission failed: {e}")

    async def _default_emit_log(self, message: Any) -> None:
        try:
            log = getLogger(__name__)
            msg_type = (
                message.get("type")
                if isinstance(message, dict)
                else getattr(message, "type", "unknown")
            )
            msg_id = (
                message.get("id")
                if isinstance(message, dict)
                else getattr(message, "id", "unknown")
            )
            log.debug(f"Message processed: type={msg_type}, id={msg_id}")
        except Exception as e:
            log = getLogger(__name__)
            log.debug(f"Log emission failed: {e}")

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for message in stream:
            try:
                await self.emit_span(message)
                await self.emit_log(message)
            except Exception as e:
                log = getLogger(__name__)
                log.debug(f"Observe stage error (non-blocking): {e}")

            yield message
