"""Response strategy routing pipeline stages (Phase 6 T6.5)."""

from css.core.logger import getLogger
from typing import AsyncGenerator, Any, Optional, override

from css.core.routing.pipeline import Stage
from css.modules.a2a_google.enums import ResponseInjectionStrategy
from .response_strategy_router import ResponseStrategyRouter


class RouteStage(Stage):
    """Response strategy routing stage.

    Receives messages (typically enriched from ClassifyStage), determines
    the optimal response injection strategy based on classification,
    and yields messages enriched with routing information.

    Expected input message fields:
    - text, query, or content: The query text
    - classification: TriageResult with category (optional)

    Output message fields added:
    - strategy: ResponseInjectionStrategy enum value
    - route_info: Dict with routing metadata
    """

    def __init__(self, router: Optional[ResponseStrategyRouter] = None):
        """Initialize route stage.

        Args:
            router: ResponseStrategyRouter instance (creates default if not provided)
        """
        self.router = router or ResponseStrategyRouter()

    @override
    async def __call__(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        """Route each message based on strategy decision.

        Args:
            stream: Async generator of messages to route

        Yields:
            Messages enriched with routing strategy and metadata
        """
        async for message in stream:
            try:
                # Extract query and classification info
                query = (
                    message.get("text")
                    if isinstance(message, dict)
                    else getattr(message, "text", None)
                ) or (
                    message.get("query")
                    if isinstance(message, dict)
                    else getattr(message, "query", None)
                ) or str(message)

                # Try to use classification from triage stage
                classification = (
                    message.get("classification")
                    if isinstance(message, dict)
                    else getattr(message, "classification", None)
                )

                # Determine complexity level
                complexity = None
                if classification and hasattr(classification, "category"):
                    # Map triage category to routing complexity
                    complexity = self.router.from_triage_category(classification.category)
                else:
                    # Fallback now uses real triage classification.
                    complexity = await self.router.classify_complexity(query)

                # Decide strategy
                strategy = self.router.decide_strategy(query, complexity)

                # Enrich message with routing info
                route_info = {
                    "complexity": complexity.value if complexity else None,
                    "strategy": strategy.value,
                }

                if isinstance(message, dict):
                    message["strategy"] = strategy
                    message["route_info"] = route_info
                else:
                    if hasattr(message, "__dict__"):
                        message.strategy = strategy
                        message.route_info = route_info

                yield message

            except Exception as e:
                log = getLogger(__name__)
                log.error(f"Route stage error: {e}")

                # Yield message with default strategy
                if isinstance(message, dict):
                    message["strategy"] = ResponseInjectionStrategy.PREPEND
                    message["routing_error"] = str(e)
                yield message


async def route(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
    """Convenience function for inline routing stage.

    Usage:
        results = pipe(source, classify, route)

    Args:
        stream: Async generator of messages

    Yields:
        Messages with routing strategy metadata
    """
    router = ResponseStrategyRouter()
    stage = RouteStage(router)
    async for item in stage(stream):
        yield item
