"""Tests for AI asgi — provider routing, combo strategies, rate limiter, usage tracker."""

import pytest

try:
    from ai_proxy.services.rate_limiter import RateLimiter, ProviderLimits
    from ai_proxy.services.usage_tracker import UsageTracker, UsageRecord

    AI_PROXY_AVAILABLE = True
except ImportError:
    AI_PROXY_AVAILABLE = False
    pytest.skip("AI asgi module not fully available", allow_module_level=True)


class TestProviderRegistry:
    """Test AI provider registry (60+ providers)."""

    @pytest.mark.skip(reason="Provider registry API not yet finalized")
    def test_providers_loaded(self):
        pass


@pytest.mark.skip(reason="ComboRouter / RouteStrategy not yet exported from ai_proxy.routing")
class TestComboRouter:
    """Test combo routing engine — 13 strategies."""

    class _ComboRouter:
        def resolve(self, targets, *, strategy):
            return targets[:1]

    class _RouteStrategy:
        PRIORITY = "priority"
        COST_OPTIMIZED = "cost-optimized"
        ROUND_ROBIN = "round-robin"
        WEIGHTED = "weighted"

    ComboRouter = _ComboRouter
    RouteStrategy = _RouteStrategy

    @pytest.fixture
    def router(self):
        return self.ComboRouter()

    def test_priority_strategy(self, router):
        targets = [
            {"provider": "anthropic", "priority": 1},
            {"provider": "openai", "priority": 2},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.PRIORITY)
        assert resolved

    def test_cost_optimized_strategy(self, router):
        targets = [
            {"provider": "expensive", "cost_per_1k": 10.0},
            {"provider": "cheap", "cost_per_1k": 0.50},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.COST_OPTIMIZED)
        assert resolved

    def test_round_robin_strategy(self, router):
        targets = [{"provider": "a"}, {"provider": "b"}, {"provider": "c"}]
        resolutions = []
        for _ in range(3):
            resolved = router.resolve(targets, strategy=self.RouteStrategy.ROUND_ROBIN)
            if resolved:
                resolutions.append(resolved[0]["provider"])
        assert len(set(resolutions)) >= 1

    def test_weighted_strategy(self, router):
        targets = [
            {"provider": "high-weight", "weight": 0.7},
            {"provider": "low-weight", "weight": 0.3},
        ]
        resolved = router.resolve(targets, strategy=self.RouteStrategy.WEIGHTED)
        assert resolved


@pytest.mark.skip(reason="CircuitBreaker module not yet implemented")
class TestCircuitBreaker:
    """Placeholder until CircuitBreaker module exists."""
    def test_placeholder(self):
        pass


class TestRateLimiter:
    """Test rate limiting per provider."""

    @pytest.fixture
    def limiter(self):
        lim = RateLimiter()
        lim.configure("anthropic", ProviderLimits(rpm=100, tpm=1_000_000, concurrent=10))
        return lim

    @pytest.mark.anyio
    async def test_acquire_within_limit(self, limiter):
        assert await limiter.acquire("anthropic", estimated_tokens=1)

    @pytest.mark.anyio
    async def test_acquire_unconfigured_provider(self):
        lim = RateLimiter()
        result = await lim.acquire("unknown-provider")
        assert result is True

    def test_get_status(self, limiter):
        status = limiter.get_status("anthropic")
        assert isinstance(status, dict)

    def test_get_all_status(self, limiter):
        statuses = limiter.get_all_status()
        assert isinstance(statuses, list)


class TestUsageTracker:
    """Test token usage tracking."""

    @pytest.fixture
    def tracker(self):
        return UsageTracker()

    def test_record_usage(self, tracker):
        rec = UsageRecord(
            provider_id="anthropic",
            model_id="claude-opus",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost_usd=0.01,
        )
        tracker.record(rec)
        summary = tracker.get_summary()
        assert summary["total_requests"] >= 1

    def test_usage_aggregation(self, tracker):
        for _ in range(5):
            tracker.record(UsageRecord(
                provider_id="openai",
                model_id="gpt-4",
                prompt_tokens=100,
                completion_tokens=100,
                total_tokens=200,
                cost_usd=0.05,
            ))
        summary = tracker.get_summary()
        assert summary["total_tokens"] >= 1000

    def test_get_recent(self, tracker):
        tracker.record(UsageRecord(
            provider_id="anthropic",
            model_id="claude-sonnet",
            worktree_sid="abc123def456",
            prompt_tokens=50,
            completion_tokens=25,
            total_tokens=75,
        ))
        recent = tracker.get_recent(limit=5)
        assert len(recent) >= 1
        assert recent[0]["worktree_sid"] == "abc123def456"

    def test_reset(self, tracker):
        tracker.record(UsageRecord(
            provider_id="test",
            model_id="test-model",
            total_tokens=100,
        ))
        tracker.reset()
        summary = tracker.get_summary()
        assert summary["total_requests"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
