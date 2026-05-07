"""Chat WebSocket endpoint with async generator pipeline (Phase 6 T6.5).

Wires up the full pipeline for message processing:
source → classify → route → execute → observe

This endpoint receives messages from clients, processes them through
the pipeline stages, and streams results back.
"""

from typing import AsyncGenerator, Any, Optional
import logging

from css.core import pipe
from css.modules.triage import classify
from css.modules.strategies import route
from css.core.pipeline import ExecuteStage, ObserveStage

log = logging.getLogger(__name__)


async def message_source() -> AsyncGenerator[Any, None]:
    """Source stage that yields messages (would receive from WebSocket in real implementation)."""
    # Placeholder: in real use, this would yield messages from WebSocket clients
    yield {"text": "example message", "id": "msg-001"}


async def chat_pipeline() -> AsyncGenerator[Any, None]:
    """Assemble and run the full chat processing pipeline.

    Pipeline stages:
    1. classify: Triage classification
    2. route: Strategy routing based on classification
    3. execute: Call external LLM provider/handler
    4. observe: Emit telemetry events

    Usage:
        async for result in chat_pipeline():
            await websocket.send_json(result)
    """
    # Create pipeline stages
    execute = ExecuteStage()  # Will call handler from message or default
    observe = ObserveStage()

    # Compose pipeline: source → classify → route → execute → observe
    pipeline = pipe(
        message_source(),
        classify,  # from triage module
        route,     # from strategies module
        execute,   # from core.pipeline
        observe,   # from core.pipeline
    )

    # Yield all results
    async for result in pipeline:
        yield result


async def process_chat_message(message: dict) -> dict:
    """Process a single chat message through the pipeline.

    Args:
        message: Input message dict with at least 'text' and 'handler' fields

    Returns:
        Enriched message dict with classification, routing, and execution results
    """
    # Create a single-item source
    async def source():
        yield message

    # Compose pipeline
    execute = ExecuteStage()
    observe = ObserveStage()

    pipeline = pipe(
        source(),
        classify,
        route,
        execute,
        observe,
    )

    # Process single message
    async for result in pipeline:
        return result

    return message  # Fallback if pipeline fails
