"""
Routing Engine — multi-provider combo routing with 13 strategies,
4-tier free-first smart fallback, budget guards, and context relay.

Resolve combo targets, apply strategy,
execute with fallback on failure, circuit breaker per target.
"""
from __future__ import annotations

import logging
import os
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

# ── QoL Output-Control Injection Hook ───────────────────────────────────────
# T005: Inject QoL directives before provider dispatch
# Lazy import prevents circular dependency at module load time.
# Injection is non-blocking: errors do not break routing (T020).

def _qol_inject(
    body: dict[str, Any],
    session_id: str | None,
    agent_name: str | None = None,
) -> dict[str, Any]:
    """
    Apply QoL output-control directives to request body if toggles are active.

    Hook behavior:
      • Loads settings per scope (session → project cascade per T017)
      • Agent-level preset overrides scope settings (T018)
      • Builds injection fragment and prepends to system prompt
      • Validates toggle combinations for security (T019)
      • Never blocks routing on error; returns unmodified body (T020)

    Args:
        body        — OpenAI-compatible request dict to enhance
        session_id  — optional session identifier for scope resolution
        agent_name  — optional agent name for preset lookup

    Returns:
        Modified body dict with QoL system prompt prepended, or original body on error.

    References:
        • T016: Emit telemetry event (qol.injection) with toggle metadata
        • T017: Scope cascade — session → project if session empty
        • T018: Agent preset — agent_name binding overrides scope
        • T019: Security validation — reject dangerous toggle combos
        • T020: Non-blocking error handling — never break routing
        • plan.md Phase 1 QoL Core — detailed spec
    """
    try:
        # Load QoL manager
        from ai_proxy.qol_controls.manager import get_manager
        
        # Resolve scope: use session if available, fall back to project
        scope = "session" if session_id else "project"
        
        # Load settings (with cascade and agent preset resolution)
        # and inject into request (prepend to system prompt)
        manager = get_manager()
        if manager is None:
            return body
            
        return manager.inject_into_request(
            body, scope=scope, session_id=session_id, agent_name=agent_name
        )
    except Exception as exc:
        # T020: Never break routing due to QoL errors
        # Log for observability but proceed with unmodified request
        logger.warning(
            "qol_inject failed (non-blocking): %s — routing proceeds without QoL injection",
            f"{type(exc).__name__}: {exc}"
        )
        return body


