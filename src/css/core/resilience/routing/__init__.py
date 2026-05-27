"""Provider-routing foundations for resilience."""

from .circuit_breaker import CircuitBreaker, circuit_breaker
from .models import ComboTarget, ComboConfig, ResolvedTarget
from .strategies import _apply_strategy, _record_good
from .strategy import Strategy, ProviderTier, PROVIDER_TIER_LIST

__all__ = [
    "Strategy",
    "ProviderTier",
    "PROVIDER_TIER_LIST",
    "ComboTarget",
    "ComboConfig",
    "ResolvedTarget",
    "_apply_strategy",
    "_record_good",
    "CircuitBreaker",
    "circuit_breaker",
]
