"""Chat pipeline endpoint with async generator stages (Phase 8 wiring).

Wires up the full pipeline for message processing:
source → classify → route → execute → observe

This endpoint receives messages from clients, processes them through
the pipeline stages, and streams results back.
"""

from typing import AsyncGenerator, Any
import logging

from css.core import pipe
from css.modules.triage import classify
from css.modules.strategies import route
from css.core.pipeline import ExecuteStage, ObserveStage
from css.modules.agents.base import AgentExecutor
from css.modules.events import EventStore, DomainEvent
from css.config import OLLAMA_MODEL

log = logging.getLogger(__name__)
_EVENT_STORE = EventStore()


def get_pipeline_event_store() -> EventStore:
    """Expose pipeline EventStore for observability and testing."""
    return _EVENT_STORE


async def _source_from_message(message: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
    """Source stage for one incoming query message."""
    yield message


async def _execute_with_agent(message: dict[str, Any]) -> dict[str, Any]:
    """Execute stage handler backed by provider-agnostic AgentExecutor.

    If the caller provides a callable `handler` in the message, ExecuteStage
    resolves and executes that first. This fallback is for the common path
    where only text/session metadata is provided.
    """
    text = message.get("text") or message.get("query") or message.get("content") or ""
    provider = str(message.get("provider", "ollama"))
    model = str(message.get("model", OLLAMA_MODEL))

    executor = AgentExecutor(provider=provider, model=model)
    result = await executor.execute(
        prompt=text,
        context={
            "session_id": message.get("session_id", ""),
            "agent_id": message.get("agent_id", "chat-agent"),
        },
    )
    return {
        "text": result.response,
        "provider": result.provider,
        "model": result.model,
        "stop_reason": result.stop_reason,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "duration_ms": result.duration_ms,
    }


async def _observe_event(message: dict[str, Any]) -> None:
    """Observe stage callback that emits a DomainEvent into EventStore."""
    session_id = str(message.get("session_id", "unknown"))
    event = DomainEvent(
        kind="pipeline.observed",
        aggregate_type="chat_session",
        aggregate_id=session_id,
        data={
            "classification": getattr(message.get("classification"), "category", None).value
            if message.get("classification")
            else None,
            "strategy": message.get("route_info", {}).get("strategy"),
            "has_execution_result": "execution_result" in message,
            "has_execution_error": "execution_error" in message,
        },
        metadata={"source": "chat.pipeline"},
    )
    _EVENT_STORE.append(event)


async def chat_pipeline(message: dict[str, Any]) -> AsyncGenerator[Any, None]:
    """Assemble and run the full chat processing pipeline for one message.

    Pipeline stages:
    1. classify: Triage classification
    2. route: Strategy routing based on classification
    3. execute: Call external LLM provider/handler
    4. observe: Emit telemetry events

    Usage:
        async for result in chat_pipeline():
            await websocket.send_json(result)
    """
    execute = ExecuteStage(handler=_execute_with_agent)
    observe = ObserveStage(emit_log=_observe_event)

    # Compose pipeline: source → classify → route → execute → observe
    pipeline = pipe(
        _source_from_message(message),
        classify,  # from triage module
        route,     # from strategies module
        execute,   # default handler -> AgentExecutor fallback
        observe,   # emits DomainEvent to EventStore
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
    async for result in chat_pipeline(message):
        return result

    return message  # Fallback if pipeline fails
