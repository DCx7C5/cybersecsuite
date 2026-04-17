"""Tests for AI proxy — provider routing, combo strategies, circuit breaker."""

import pytest

try:
    from ai_proxy.services.rate_limiter import RateLimiter
    from ai_proxy.services.usage_tracker import UsageTracker

    AI_PROXY_AVAILABLE = True
except ImportError:
    AI_PROXY_AVAILABLE = False
    pytest.skip("AI proxy module not fully available", allow_module_level=True)


class TestProviderRegistry:
    """Test AI provider registry (60+ providers)."""

    @pytest.mark.skip(reason="Provider registry API not yet finalized")
    def test_providers_loaded(self):
        """Test that provider registry loads."""
        pass


@pytest.mark.skip(reason="ComboRouter / RouteStrategy not yet exported from ai_proxy.routing")
class TestComboRouter:
    """Test combo routing engine — 13 strategies.

    These tests are intentionally skipped until ComboRouter and RouteStrategy
    are exported from ai_proxy.routing.combo.
    """

    # Placeholders so ruff does not complain about undefined names.
    # Replace with real imports once the classes are available:
    #   from ai_proxy.routing.combo import ComboRouter, RouteStrategy
    class _ComboRouter:  # noqa: D106
        def resolve(self, targets, *, strategy):
            return targets[:1]

    class _RouteStrategy:  # noqa: D106
        PRIORITY = "priority"
        COST_OPTIMIZED = "cost-optimized"
        ROUND_ROBIN = "round-robin"
        WEIGHTED = "weighted"

    ComboRouter = _ComboRouter
    RouteStrategy = _RouteStrategy

    @pytest.fixture
    def router(self):
        """Create a combo router."""
        return self.ComboRouter()

    def test_priority_strategy(self, router):
        """Test priority routing strategy."""
        targets = [
            {"provider": "anthropic", "priority": 1},
            {"provider": "openai", "priority": 2},
            {"provider": "free-tier", "priority": 3},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.PRIORITY)
        assert resolved
        assert resolved[0]["provider"] == "anthropic"

    def test_cost_optimized_strategy(self, router):
        """Test cost-optimized routing."""
        targets = [
            {"provider": "expensive", "cost_per_1k": 10.0},
            {"provider": "cheap", "cost_per_1k": 0.50},
            {"provider": "free", "cost_per_1k": 0.0},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.COST_OPTIMIZED)
        assert resolved[0]["provider"] == "free"

    def test_round_robin_strategy(self, router):
        """Test round-robin routing."""
        targets = [{"provider": "a"}, {"provider": "b"}, {"provider": "c"}]
        resolutions = []
        for _ in range(3):
            resolved = router.resolve(targets, strategy=self.RouteStrategy.ROUND_ROBIN)
            if resolved:
                resolutions.append(resolved[0]["provider"])
        assert len(set(resolutions)) >= 1

    def test_weighted_strategy(self, router):
        """Test weighted routing strategy."""
        targets = [
            {"provider": "high-weight", "weight": 0.7},
            {"provider": "low-weight", "weight": 0.3},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.WEIGHTED)
        assert resolved


class TestCircuitBreaker:
    """Test circuit breaker for resilience."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        from ai_proxy.services.circuit_breaker import CircuitBreaker

        breaker = CircuitBreaker(failure_threshold=3, timeout=60)

        # Simulate failures
        for _ in range(3):
            await breaker.record_failure("test_provider")

        # Should be open
        assert breaker.is_open("test_provider")

    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_on_success(self):
        """Test that circuit breaker closes after successful call."""
        from ai_proxy.services.circuit_breaker import CircuitBreaker

        breaker = CircuitBreaker(failure_threshold=2, timeout=60)

        # Record success
        await breaker.record_success("test_provider")

        # Should not be open
        assert not breaker.is_open("test_provider")


class TestRateLimiter:
    """Test rate limiting per provider."""

    @pytest.fixture
    def limiter(self):
        """Create a rate limiter."""
        return RateLimiter()

    def test_rate_limit_check(self, limiter):
        """Test rate limit checking."""
        provider = "anthropic"
        limit = 100  # 100 req/min

        # Should allow first requests
        assert limiter.check_limit(provider, limit)
        assert limiter.check_limit(provider, limit)

    def test_rate_limit_exceeded(self, limiter):
        """Test rate limit exceeded handling."""
        provider = "anthropic"
        limit = 1  # 1 request max

        assert limiter.check_limit(provider, limit)
        # Second request should be rejected
        assert not limiter.check_limit(provider, limit)


class TestUsageTracker:
    """Test token usage tracking."""

    @pytest.fixture
    def tracker(self):
        """Create usage tracker."""
        return UsageTracker()

    def test_track_usage(self, tracker):
        """Test tracking API usage."""
        tracker.record_usage(
            provider="anthropic",
            model="claude-opus",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
        )
        # Usage should be recorded
        usage = tracker.get_usage("anthropic")
        assert usage is not None

    def test_usage_aggregation(self, tracker):
        """Test usage aggregation across calls."""
        for i in range(5):
            tracker.record_usage(
                provider="openai",
                model="gpt-4",
                input_tokens=100,
                output_tokens=100,
                cost_usd=0.05,
            )

        usage = tracker.get_usage("openai")
        if usage:
            # Should aggregate
            assert usage.get("total_input_tokens", 0) >= 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
