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
