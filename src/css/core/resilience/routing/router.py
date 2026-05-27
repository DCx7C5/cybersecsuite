"""ComboRouter — full request execution with resilience."""

from collections.abc import Awaitable, Callable
from typing import Any

from css.core.logger import getLogger
from css.core.messages.types import LLMResponse
from css.core.resilience.routing.budget import BudgetGuard, budget_guard
from css.core.resilience.routing.circuit_breaker import CircuitBreaker, circuit_breaker
from css.core.resilience.routing.rate_limiter import RateLimiter, rate_limiter
from css.core.resilience.routing.registry import ComboRegistry, combo_registry
from css.core.resilience.routing.strategies import _apply_strategy
from css.core.resilience.routing.usage_tracker import UsageRecord, UsageTracker, usage_tracker

logger = getLogger(__name__)


class ComboRouter:
    """Orchestrator for resilient combo-based provider routing."""

    def __init__(
        self,
        registry: ComboRegistry | None = None,
        budget: BudgetGuard | None = None,
        breaker: CircuitBreaker | None = None,
        limiter: RateLimiter | None = None,
        tracker: UsageTracker | None = None,
        call_target: Callable[[str, str, list[dict[str, object]], dict[str, Any]], Awaitable[LLMResponse]] | None = None,
    ) -> None:
        self._registry = registry or combo_registry
        self._budget = budget or budget_guard
        self._breaker = breaker or circuit_breaker
        self._limiter = limiter or rate_limiter
        self._tracker = tracker or usage_tracker
        self._call_target = call_target

    def set_call_target(
        self,
        call_target: Callable[[str, str, list[dict[str, object]], dict[str, Any]], Awaitable[LLMResponse]],
    ) -> None:
        self._call_target = call_target

    async def route(
        self,
        combo_id: str,
        messages: list[dict[str, object]],
        **kw: Any,
    ) -> LLMResponse:
        combo = self._registry.get(combo_id)
        if combo is None:
            raise RuntimeError(f"Unknown combo_id: {combo_id}")

        targets = _apply_strategy(combo.targets, combo.strategy, combo_id)
        if not targets:
            raise RuntimeError(f"No active targets for combo: {combo_id}")

        fallback_on_error = kw.pop("fallback_on_error", True)
        errors: list[str] = []

        for target in targets:
            target_key = f"{target.provider}:{target.model_id}"

            if self._breaker.is_open(target_key):
                errors.append(f"{target_key}: circuit open")
                continue

            if not self._budget.check_budget(combo_id, combo.budget_usd):
                errors.append(f"{target_key}: budget exhausted")
                continue

            if self._limiter is not None:
                acquired = await self._limiter.wait_and_acquire(target_key)
                if not acquired:
                    errors.append(f"{target_key}: rate limited")
                    continue

            try:
                if self._call_target is None:
                    raise RuntimeError(f"call_target not set; cannot invoke {target_key}")

                response = await self._call_target(target.provider, target.model_id, messages, kw)

                self._breaker.record_success(target_key)
                if self._limiter is not None:
                    self._limiter.release(target_key)

                usage = response.usage or {}
                self._tracker.record(
                    UsageRecord(
                        provider_id=target.provider,
                        model_id=target.model_id,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        cost_usd=usage.get("cost", 0.0),
                        latency_ms=0.0,
                        request_id=kw.get("request_id"),
                    )
                )

                if response.usage:
                    cost = response.usage.get("cost", 0.0) or 0.0
                    self._budget.record_cost(combo_id, float(cost))

                return response

            except Exception as exc:
                self._breaker.record_failure(target_key)
                if self._limiter is not None:
                    self._limiter.release(target_key)
                errors.append(f"{target_key}: {exc}")
                logger.warning("Target %s failed for combo %s: %s", target_key, combo_id, exc)
                if not fallback_on_error:
                    raise

        raise RuntimeError(
            f"All targets failed for combo {combo_id}: {'; '.join(errors)}"
        )


combo_router: ComboRouter = ComboRouter()
