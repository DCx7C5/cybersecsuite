"""Response injection strategy router — automatic selection via Qwen triage.

Decides PREPEND vs INJECT vs CHAIN based on query complexity using local LLM.
"""

from css.modules.triage import classify_query
from css.modules.a2a_google.enums import ResponseInjectionStrategy
from .enums import QueryComplexity


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
        """Classify query complexity heuristically for explicit fallback callers."""
        q_count = query_text.count("?")
        and_or = query_text.lower().count(" and ") + query_text.lower().count(" or ")
        synthesis = any(kw in query_text.lower() for kw in ["synthesize", "compare", "combine"])

        if synthesis or q_count >= 2:
            return QueryComplexity.COMPLEX
        elif and_or >= 1 or q_count == 1:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE

    @staticmethod
    def from_triage_category(category: object | None) -> QueryComplexity:
        """Map triage category to routing complexity."""
        value = getattr(category, "value", category)
        if not isinstance(value, str):
            return QueryComplexity.MODERATE
        normalized = value.lower()
        if normalized == "simple":
            return QueryComplexity.SIMPLE
        if normalized == "moderate":
            return QueryComplexity.MODERATE
        if normalized in {"complex", "critical"}:
            return QueryComplexity.COMPLEX
        return QueryComplexity.MODERATE

    async def classify_complexity(self, query_text: str) -> QueryComplexity:
        """Classify complexity using TriageEngine instead of heuristics."""
        result = await classify_query(query_text)
        if result.category is None:
            return QueryComplexity.MODERATE
        return self.from_triage_category(result.category)
