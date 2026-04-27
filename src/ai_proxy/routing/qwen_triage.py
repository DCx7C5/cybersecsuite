"""QwenTriageRouter — Tier 0 router with intelligent triage, cost optimization, and fallback routing.

Referenz:
    plan.md t134 — Tier 0 router (QwenTriageRouter)
    plan.md T0-INF-004 — AIProviderContext integration
    src/ai_proxy/routing/combo.py — Routing engine
    src/llm/ai_provider_context.py — AIProviderContext
"""


import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from llm.ai_provider_context import AIProviderContext, AIProviderType, ContextSource

logger = logging.getLogger("ai_proxy.routing.qwen_triage")


class TriageLevel(str, Enum):
    """Triage classification levels for request routing."""

    tier0_simple = "tier0_simple"  # Free tier: Ollama local
    tier1_standard = "tier1_standard"  # Standard: Gemini, Copilot
    tier2_advanced = "tier2_advanced"  # Advanced: Claude, OpenAI GPT
    tier3_premium = "tier3_premium"  # Premium: Claude Premium, GPT-4o
    tier4_critical = "tier4_critical"  # Critical: Dedicated with priority


class RequestComplexity(str, Enum):
    """Measure of request complexity for triage."""

    trivial = "trivial"  # < 50 tokens
    simple = "simple"  # 50-200 tokens
    moderate = "moderate"  # 200-1000 tokens
    complex = "complex"  # 1000-4000 tokens
    critical = "critical"  # > 4000 tokens


@dataclass
class TriageMetrics:
    """Metrics collected during triage analysis."""

    input_length: int
    estimated_tokens: int
    complexity: RequestComplexity
    has_tool_use: bool
    requires_vision: bool
    has_code_generation: bool
    requires_reasoning: bool
    security_level: int  # 1-10, 10 highest


class QwenTriageRequest(BaseModel):
    """Request for Qwen triage routing."""

    request_id: str = Field(..., description="Unique request identifier")
    query: str = Field(..., description="User query or prompt", max_length=10000)
    context_history: list[dict[str, str]] = Field(
        default_factory=list, description="Conversation history for context"
    )
    tools_requested: list[str] = Field(
        default_factory=list, description="Tools that will be used"
    )
    requires_vision: bool = Field(default=False, description="Image/vision analysis needed")
    max_budget_cents: int = Field(
        default=1000, description="Maximum budget in cents for this request"
    )
    preferred_providers: list[AIProviderType] = Field(
        default_factory=lambda: [AIProviderType.claude],
        description="User preferred providers in priority order",
    )
    session_id: str | None = Field(default=None, description="Session identifier")
    force_provider: AIProviderType | None = Field(
        default=None, description="Force specific provider (bypass triage)"
    )

    class Config:
        """Pydantic config."""

        use_enum_values = False


class QwenTriageResponse(BaseModel):
    """Response from Qwen triage router."""

    request_id: str
    triage_level: TriageLevel
    primary_provider: AIProviderContext
    fallback_providers: list[AIProviderContext] = Field(default_factory=list)
    estimated_cost_cents: int
    reasoning: str
    metrics: dict[str, Any]

    class Config:
        """Pydantic config."""

        use_enum_values = False


