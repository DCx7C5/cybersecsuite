"""Canonical triage pipeline entrypoints after root intelligence-facade removal."""

from css.core.logger import getLogger
from typing import AsyncGenerator, Any, Optional, override

from css.core.routing.pipeline import Stage
from .engine import TriageEngine
from .models import TriageRequest


class ClassifyStage(Stage):
    """Triage classification stage.

    Receives messages from upstream, classifies each one using the triage
    engine, and yields messages enriched with classification metadata.

    Input messages should have a 'text' or 'query' field containing the
    content to classify.

    Output messages will have added fields:
    - classification: TriageResult with category, decision, severity
    - confidence: float (0.0-1.0)
    """

    def __init__(self, engine: Optional[TriageEngine] = None):
        """Initialize classify stage.

        Args:
            engine: TriageEngine instance (creates default if not provided)
        """
        self.engine = engine or TriageEngine()

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        """Classify each message in the stream.

        Args:
            stream: Async generator of messages to classify

        Yields:
            Messages enriched with classification metadata
        """
        async for message in stream:
            try:
                # Extract query text from message
                # Support multiple field names for flexibility
                query = (
                    message.get("text")
                    or message.get("query")
                    or message.get("content")
                    or str(message)
                )

                # Create triage request and classify
                request = TriageRequest(query=query)
                result = await self.engine.classify(request)

                # Enrich message with classification
                if isinstance(message, dict):
                    message["classification"] = result
                    message["confidence"] = result.confidence if result else 0.0
                else:
                    # For objects with __dict__, try to set attributes
                    if hasattr(message, "__dict__"):
                        message.classification = result
                        message.confidence = result.confidence if result else 0.0

                yield message

            except Exception as e:
                # Log but continue processing (don't break the stream)
                log = getLogger(__name__)
                log.error(f"Classify stage error: {e}")

                # Yield message even if classification failed (optional)
                # or skip it depending on requirements
                if isinstance(message, dict):
                    message["classification_error"] = str(e)
                yield message


async def classify(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
    """Convenience function for inline classification stage.

    Usage:
        results = pipe(source, classify)

    Args:
        stream: Async generator of messages

    Yields:
        Messages with classification metadata
    """
    engine = TriageEngine()
    stage = ClassifyStage(engine)
    async for item in stage(stream):
        yield item
