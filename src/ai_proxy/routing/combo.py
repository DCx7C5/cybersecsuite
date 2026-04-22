"""
Routing Engine — multi-provider combo routing with 13 strategies,
4-tier free-first smart fallback, budget guards, and context relay.

Resolve combo targets, apply strategy,
execute with fallback on failure, circuit breaker per target.
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ai_proxy.executors.base import BaseExecutor, ExecutorResult, get_executor
from ai_proxy.providers.registry import (
    ApiFormat,
    AuthType,
    ProviderConfig,
    get_provider,
    get_enabled_providers,
)
from ai_proxy.translators.core import translate_request, translate_response

logger = logging.getLogger("ai_proxy.routing")

# QoL injection — imported lazily to avoid circular deps at module load time
def _qol_inject(
    body: dict[str, Any],
    session_id: str | None,
    agent_name: str | None = None,
) -> dict[str, Any]:
    """Apply QoL output-control directives to *body* if any toggles are active.

    Scope cascade (T017): session → project (if session has no toggles).
    Agent preset (T018): agent_name overrides scope if a binding exists.
    """
    try:
        from ai_proxy.qol_controls.manager import get_manager
        scope = "session" if session_id else "project"
        return get_manager().inject_into_request(
            body, scope=scope, session_id=session_id, agent_name=agent_name
        )
    except Exception:
        # Never break routing due to QoL errors
        return body


# ── 13 Combo Strategies ─────────────────────────────────

class Strategy(str, Enum):
    PRIORITY = "priority"               # Ordered list, first success wins
    ROUND_ROBIN = "round-robin"         # Rotate through targets
    COST_OPTIMIZED = "cost-optimized"   # Cheapest first
    WEIGHTED = "weighted"               # Probabilistic by weight
    RANDOM = "random"                   # Shuffle randomly
    LEAST_USED = "least-used"           # Fewest past requests first
    FILL_FIRST = "fill-first"           # Fill quota of first before next
    P2C = "p2c"                         # Power of two choices
    STRICT_RANDOM = "strict-random"     # Pure random, no dedup
    AUTO = "auto"                       # Auto-select based on context
    LKGP = "lkgp"                       # Last known good provider
    CONTEXT_OPTIMIZED = "context-optimized"  # Best context window match
    CONTEXT_RELAY = "context-relay"     # Relay context across accounts


@dataclass
class ComboTarget:
    provider_id: str
    model_id: str
    weight: float = 1.0
    enabled: bool = True


@dataclass
class ComboConfig:
    id: str
    name: str
    strategy: Strategy = Strategy.PRIORITY
    targets: list[ComboTarget] = field(default_factory=list)
    enabled: bool = True
    budget_usd: float | None = None  # Max budget for this combo


@dataclass
class ResolvedTarget:
    provider: ProviderConfig
    model_id: str
    executor: BaseExecutor
    weight: float = 1.0


# ── Circuit Breaker ──────────────────────────────────────────────────────────

@dataclass
class _CircuitState:
    failures: int = 0
    last_failure: float = 0.0
    open_until: float = 0.0

    THRESHOLD: int = 5
    RECOVERY_SECONDS: float = 60.0

    @property
    def is_open(self) -> bool:
        if self.failures < self.THRESHOLD:
            return False
        return time.monotonic() < self.open_until

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure = time.monotonic()
        if self.failures >= self.THRESHOLD:
            self.open_until = time.monotonic() + self.RECOVERY_SECONDS

    def record_success(self) -> None:
        self.failures = 0
        self.open_until = 0.0


_circuit_breakers: dict[str, _CircuitState] = {}


def _get_circuit(key: str) -> _CircuitState:
    if key not in _circuit_breakers:
        _circuit_breakers[key] = _CircuitState()
    return _circuit_breakers[key]


# ── State tracking ───────────────────────────────────────────────────────────

_usage_counts: dict[str, int] = {}
_rr_index: dict[str, int] = {}
_last_good: dict[str, str] = {}  # combo_id -> "provider:model"
_context_relay_state: dict[str, list[dict[str, Any]]] = {}  # session -> messages


# ── Budget Guard ─────────────────────────────────────────────────────────────

class BudgetGuard:
    """Track spending per tier and enforce budget limits."""

    def __init__(self) -> None:
        self._spent: dict[str, float] = {}  # tier/combo -> USD spent

    def record_cost(self, key: str, cost_usd: float) -> None:
        self._spent[key] = self._spent.get(key, 0.0) + cost_usd

    def check_budget(self, key: str, budget_usd: float | None) -> bool:
        """Return True if under budget or no budget set."""
        if budget_usd is None:
            return True
        return self._spent.get(key, 0.0) < budget_usd

    def get_spent(self, key: str) -> float:
        return self._spent.get(key, 0.0)

    def get_all(self) -> dict[str, float]:
        return dict(self._spent)

    def reset(self, key: str | None = None) -> None:
        if key:
            self._spent.pop(key, None)
        else:
            self._spent.clear()


budget_guard = BudgetGuard()


# ── Resolve targets ──────────────────────────────────────────────────────────

def resolve_targets(combo: ComboConfig) -> list[ResolvedTarget]:
    """Expand combo config into ordered ResolvedTarget list."""
    resolved: list[ResolvedTarget] = []
    for t in combo.targets:
        if not t.enabled:
            continue
        provider = get_provider(t.provider_id)
        if provider is None or not provider.is_available:
            continue
        resolved.append(ResolvedTarget(
            provider=provider,
            model_id=t.model_id,
            executor=get_executor(provider),
            weight=t.weight,
        ))
    return resolved


def _apply_strategy(targets: list[ResolvedTarget], strategy: Strategy, combo_id: str) -> list[ResolvedTarget]:
    """Reorder targets according to strategy."""
    if not targets:
        return targets

    if strategy == Strategy.PRIORITY:
        return targets

    if strategy == Strategy.RANDOM:
        shuffled = list(targets)
        random.shuffle(shuffled)
        return shuffled

    if strategy == Strategy.STRICT_RANDOM:
        return [random.choice(targets)]

    if strategy == Strategy.ROUND_ROBIN:
        idx = _rr_index.get(combo_id, 0)
        _rr_index[combo_id] = (idx + 1) % len(targets)
        return targets[idx:] + targets[:idx]

    if strategy == Strategy.COST_OPTIMIZED:
        return sorted(targets, key=lambda t: _target_cost(t))

    if strategy == Strategy.WEIGHTED:
        weighted = []
        for t in targets:
            weighted.extend([t] * max(1, int(t.weight)))
        random.shuffle(weighted)
        seen: set[str] = set()
        result = []
        for t in weighted:
            key = f"{t.provider.id}:{t.model_id}"
            if key not in seen:
                seen.add(key)
                result.append(t)
        return result

    if strategy == Strategy.LEAST_USED:
        return sorted(targets, key=lambda t: _usage_counts.get(f"{t.provider.id}:{t.model_id}", 0))

    if strategy == Strategy.FILL_FIRST:
        return targets

    if strategy == Strategy.P2C:
        # Power of two choices: pick 2 random, choose the one with fewer uses
        if len(targets) < 2:
            return targets
        a, b = random.sample(targets, 2)
        a_uses = _usage_counts.get(f"{a.provider.id}:{a.model_id}", 0)
        b_uses = _usage_counts.get(f"{b.provider.id}:{b.model_id}", 0)
        winner = a if a_uses <= b_uses else b
        others = [t for t in targets if t is not winner]
        return [winner] + others

    if strategy == Strategy.LKGP:
        # Last known good provider — move it to front
        last = _last_good.get(combo_id)
        if last:
            for i, t in enumerate(targets):
                if f"{t.provider.id}:{t.model_id}" == last:
                    return [targets[i]] + targets[:i] + targets[i + 1:]
        return targets

    if strategy == Strategy.CONTEXT_OPTIMIZED:
        # Sort by context window size (largest first for long conversations)
        def _context_window(t: Any) -> int:
            m = t.provider.get_model(t.model_id)
            return -(m.context_window if m else 0)
        return sorted(targets, key=_context_window)

    if strategy in (Strategy.CONTEXT_RELAY, Strategy.AUTO):
        # Context relay uses priority order but with session continuity
        # Auto delegates to cost-optimized
        return sorted(targets, key=lambda t: _target_cost(t))

    return targets


def _target_cost(t: ResolvedTarget) -> float:
    """Get combined input+output cost for sorting."""
    m = t.provider.get_model(t.model_id)
    if m is None:
        return float("inf")
    return m.cost.input + m.cost.output


# ── Core routing ─────────────────────────────────────────────────────────────

async def route_request(
    body: dict[str, Any],
    combo: ComboConfig,
    stream: bool = False,
    session_id: str | None = None,
    agent_name: str | None = None,
) -> ExecutorResult:
    """
    Route a request through a combo config. Tries targets in strategy order,
    falls back on failure. Returns first successful result.

    Supports:
    - Budget guard: skip targets if combo budget exceeded
    - Context relay: carry conversation context across provider switches
    - LKGP: remember last successful provider
    """
    # Budget check
    if not budget_guard.check_budget(combo.id, combo.budget_usd):
        return ExecutorResult(
            status_code=429,
            error=f"Budget exhausted for combo '{combo.name}' "
                  f"(${budget_guard.get_spent(combo.id):.4f} / ${combo.budget_usd:.4f})",
        )

    targets = resolve_targets(combo)
    ordered = _apply_strategy(targets, combo.strategy, combo.id)

    if not ordered:
        return ExecutorResult(
            status_code=503,
            error="No available targets in combo — check provider API keys and config",
        )

    # Context relay: inject previous context if switching providers mid-session
    if combo.strategy == Strategy.CONTEXT_RELAY and session_id:
        prev_context = _context_relay_state.get(session_id, [])
        if prev_context:
            messages = body.get("messages", [])
            # Prepend context summary as system message
            context_summary = _build_context_summary(prev_context)
            if context_summary:
                body = {**body, "messages": [
                    {"role": "system", "content": f"[Context from previous provider session]\n{context_summary}"},
                    *messages,
                ]}

    # QoL: inject output-control directives before dispatch
    body = _qol_inject(body, session_id, agent_name=agent_name)

    last_result: ExecutorResult | None = None

    for target in ordered:
        circuit_key = f"{target.provider.id}:{target.model_id}"
        circuit = _get_circuit(circuit_key)

        if circuit.is_open:
            logger.info("Circuit open for %s, skipping", circuit_key)
            continue

        # Translate request if provider uses non-OpenAI format
        translated_body = translate_request(body, ApiFormat.OPENAI, target.provider.api_format)

        try:
            result = await target.executor.execute(
                body=translated_body,
                model=target.model_id,
                stream=stream,
            )

            if result.ok:
                circuit.record_success()
                _usage_counts[circuit_key] = _usage_counts.get(circuit_key, 0) + 1
                _last_good[combo.id] = circuit_key

                # Translate response back to OpenAI format if needed
                if result.body and target.provider.api_format != ApiFormat.OPENAI:
                    result.body = translate_response(result.body, target.provider.api_format, ApiFormat.OPENAI)

                # Track cost in budget guard
                if result.body:
                    usage = result.body.get("usage", {})
                    model_cfg = target.provider.get_model(target.model_id)
                    if model_cfg and usage:
                        cost = (
                            (usage.get("prompt_tokens", 0) / 1_000_000) * model_cfg.cost.input +
                            (usage.get("completion_tokens", 0) / 1_000_000) * model_cfg.cost.output
                        )
                        budget_guard.record_cost(combo.id, cost)

                # Context relay: store messages for session continuity
                if session_id and combo.strategy == Strategy.CONTEXT_RELAY:
                    _store_context_relay(session_id, body, result.body)

                return result
            else:
                circuit.record_failure()
                last_result = result
                logger.warning(
                    "Target %s failed with %d: %s — trying next",
                    circuit_key, result.status_code, (result.error or "")[:200],
                )

        except Exception as exc:
            circuit.record_failure()
            last_result = ExecutorResult(
                status_code=502,
                error=f"{type(exc).__name__}: {exc}",
                provider_id=target.provider.id,
                model_id=target.model_id,
            )
            logger.exception("Target %s raised exception", circuit_key)

        finally:
            await target.executor.close()

    return last_result or ExecutorResult(status_code=503, error="All targets exhausted")


# ── Context Relay helpers ────────────────────────────────────────────────────

def _build_context_summary(messages: list[dict[str, Any]]) -> str:
    """Summarize previous conversation context for relay."""
    parts = []
    for msg in messages[-10:]:  # Last 10 messages max
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if isinstance(content, str) and content:
            snippet = content[:500] + "..." if len(content) > 500 else content
            parts.append(f"{role}: {snippet}")
    return "\n".join(parts)


def _store_context_relay(
    session_id: str,
    request_body: dict[str, Any],
    response_body: dict[str, Any] | None,
) -> None:
    """Store messages from this exchange for future context relay."""
    if session_id not in _context_relay_state:
        _context_relay_state[session_id] = []

    # Add user messages
    for msg in request_body.get("messages", []):
        if msg.get("role") in ("user", "assistant"):
            _context_relay_state[session_id].append(msg)

    # Add assistant response
    if response_body:
        choices = response_body.get("choices", [])
        if choices and choices[0].get("message"):
            _context_relay_state[session_id].append(choices[0]["message"])

    # Cap at 50 messages
    if len(_context_relay_state[session_id]) > 50:
        _context_relay_state[session_id] = _context_relay_state[session_id][-50:]


# ── 4-Tier Smart Fallback (Free-First) ───────────────────────────────────────

class RoutingTier(str, Enum):
    FREE = "free"          # Tier 1: Free providers (Pollinations, Ollama, Galadriel, browser)
    BUDGET = "budget"      # Tier 2: Cheap providers (<$1/M tokens)
    STANDARD = "standard"  # Tier 3: Standard pricing ($1-5/M tokens)
    PREMIUM = "premium"    # Tier 4: Premium providers (>$5/M tokens)


def _classify_tier(provider: ProviderConfig, model_id: str) -> RoutingTier:
    """Classify a provider+model into a pricing tier."""
    if provider.is_free or provider.auth_type in (AuthType.NONE, AuthType.BROWSER):
        return RoutingTier.FREE

    model = provider.get_model(model_id)
    if model is None:
        return RoutingTier.STANDARD

    avg_cost = (model.cost.input + model.cost.output) / 2
    if avg_cost == 0:
        return RoutingTier.FREE
    if avg_cost < 1.0:
        return RoutingTier.BUDGET
    if avg_cost <= 5.0:
        return RoutingTier.STANDARD
    return RoutingTier.PREMIUM



async def smart_route(
    body: dict[str, Any],
    stream: bool = False,
    prefer_free: bool = False,
    max_cost_per_1k: float | None = None,
    budget_usd: float | None = None,
    session_id: str | None = None,
    agent_name: str | None = None,
) -> ExecutorResult:
    """
    4-tier free-first smart routing with budget guard.

    Tier order when prefer_free=True:
      1. FREE:     Pollinations, Ollama, LM Studio, Galadriel, browser providers
      2. BUDGET:   DeepSeek, Groq, Cerebras, DeepInfra, nScale, etc. (<$1/M)
      3. STANDARD: Mistral, Together, Fireworks, etc. ($1-5/M)
      4. PREMIUM:  OpenAI, Anthropic, Gemini, xAI, etc. (>$5/M)

    When prefer_free=False: all tiers mixed, sorted by cost-optimized.
    """
    all_providers = get_enabled_providers()
    if not all_providers:
        return ExecutorResult(status_code=503, error="No providers configured — set API keys in environment")

    model_id = body.get("model", "")

    # Build targets grouped by tier
    tier_targets: dict[RoutingTier, list[ComboTarget]] = {
        RoutingTier.FREE: [],
        RoutingTier.BUDGET: [],
        RoutingTier.STANDARD: [],
        RoutingTier.PREMIUM: [],
    }

    for p in all_providers:
        # Try exact model match first
        m = p.get_model(model_id)
        if m:
            if max_cost_per_1k is not None and m.cost.input > max_cost_per_1k:
                continue
            tier = _classify_tier(p, m.id)
            tier_targets[tier].append(ComboTarget(provider_id=p.id, model_id=m.id))

    # If no exact match, use first model from each provider
    if not any(tier_targets.values()):
        for p in all_providers:
            if p.models:
                m = p.models[0]
                if max_cost_per_1k is not None and m.cost.input > max_cost_per_1k:
                    continue
                tier = _classify_tier(p, m.id)
                tier_targets[tier].append(ComboTarget(provider_id=p.id, model_id=m.id))

    # Build ordered target list based on preference
    if prefer_free:
        # 4-tier cascade: free → budget → standard → premium
        ordered_targets: list[ComboTarget] = []
        for tier in (RoutingTier.FREE, RoutingTier.BUDGET, RoutingTier.STANDARD, RoutingTier.PREMIUM):
            # Sort each tier by cost
            tier_list = tier_targets[tier]
            tier_list.sort(key=lambda t: _combo_target_cost(t))
            ordered_targets.extend(tier_list)
    else:
        # Cost-optimized across all tiers
        ordered_targets = []
        for targets in tier_targets.values():
            ordered_targets.extend(targets)
        ordered_targets.sort(key=lambda t: _combo_target_cost(t))

    if not ordered_targets:
        return ExecutorResult(
            status_code=404,
            error=f"Model '{model_id}' not found in any configured provider",
        )

    # Log tier distribution
    tier_counts = {t.value: len(tl) for t, tl in tier_targets.items() if tl}
    logger.info("Smart route: %d targets across tiers %s (prefer_free=%s)", len(ordered_targets), tier_counts, prefer_free)

    strategy = Strategy.COST_OPTIMIZED if not prefer_free else Strategy.PRIORITY
    combo = ComboConfig(
        id="smart-route",
        name="smart-route",
        strategy=strategy,
        targets=ordered_targets,
        budget_usd=budget_usd,
    )
    return await route_request(body, combo, stream=stream, session_id=session_id, agent_name=agent_name)


def _combo_target_cost(t: ComboTarget) -> float:
    """Get cost for a ComboTarget for sorting."""
    p = get_provider(t.provider_id)
    if p is None:
        return float("inf")
    m = p.get_model(t.model_id)
    if m is None:
        return float("inf")
    return m.cost.input + m.cost.output


# ── Cleanup ──────────────────────────────────────────────────────────────────

async def cleanup_executors() -> None:
    """Close all cached executor HTTP clients and reset state."""
    _circuit_breakers.clear()
    _usage_counts.clear()
    _rr_index.clear()
    _last_good.clear()
    _context_relay_state.clear()
    budget_guard.reset()


# ── Public accessors (avoids protected-member access from dashboard) ─────────

def get_circuit_breaker_status() -> list[dict[str, object]]:
    """Return circuit breaker state for all targets."""
    return [
        {
            "target": key,
            "state": "open" if cb.is_open else "closed",
            "failures": cb.failures,
            "last_failure": cb.last_failure,
        }
        for key, cb in _circuit_breakers.items()
    ]


def get_usage_counts() -> dict[str, int]:
    """Return per-provider usage counts."""
    return dict(_usage_counts)