# ── WebLLM Routing Decision Flow Documentation (T026) ──────────────────────
# 
# When webllm: true is specified in a request:
#
#   1. REQUEST VALIDATION & CONFIG CHECK
#      ├─ Check if webllm=True or body["webllm"]=True
#      ├─ Load WEBLLM_CONFIG from environment (backend_url, fallback_on_error, etc.)
#      └─ Establish decision tree for target routing
#
#   2. TARGET CLASSIFICATION
#      ├─ BROWSER TARGETS: provider.auth_type == AuthType.BROWSER
#      │  └─ Includes: Playwright, Selenium, Puppeteer, browser automation providers
#      └─ STANDARD TARGETS: all other providers (Claude, ChatGPT, Grok, DeepSeek, etc.)
#
#   3. ROUTING STRATEGY SELECTION
#      ├─ IF browser targets available AND fallback_on_error=True:
#      │  └─ Route = [browser_targets] + [standard_targets]  (browser-first with fallback)
#      ├─ ELIF browser targets available AND fallback_on_error=False:
#      │  └─ Route = [browser_targets]  (browser-only, fail if all browser targets fail)
#      └─ ELIF no browser targets AND fallback_on_error=True:
#         └─ Route = [standard_targets]  (degrade to standard providers)
#
#   4. REQUEST PREPARATION
#      ├─ Remove "webllm" metadata field from request body
#      ├─ Apply QoL output-control injection (T020 non-blocking)
#      ├─ Apply context relay if session_id specified (for provider switching)
#      └─ Prepare request body for dispatch
#
#   5. TARGET EXECUTION LOOP (with circuit breaker pattern)
#      ├─ FOR each target in order:
#      │  ├─ Check circuit breaker state (skip if open after 5 failures/60s)
#      │  ├─ Track if target is browser-based (for fallback decision)
#      │  ├─ Translate request to provider's API format (OpenAI → provider-specific)
#      │  ├─ Execute request via executor.execute()
#      │  ├─ IF success (200/201 range):
#      │  │  ├─ Record circuit success (failures reset to 0)
#      │  │  ├─ Translate response back to OpenAI format
#      │  │  ├─ Track cost in budget guard
#      │  │  ├─ Store context for relay (if session_id)
#      │  │  └─ RETURN result immediately
#      │  ├─ ELIF failure AND browser target exhausted AND fallback_on_error:
#      │  │  ├─ Log fallback decision
#      │  │  ├─ Inject standard_targets into routing order
#      │  │  └─ Continue loop with fallback targets
#      │  └─ ELIF failure:
#      │     ├─ Record circuit failure (increment failure counter)
#      │     ├─ Log error with target details
#      │     └─ Continue to next target
#      │
#      └─ IF all targets exhausted: RETURN 503 Service Unavailable
#
#   6. RESPONSE RELAY & INTEGRATION
#      ├─ WebLLM response includes browser automation context:
#      │  ├─ Page title and URL from final navigation
#      │  ├─ Screenshot data (if captured via playwright tools)
#      │  ├─ Console logs (JS errors, warnings from page)
#      │  ├─ Page HTML content (for DOM analysis)
#      │  └─ Form submission status (if automated form fill)
#      ├─ Dashboard integration:
#      │  ├─ Display browser automation sequence
#      │  ├─ Render screenshots inline
#      │  ├─ Show JavaScript errors and network failures
#      │  └─ Allow re-run with different prompt/parameters
#      └─ Multi-step workflows:
#         ├─ Navigate → Take screenshot → Inject prompt → Submit → Capture response
#         ├─ Fill form → Click → Wait for JS → Get console logs → Extract data
#         └─ All steps maintain session context and authentication
#
#   7. ERROR HANDLING & RECOVERY
#      ├─ Browser provider failure modes:
#      │  ├─ Timeout (15s navigation timeout, 5s element wait, 30s global timeout)
#      │  ├─ Element not found (returns 404-like error)
#      │  ├─ JavaScript error (captured in console logs)
#      │  ├─ Network failure (Playwright connection error)
#      │  └─ Resource unavailable (browser context destroyed)
#      ├─ Fallback logic (when enabled):
#      │  ├─ Mark browser target as failed in circuit breaker
#      │  ├─ Check if all browser targets exhausted
#      │  ├─ IF yes AND fallback_on_error=True: retry with standard providers
#      │  └─ IF yes AND fallback_on_error=False: return browser error to caller
#      └─ Budget limits:
#         ├─ Track cost per browser automation step
#         ├─ If combo budget exhausted: return 429 Too Expensive
#         └─ Dashboard shows cost breakdown and remaining budget
#
# ── Configuration Reference (environment variables) ──────────────────────────
#
# CYBERSEC_WEBLLM_URL           — Backend URL for webllm service (optional)
# CYBERSEC_BROWSER_PROFILE      — Persistent browser profile path (default: /tmp/.cybersec_browser_profile)
# CYBERSEC_BROWSER_HEADLESS     — Run browser headless (default: true)
# CYBERSEC_WEBLLM_TIMEOUT_MS    — Global request timeout in ms (default: 30000)
# CYBERSEC_BROWSER_STEALTH      — Enable anti-bot evasion (default: true)
# CYBERSEC_MAX_BROWSERS         — Max concurrent browser instances (default: 3)
# CYBERSEC_WEBLLM_FALLBACK      — Fallback to standard providers on error (default: true)
#
# ─────────────────────────────────────────────────────────────────────────────

