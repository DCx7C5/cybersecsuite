"""Tests for AIProviderContext and QwenTriageRouter.

Referenz:
    src/llm/ai_provider_context.py — AIProviderContext classes
    src/ai_proxy/routing/qwen_triage.py — QwenTriageRouter
"""
import pytest
from datetime import datetime, timedelta
from llm.ai_provider_context import (
    AIProviderContext,
    AIProviderType,
)
from ai_proxy.routing.qwen_triage import (
    QwenTriageRouter,
    QwenTriageRequest,
    TriageLevel,
    RequestComplexity,
)


class TestAIProviderContext:
    """Test AIProviderContext class."""

    def test_context_creation(self) -> None:
        """Test basic context creation."""
        context = AIProviderContext(
            provider=AIProviderType.claude,
            model="claude-3-5-sonnet-20241022",
            request_id="req-123",
        )

        assert context.provider == AIProviderType.claude
        assert context.request_id == "req-123"
        assert context.priority == 5
        assert context.max_tokens == 4096

    def test_context_expiration(self) -> None:
        """Test context expiration logic."""
        now = datetime.utcnow()
        context = AIProviderContext(
            provider=AIProviderType.claude,
            model="claude-3-5-sonnet-20241022",
            request_id="req-123",
            expires_at=now - timedelta(seconds=1),
        )

        assert context.is_expired

    def test_context_age(self) -> None:
        """Test context age calculation."""
        context = AIProviderContext(
            provider=AIProviderType.claude,
            model="claude-3-5-sonnet-20241022",
            request_id="req-123",
            created_at=datetime.utcnow() - timedelta(seconds=10),
        )

        age = context.age_seconds
        assert 9 < age < 11  # Allow 1 second variance

    def test_context_to_headers(self) -> None:
        """Test converting context to HTTP headers."""
        context = AIProviderContext(
            provider=AIProviderType.claude,
            model="claude-3-5-sonnet-20241022",
            request_id="req-123",
            session_id="sess-456",
            priority=8,
        )

        headers = context.to_headers()

        assert headers["X-AI-Provider"] == "claude"
        assert headers["X-Request-ID"] == "req-123"
        assert headers["X-Session-ID"] == "sess-456"
        assert headers["X-Priority"] == "8"

    def test_context_from_headers(self) -> None:
        """Test creating context from HTTP headers."""
        headers = {
            "X-AI-Provider": "openai",
            "X-AI-Model": "gpt-4o",
            "X-Request-ID": "req-789",
            "X-Priority": "7",
        }

        context = AIProviderContext.from_headers(headers)

        assert context.provider == AIProviderType.openai
        assert context.model == "gpt-4o"
        assert context.request_id == "req-789"
        assert context.priority == 7

    def test_context_schema_validation(self) -> None:
        """Test Pydantic schema validation."""
        from llm.ai_provider_context import AIProviderContextSchema

        schema = AIProviderContextSchema(
            provider=AIProviderType.claude,
            model="claude-3-5-sonnet-20241022",
            request_id="req-123",
            priority=5,
            max_tokens=4096,
            temperature=0.7,
        )

        assert schema.provider == AIProviderType.claude
        assert schema.max_tokens == 4096


class TestQwenTriageRouter:
    """Test QwenTriageRouter class."""

    def test_router_initialization(self) -> None:
        """Test router initialization."""
        router = QwenTriageRouter()
        assert router.cache == {}

    def test_token_estimation(self) -> None:
        """Test token estimation."""
        router = QwenTriageRouter()

        # "Hello, world!" = 13 chars / 4 = 3 tokens (approx)
        tokens = router.estimate_tokens("Hello, world!")
        assert tokens > 0

    def test_complexity_analysis_trivial(self) -> None:
        """Test complexity analysis for trivial request."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Hello",  # Very short
        )

        metrics = router.analyze_complexity(request)
        assert metrics.complexity == RequestComplexity.trivial

    def test_complexity_analysis_complex(self) -> None:
        """Test complexity analysis for complex request."""
        router = QwenTriageRouter()
        query = "Analyze this " * 200  # Long query
        request = QwenTriageRequest(
            request_id="req-1",
            query=query,
        )

        metrics = router.analyze_complexity(request)
        assert metrics.complexity in [
            RequestComplexity.complex,
            RequestComplexity.critical,
        ]

    def test_complexity_with_security_keywords(self) -> None:
        """Test complexity analysis detects security context."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Analyze security vulnerabilities in our system",
        )

        metrics = router.analyze_complexity(request)
        assert metrics.security_level > 1

    def test_triage_level_determination_simple(self) -> None:
        """Test triage level for simple request with budget."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Hello",
            max_budget_cents=100,
        )

        metrics = router.analyze_complexity(request)
        level = router.determine_triage_level(metrics, 100, None)

        assert level == TriageLevel.tier0_simple

    def test_triage_level_determination_low_budget(self) -> None:
        """Test triage level with insufficient budget."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Analyze security vulnerabilities " * 50,
            max_budget_cents=10,  # Very low budget
        )

        metrics = router.analyze_complexity(request)
        level = router.determine_triage_level(metrics, 10, None)

        assert level == TriageLevel.tier0_simple

    def test_provider_selection(self) -> None:
        """Test provider selection based on triage level."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Hello",
        )

        metrics = router.analyze_complexity(request)
        provider = router.select_provider(
            TriageLevel.tier0_simple, metrics, [], None
        )

        assert provider == AIProviderType.ollama_local

    def test_provider_selection_prefers_user_choice(self) -> None:
        """Test that provider selection respects user preferences."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Hello",
        )

        metrics = router.analyze_complexity(request)
        provider = router.select_provider(
            TriageLevel.tier0_simple,
            metrics,
            [AIProviderType.claude],
            None,
        )

        # Should prefer user's choice over tier0
        assert provider == AIProviderType.claude

    def test_fallback_chain_building(self) -> None:
        """Test building fallback provider chain."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-1",
            query="Test query",
        )

        metrics = router.analyze_complexity(request)
        fallbacks = router.build_fallback_chain(
            AIProviderType.claude, metrics, 1000
        )

        assert len(fallbacks) > 0
        assert AIProviderType.claude not in fallbacks  # Primary not in fallbacks

    @pytest.mark.asyncio
    async def test_full_triage_routing(self) -> None:
        """Test full triage routing process."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-123",
            query="Analyze potential security threats in network logs",
            session_id="sess-456",
            max_budget_cents=5000,
        )

        response = await router.triage(request)

        assert response.request_id == "req-123"
        assert response.triage_level is not None
        assert response.primary_provider is not None
        assert response.primary_provider.model is not None
        assert response.estimated_cost_cents >= 0

    @pytest.mark.asyncio
    async def test_triage_with_forced_provider(self) -> None:
        """Test triage with forced provider."""
        router = QwenTriageRouter()
        request = QwenTriageRequest(
            request_id="req-123",
            query="Test",
            force_provider=AIProviderType.claude,
        )

        response = await router.triage(request)

        assert response.primary_provider.provider == AIProviderType.claude
        assert response.triage_level == TriageLevel.tier4_critical