class QwenTriageRouter:
    """
    Tier 0 router using Qwen-style triage for intelligent provider selection.

    Implements cost-optimized, context-aware routing with:
    - Complexity analysis (trivial, simple, moderate, complex, critical)
    - Budget-aware fallback (always prefer cheaper options first)
    - Provider capability matching (vision, tools, reasoning)
    - Session-based preference learning
    - Fallback chain with circuit breaker support

    Routing Strategy:
        1. Analyze request complexity and characteristics
        2. Calculate triage level (tier0-4)
        3. Select primary provider based on triage + budget + preferences
        4. Build fallback chain with cost optimization
        5. Inject AIProviderContext with routing metadata
    """

    # Provider tier matrix: (provider, cost_cents_per_1k_tokens, supports_vision)
    PROVIDER_TIERS: dict[AIProviderType, tuple[int, bool, list[str]]] = {
        AIProviderType.ollama_local: (0, False, ["general"]),
        AIProviderType.gemini: (0.5, True, ["general", "vision"]),
        AIProviderType.copilot: (1, False, ["general"]),
        AIProviderType.grok: (1, False, ["general", "reasoning"]),
        AIProviderType.openai: (3, True, ["general", "vision", "code"]),
        AIProviderType.claude: (5, True, ["general", "vision", "reasoning"]),
    }

    def __init__(self) -> None:
        """Initialize Qwen triage router."""
        self.logger = logger
        self.cache: dict[str, QwenTriageResponse] = {}

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: ~4 chars per token.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough approximation: average 4 characters per token
        return max(1, len(text) // 4)

    def analyze_complexity(self, request: QwenTriageRequest) -> TriageMetrics:
        """
        Analyze request to determine complexity.

        Args:
            request: QwenTriageRequest

        Returns:
            TriageMetrics with analysis

        Raises:
            ValueError: If request is invalid
        """
        if not request.query:
            raise ValueError("Query cannot be empty")

        input_length = len(request.query)
        estimated_tokens = self.estimate_tokens(request.query)

        # Determine complexity level
        if estimated_tokens < 50:
            complexity = RequestComplexity.trivial
        elif estimated_tokens < 200:
            complexity = RequestComplexity.simple
        elif estimated_tokens < 1000:
            complexity = RequestComplexity.moderate
        elif estimated_tokens < 4000:
            complexity = RequestComplexity.complex
        else:
            complexity = RequestComplexity.critical

        # Analyze characteristics
        has_tool_use = len(request.tools_requested) > 0
        has_code_generation = "code" in request.query.lower() or "function" in request.query.lower()
        requires_reasoning = (
            "why" in request.query.lower()
            or "analyze" in request.query.lower()
            or "explain" in request.query.lower()
        )

        # Security level estimation (1-10)
        security_level = 1
        if "security" in request.query.lower() or "vulnerability" in request.query.lower():
            security_level = 8
        elif "penetration" in request.query.lower() or "exploit" in request.query.lower():
            security_level = 10
        elif has_code_generation:
            security_level = 5

        return TriageMetrics(
            input_length=input_length,
            estimated_tokens=estimated_tokens,
            complexity=complexity,
            has_tool_use=has_tool_use,
            requires_vision=request.requires_vision,
            has_code_generation=has_code_generation,
            requires_reasoning=requires_reasoning,
            security_level=security_level,
        )

    def determine_triage_level(
        self, metrics: TriageMetrics, budget_cents: int, force_provider: AIProviderType | None
    ) -> TriageLevel:
        """
        Determine triage level based on metrics and budget.

        Args:
            metrics: TriageMetrics from analysis
            budget_cents: Maximum budget in cents
            force_provider: Force provider (returns tier4 for priority)

        Returns:
            TriageLevel
        """
        # If provider forced, mark as critical for priority handling
        if force_provider:
            return TriageLevel.tier4_critical

        # Budget-based routing
        estimated_cost = metrics.estimated_tokens * 0.005  # Average cost estimate

        if budget_cents < int(estimated_cost):
            return TriageLevel.tier0_simple

        # Complexity-based routing
        if metrics.security_level >= 9:
            return TriageLevel.tier4_critical
        elif metrics.complexity == RequestComplexity.critical:
            return TriageLevel.tier3_premium
        elif metrics.complexity == RequestComplexity.complex:
            if metrics.requires_reasoning or metrics.has_code_generation:
                return TriageLevel.tier2_advanced
            return TriageLevel.tier1_standard
        elif metrics.complexity in (RequestComplexity.simple, RequestComplexity.trivial):
            return TriageLevel.tier0_simple

        return TriageLevel.tier1_standard

    def select_provider(
        self,
        triage_level: TriageLevel,
        metrics: TriageMetrics,
        preferred_providers: list[AIProviderType],
        force_provider: AIProviderType | None,
    ) -> AIProviderType:
        """
        Select primary provider based on triage level.

        Args:
            triage_level: Triage level from determination
            metrics: TriageMetrics
            preferred_providers: User preferred providers
            force_provider: Force specific provider

        Returns:
            Selected AIProviderType
        """
        if force_provider:
            return force_provider

        # Check user preferences first
        for provider in preferred_providers:
            if self._provider_supports_request(provider, metrics):
                return provider

        # Select based on triage level
        if triage_level == TriageLevel.tier0_simple:
            return AIProviderType.ollama_local
        elif triage_level == TriageLevel.tier1_standard:
            return AIProviderType.gemini
        elif triage_level == TriageLevel.tier2_advanced:
            return AIProviderType.openai
        elif triage_level in (TriageLevel.tier3_premium, TriageLevel.tier4_critical):
            return AIProviderType.claude

        return AIProviderType.claude

    def build_fallback_chain(
        self, primary: AIProviderType, metrics: TriageMetrics, budget_remaining: int
    ) -> list[AIProviderType]:
        """
        Build fallback provider chain ordered by cost.

        Args:
            primary: Primary provider selected
            metrics: TriageMetrics
            budget_remaining: Remaining budget in cents

        Returns:
            List of fallback providers in priority order
        """
        fallbacks: list[AIProviderType] = []
        budget = budget_remaining

        # Get all providers except primary, sorted by cost
        candidates = sorted(
            [p for p in AIProviderType if p != primary],
            key=lambda p: self.PROVIDER_TIERS[p][0],
        )

        for provider in candidates:
            cost, supports_vision, capabilities = self.PROVIDER_TIERS[provider]

            # Skip if doesn't support required features
            if metrics.requires_vision and not supports_vision:
                continue

            # Skip if would exceed budget
            estimated_cost = metrics.estimated_tokens * (cost / 1000)
            if budget < int(estimated_cost):
                continue

            fallbacks.append(provider)
            budget -= int(estimated_cost)

        return fallbacks

    def _provider_supports_request(self, provider: AIProviderType, metrics: TriageMetrics) -> bool:
        """Check if provider supports request requirements."""
        _, supports_vision, capabilities = self.PROVIDER_TIERS[provider]

        if metrics.requires_vision and not supports_vision:
            return False

        if metrics.has_code_generation and "code" not in capabilities:
            return False

        return True

    async def triage(self, request: QwenTriageRequest) -> QwenTriageResponse:
        """
        Execute full triage routing for a request.

        Args:
            request: QwenTriageRequest

        Returns:
            QwenTriageResponse with routing decision

        Raises:
            ValueError: If request is invalid
        """
        self.logger.info(f"Triaging request {request.request_id}")

        # Check cache first
        cache_key = hashlib.sha256(request.query.encode()).hexdigest()
        if cache_key in self.cache:
            self.logger.debug(f"Cache hit for request {request.request_id}")
            return self.cache[cache_key]

        # Analyze complexity
        metrics = self.analyze_complexity(request)

        # Determine triage level
        triage_level = self.determine_triage_level(
            metrics, request.max_budget_cents, request.force_provider
        )

        # Select primary provider
        primary_provider = self.select_provider(
            triage_level, metrics, request.preferred_providers, request.force_provider
        )

        # Estimate cost
        cost_per_1k, _, _ = self.PROVIDER_TIERS[primary_provider]
        estimated_cost = int((metrics.estimated_tokens / 1000) * cost_per_1k)

        # Create primary AIProviderContext
        primary_context = AIProviderContext(
            provider=primary_provider,
            model=self._get_model_for_provider(primary_provider),
            request_id=request.request_id,
            session_id=request.session_id,
            priority=self._priority_from_triage_level(triage_level),
            max_tokens=min(metrics.estimated_tokens * 2, 8000),
            context_source=ContextSource.agent_orchestration,
            metadata={
                "triage_level": triage_level.value,
                "complexity": metrics.complexity.value,
                "security_level": metrics.security_level,
            },
            budget_remaining=request.max_budget_cents - estimated_cost,
            fallback_providers=self.build_fallback_chain(
                primary_provider, metrics, request.max_budget_cents - estimated_cost
            ),
        )

        # Build fallback contexts
        fallback_contexts = [
            AIProviderContext(
                provider=provider,
                model=self._get_model_for_provider(provider),
                request_id=request.request_id,
                session_id=request.session_id,
                priority=max(1, self._priority_from_triage_level(triage_level) - 1),
                context_source=ContextSource.agent_orchestration,
                metadata={"fallback": True},
            )
            for provider in self.build_fallback_chain(
                primary_provider, metrics, request.max_budget_cents - estimated_cost
            )
        ]

        reasoning = (
            f"Triage level: {triage_level.value} | "
            f"Complexity: {metrics.complexity.value} | "
            f"Selected: {primary_provider.value} | "
            f"Cost: {estimated_cost} cents"
        )

        response = QwenTriageResponse(
            request_id=request.request_id,
            triage_level=triage_level,
            primary_provider=primary_context,
            fallback_providers=fallback_contexts,
            estimated_cost_cents=estimated_cost,
            reasoning=reasoning,
            metrics={
                "input_length": metrics.input_length,
                "estimated_tokens": metrics.estimated_tokens,
                "complexity": metrics.complexity.value,
                "security_level": metrics.security_level,
            },
        )

        # Cache result
        self.cache[cache_key] = response

        self.logger.info(f"Triage complete: {request.request_id} → {primary_provider.value}")
        return response

    def _get_model_for_provider(self, provider: AIProviderType) -> str:
        """Get default model for provider."""
        models = {
            AIProviderType.claude: "claude-3-5-sonnet-20241022",
            AIProviderType.openai: "gpt-4o",
            AIProviderType.gemini: "gemini-2.0-flash",
            AIProviderType.grok: "grok-3",
            AIProviderType.copilot: "copilot-latest",
            AIProviderType.cursor: "cursor-latest",
            AIProviderType.ollama_local: "qwen2.5:14b",
        }
        return models.get(provider, "unknown")

    def _priority_from_triage_level(self, level: TriageLevel) -> int:
        """Convert triage level to priority (1-10)."""
        levels = {
            TriageLevel.tier0_simple: 3,
            TriageLevel.tier1_standard: 5,
            TriageLevel.tier2_advanced: 7,
            TriageLevel.tier3_premium: 9,
            TriageLevel.tier4_critical: 10,
        }
        return levels.get(level, 5)
