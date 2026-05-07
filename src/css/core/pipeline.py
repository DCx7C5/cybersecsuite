"""
Async generator pipeline infrastructure for composable message processing (Phase 6 T6.5).

Convention — a "stage" is an async generator that yields results of type T_out,
consuming inputs of type T_in. Multiple stages can be piped together to form a
processing chain with type safety and backpressure support.

Example:

    async def source() -> AsyncGenerator[Message]:
        # Yield initial messages
        for item in items:
            yield item

    async def classify_stage(messages: AsyncGenerator[Message]):
        # Process and classify messages
        async for msg in messages:
            msg.classification = await classifier.predict(msg.text)
            yield msg

    async def route_stage(messages: AsyncGenerator[Message]):
        # Route based on classification
        async for msg in messages:
            msg.route = determine_route(msg.classification)
            yield msg

    # Compose pipeline
    pipeline = pipe(source(), classify_stage, route_stage)
    async for result in pipeline:
        print(result)
"""

from typing import AsyncGenerator, Callable, TypeVar, Any

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


# Stage type: async callable that takes an async generator and yields results
# Can also be a plain async generator function (source stage)
Stage = Callable[[AsyncGenerator[T_in, None]], AsyncGenerator[T_out, None]]


async def pipe(
    source: AsyncGenerator[Any, None],
    *stages: Stage,
) -> AsyncGenerator[Any, None]:
    """Compose async generator stages into a pipeline.

    Args:
        source: Initial async generator yielding items to process
        *stages: One or more stage callables that transform the stream

    Yields:
        Final output from the last stage in the pipeline

    Example:
        async def classify(messages):
            async for msg in messages:
                msg.type = await classifier.predict(msg)
                yield msg

        async def route(messages):
            async for msg in messages:
                msg.handler = get_handler(msg.type)
                yield msg

        results = pipe(source_gen(), classify, route)
        async for item in results:
            await item.handler()
    """
    current = source

    for stage in stages:
        current = stage(current)

    async for item in current:
        yield item


class Stage:
    """Base class for reusable pipeline stages with async generator contract.

    Subclass to create domain-specific stages that can be composed into pipelines.

    Example:

        class ClassifyStage(Stage):
            async def __call__(self, stream):
                async for msg in stream:
                    msg.topic = await classifier.predict(msg.text)
                    yield msg

        class RouteStage(Stage):
            async def __call__(self, stream):
                async for msg in stream:
                    msg.handler = routers[msg.topic]
                    yield msg

        async def pipeline(messages):
            classify = ClassifyStage()
            route = RouteStage()
            return pipe(messages, classify, route)
    """

    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        """Transform stream items.

        Must be implemented by subclasses. Implementations should:
        - Iterate over the input stream
        - Transform items as needed
        - Yield results (can be the same items modified, or new items)
        """
        raise NotImplementedError


class PassthroughStage(Stage):
    """Simple stage that passes items through unchanged.

    Useful for debugging or as a no-op placeholder.
    """

    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for item in stream:
            yield item


class BufferStage(Stage):
    """Stage that buffers items and yields them in batches.

    Useful for reducing per-item overhead in downstream stages.

    Args:
        batch_size: Number of items to buffer before yielding
    """

    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size

    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[list, None]:
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

    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        async for item in stream:
            yield await self.transform(item)


class ExecuteStage(Stage):
    """Execute/dispatch stage for calling external services (Phase 6 T6.5).

    Invokes a handler function on each message and enriches it with execution
    results. Used for LLM provider calls, database operations, etc.

    Input message fields:
    - handler: Callable that will be invoked with the message
    - (other fields are passed to handler)

    Output message fields added:
    - execution_result: Result from handler execution
    - execution_error: Error message if handler failed
    """

    def __init__(self, handler=None):
        """Initialize execute stage.

        Args:
            handler: Optional default handler callable for all messages.
                     If None, messages must have a 'handler' field.
        """
        self.default_handler = handler

    async def __call__(self, stream):
        """Execute handler on each message.

        Args:
            stream: Async generator of messages

        Yields:
            Messages enriched with execution results
        """
        async for message in stream:
            try:
                # Get handler from message or use default
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

                # Execute handler
                result = (
                    await handler(message)
                    if callable(handler)
                    else handler
                )

                # Enrich message with result
                if isinstance(message, dict):
                    message["execution_result"] = result
                else:
                    if hasattr(message, "__dict__"):
                        message.execution_result = result

                yield message

            except Exception as e:
                import logging
                log = logging.getLogger(__name__)
                log.error(f"Execute stage error: {e}")

                if isinstance(message, dict):
                    message["execution_error"] = str(e)
                yield message


class ObserveStage(Stage):
    """Observability/logging stage for OpenTelemetry instrumentation (Phase 6 T6.5).

    Pass-through stage that emits telemetry events without blocking the stream.
    Useful for cross-cutting concerns like logging, tracing, metrics.

    Args:
        emit_span: Optional callable to emit a span for each message
        emit_log: Optional callable to log message metadata
    """

    def __init__(self, emit_span=None, emit_log=None):
        """Initialize observe stage.

        Args:
            emit_span: Async callable(message) -> trace span event
            emit_log: Async callable(message) -> log event
        """
        self.emit_span = emit_span or self._default_emit_span
        self.emit_log = emit_log or self._default_emit_log

    async def _default_emit_span(self, message):
        """Default span emission using OpenTelemetry."""
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
            import logging
            log = logging.getLogger(__name__)
            log.debug(f"Span emission failed: {e}")

    async def _default_emit_log(self, message):
        """Default logging of message metadata."""
        try:
            import logging
            log = logging.getLogger(__name__)
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
            import logging
            log = logging.getLogger(__name__)
            log.debug(f"Log emission failed: {e}")

    async def __call__(self, stream):
        """Pass items through while emitting telemetry.

        Args:
            stream: Async generator of messages

        Yields:
            Messages unchanged
        """
        async for message in stream:
            try:
                # Emit span and log without blocking
                await self.emit_span(message)
                await self.emit_log(message)
            except Exception as e:
                import logging
                log = logging.getLogger(__name__)
                log.debug(f"Observe stage error (non-blocking): {e}")

            yield message
