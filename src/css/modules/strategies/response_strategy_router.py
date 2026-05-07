"""Response injection strategy router — automatic selection via Qwen triage.

Decides PREPEND vs INJECT vs CHAIN based on query complexity using local LLM.
"""

from enum import Enum

from css.core.a2a.enums import ResponseInjectionStrategy


class QueryComplexity(str, Enum):
    """Query complexity level for strategy selection."""

    SIMPLE = "simple"      # Binary yes/no, validation → INJECT
    MODERATE = "moderate"  # Routing decision, classification → PREPEND
    COMPLEX = "complex"    # Multi-step reasoning, synthesis → CHAIN


class ResponseStrategyRouter:
    """Routes to best response injection strategy based on query complexity."""

    STRATEGY_MAP = {
        QueryComplexity.SIMPLE: ResponseInjectionStrategy.INJECT,
        QueryComplexity.MODERATE: ResponseInjectionStrategy.PREPEND,
        QueryComplexity.COMPLEX: ResponseInjectionStrategy.CHAIN,
    }

    @staticmethod
    def decide_strategy(
        query: str,
        complexity: QueryComplexity | None = None,
    ) -> ResponseInjectionStrategy:
        """Decide injection strategy. Defaults to PREPEND when complexity unknown."""
        if complexity is None:
            return ResponseInjectionStrategy.PREPEND
        return ResponseStrategyRouter.STRATEGY_MAP.get(
            complexity, ResponseInjectionStrategy.PREPEND
        )

    @staticmethod
    def qwen_classify_complexity(query_text: str) -> QueryComplexity:
        """Classify query complexity via heuristics (placeholder for Qwen integration).

        TODO (Phase 2): Replace with actual Qwen call when triage layer added.
        """
        q_count = query_text.count("?")
        and_or = query_text.lower().count(" and ") + query_text.lower().count(" or ")
        synthesis = any(kw in query_text.lower() for kw in ["synthesize", "compare", "combine"])

        if synthesis or q_count >= 2:
            return QueryComplexity.COMPLEX
        elif and_or >= 1 or q_count == 1:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