class TestMarketplaceAPI:
    """Test marketplace API endpoints."""

    @pytest.mark.asyncio
    async def test_list_marketplace_items(self, client) -> None:
        """Test listing marketplace items."""
        response = await client.get("/api/v1/marketplace/items")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_list_items_with_filter(self, client) -> None:
        """Test listing items with kind filter."""
        response = await client.get("/api/v1/marketplace/items?kind=agent")
        assert response.status_code == 200

        data = response.json()
        for item in data.get("items", []):
            assert item.get("kind") == "agent"

    @pytest.mark.asyncio
    async def test_list_items_invalid_kind(self, client) -> None:
        """Test that invalid kind filter returns error."""
        response = await client.get("/api/v1/marketplace/items?kind=invalid")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_marketplace_item(self, client) -> None:
        """Test getting single marketplace item."""
        # First list to get an item ID
        list_response = await client.get("/api/v1/marketplace/items")
        items = list_response.json().get("items", [])

        if items:
            item_id = items[0]["id"]
            response = await client.get(f"/api/v1/marketplace/items/{item_id}")
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == item_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_item(self, client) -> None:
        """Test that nonexistent item returns 404."""
        response = await client.get("/api/v1/marketplace/items/nonexistent-123")
        assert response.status_code == 404


class TestJSONValidation:
    """Test JSON validation components."""

    def test_finding_response_validation(self) -> None:
        """Test FindingResponse validation."""
        from ai_proxy.validation.json_response import FindingResponse

        finding = FindingResponse(
            finding_id="FIND-001",
            severity="HIGH",
            title="Test Finding",
            description="Test finding description",
        )

        assert finding.severity == "HIGH"
        assert finding.finding_id == "FIND-001"

    def test_finding_response_invalid_severity(self) -> None:
        """Test FindingResponse rejects invalid severity."""
        from ai_proxy.validation.json_response import FindingResponse
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            FindingResponse(
                finding_id="FIND-001",
                severity="INVALID",
                title="Test",
                description="Test",
            )

    def test_response_validator_extract_json(self) -> None:
        """Test JSON extraction from response."""
        from ai_proxy.validation.json_response import ResponseValidator

        validator = ResponseValidator()

        # Test markdown code block
        response = '```json\n{"key": "value"}\n```'
        extracted = validator._extract_json(response)
        assert "key" in extracted

    def test_token_optimizer_estimation(self) -> None:
        """Test token estimation."""
        from ai_proxy.validation.json_response import TokenOptimizer

        optimizer = TokenOptimizer()
        tokens = optimizer.estimate_tokens("Hello, world!")

        assert tokens > 0

    def test_few_shot_examples_retrieval(self) -> None:
        """Test few-shot examples retrieval."""
        from ai_proxy.validation.json_response import FewShotExamples

        examples = FewShotExamples.get_finding_examples(limit=2)
        assert len(examples) <= 2

        timeline = FewShotExamples.get_timeline_examples(limit=1)
        assert len(timeline) <= 1

    def test_few_shot_prompt_building(self) -> None:
        """Test few-shot prompt building."""
        from ai_proxy.validation.json_response import FewShotExamples

        prompt = FewShotExamples.build_few_shot_prompt("finding", examples_count=1)
        assert "Example 1" in prompt
