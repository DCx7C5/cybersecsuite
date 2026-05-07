"""Strategies module — response injection and routing strategies."""

from .response_strategy_router import QueryComplexity, ResponseStrategyRouter
# Phase 6 T6.5: Pipeline stages
from .pipeline import RouteStage, route
from .implementations import (
    BalancedStrategy,
    ChainStrategy,
    CostOptimizedStrategy,
    DirectStrategy,
    LatencyOptimizedStrategy,
    PrependContextStrategy,
    get_strategy,
)

__all__ = [
    "QueryComplexity",
    "ResponseStrategyRouter",
    # Pipeline stages
    "RouteStage",
    "route",
    # Strategy implementations
    "DirectStrategy",
    "PrependContextStrategy",
    "ChainStrategy",
    "BalancedStrategy",
    "CostOptimizedStrategy",
    "LatencyOptimizedStrategy",
    "get_strategy",
]