WEBLLM_CONFIG: dict[str, Any] = {
    "backend_url": os.environ.get("CYBERSEC_WEBLLM_URL", ""),
    "browser_profile": os.environ.get("CYBERSEC_BROWSER_PROFILE", "/tmp/.cybersec_browser_profile"),
    "headless": os.environ.get("CYBERSEC_BROWSER_HEADLESS", "true").lower() in ("true", "1"),
    "timeout_ms": int(os.environ.get("CYBERSEC_WEBLLM_TIMEOUT_MS", "30000")),
    "stealth_mode": os.environ.get("CYBERSEC_BROWSER_STEALTH", "true").lower() in ("true", "1"),
    "max_concurrent_browsers": int(os.environ.get("CYBERSEC_MAX_BROWSERS", "3")),
    "fallback_on_error": os.environ.get("CYBERSEC_WEBLLM_FALLBACK", "true").lower() in ("true", "1"),
}

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
    webllm: bool = False,
) -> ExecutorResult:
    """
    Route a request through a combo config. Tries targets in strategy order,
    falls back on failure. Returns first successful result.

    Supports:
    - Budget guard: skip targets if combo budget exceeded
    - Context relay: carry conversation context across provider switches
    - LKGP: remember last successful provider
    - webllm (T026): prefer browser/Playwright providers when True, fallback to standard on error
    
    WebLLM Routing (T026):
      When webllm=True or body.get("webllm")=True:
      1. Filter targets to browser-based providers only (auth_type=BROWSER)
      2. If browser targets available, use those exclusively
      3. On browser provider failure:
         a. If WEBLLM_CONFIG["fallback_on_error"]=True, retry with non-browser providers
         b. Otherwise, return error and require explicit fallback from caller
      4. Response is relayed back through dashboard with browser context metadata
      5. WebLLM metadata (webllm field) is stripped from request before dispatch
      6. Useful for automated web interaction, screenshot capture, form filling
      
    Error Handling:
      - Circuit breaker per target: 5 consecutive failures → open for 60s
      - Budget exhaustion: return 429 Too Expensive
      - All targets exhausted: return 503 Service Unavailable
      - Provider exception: log and try next target (T020 non-blocking pattern)
      
    Context Relay:
      - Stores conversation messages per session_id
      - On provider switch: prepends context summary as system message
      - Useful for multi-provider conversations (cost optimization)
      - Caps at 50 messages to avoid context explosion
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

    # T026: webllm mode — prefer browser/Playwright providers, fall back to all on error
    webllm_mode = webllm or body.get("webllm")
    webllm_targets: list[ResolvedTarget] = []
    fallback_targets: list[ResolvedTarget] = []
    
    if webllm_mode:
        from ai_proxy.providers.registry import AuthType as _AT
        for t in ordered:
            if t.provider.auth_type == _AT.BROWSER:
                webllm_targets.append(t)
            else:
                fallback_targets.append(t)
        
        # Determine target order based on config
        if webllm_targets:
            ordered = webllm_targets
        elif not WEBLLM_CONFIG["fallback_on_error"]:
            # No browser targets and fallback disabled
            return ExecutorResult(
                status_code=503,
                error="WebLLM mode requested but no browser providers available and fallback disabled",
            )
        # else: ordered remains all targets (fallback enabled)
        
        body = {k: v for k, v in body.items() if k != "webllm"}  # strip meta field

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
    attempted_webllm_targets = 0
    
    for i, target in enumerate(ordered):
        circuit_key = f"{target.provider.id}:{target.model_id}"
        circuit = _get_circuit(circuit_key)

        if circuit.is_open:
            logger.info("Circuit open for %s, skipping", circuit_key)
            continue

        # Track WebLLM target attempts for fallback decision
        if webllm_mode and target in webllm_targets:
            attempted_webllm_targets += 1

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
                
                # T026: WebLLM failure — check if we should try fallback targets
                if webllm_mode and attempted_webllm_targets > 0 and target in webllm_targets:
                    # Just finished last WebLLM target, now try fallback if enabled
                    remaining_webllm = [t for t in webllm_targets[i+1:] if t in ordered[i+1:]]
                    if not remaining_webllm and fallback_targets and WEBLLM_CONFIG["fallback_on_error"]:
                        logger.info(
                            "WebLLM targets exhausted, falling back to standard providers. "
                            "Last error: %s", (result.error or "")[:200]
                        )
                        ordered = fallback_targets + ordered[i+1:]
                
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
    webllm: bool = False,
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
    return await route_request(body, combo, stream=stream, session_id=session_id, agent_name=agent_name, webllm=webllm)


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


