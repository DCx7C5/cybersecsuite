"""Strategy-based target ordering and selection."""

import random

from .models import ComboTarget, ResolvedTarget
from .strategy import Strategy

_last_good: dict[str, str | None] = {}
_usage_counts: dict[str, dict[str, int]] = {}
_round_robin_index: dict[str, int] = {}


def _safe_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    return default


def _safe_int(value: object, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    return default


def _to_resolved(t: ComboTarget, combo_id: str = "") -> ResolvedTarget:
    return ResolvedTarget(
        provider=t.provider_id,
        model_id=t.model_id,
        weight=t.weight,
        enabled=t.enabled,
        combo_id=combo_id,
        metadata=dict(t.metadata),
    )


def _apply_strategy(
    targets: list[ComboTarget],
    strategy: Strategy,
    combo_id: str,
) -> list[ResolvedTarget]:
    active = [_to_resolved(t, combo_id) for t in targets if t.enabled]
    if not active:
        return []

    match strategy:
        case Strategy.PRIORITY:
            return active

        case Strategy.ROUND_ROBIN:
            idx = _round_robin_index.get(combo_id, 0) % len(active)
            _round_robin_index[combo_id] = idx + 1
            return active[idx:] + active[:idx]

        case Strategy.COST_OPTIMIZED:
            return sorted(active, key=lambda t: _safe_float(t.metadata.get("cost")))

        case Strategy.WEIGHTED:
            weights = [max(t.weight, 0.01) for t in active]
            chosen = random.choices(active, weights=weights, k=1)[0]
            rest = sorted(
                [t for t in active if t is not chosen],
                key=lambda t: t.weight,
                reverse=True,
            )
            return [chosen] + rest

        case Strategy.RANDOM:
            shuffled = list(active)
            random.shuffle(shuffled)
            return shuffled

        case Strategy.LEAST_USED:
            counts = _usage_counts.setdefault(combo_id, {})
            active.sort(key=lambda t: counts.get(t.provider + ":" + t.model_id, 0))
            first = active[0]
            counts[first.provider + ":" + first.model_id] = (
                counts.get(first.provider + ":" + first.model_id, 0) + 1
            )
            return active

        case Strategy.FILL_FIRST:
            return [active[0]] + sorted(active[1:], key=lambda t: t.weight, reverse=True)

        case Strategy.P2C:
            if len(active) < 2:
                return active
            a, b = random.sample(active, 2)
            counts = _usage_counts.setdefault(combo_id, {})
            key_a = a.provider + ":" + a.model_id
            key_b = b.provider + ":" + b.model_id
            if counts.get(key_a, 0) <= counts.get(key_b, 0):
                first, second = a, b
            else:
                first, second = b, a
            counts[key_a] = counts.get(key_a, 0) + 1
            counts[key_b] = counts.get(key_b, 0) + 1
            rest = [t for t in active if t is not a and t is not b]
            return [first, second] + rest

        case Strategy.STRICT_RANDOM:
            return [random.choice(active)]

        case Strategy.LKGP:
            last = _last_good.get(combo_id)
            if last is not None:
                idx = next(
                    (i for i, t in enumerate(active) if t.provider + ":" + t.model_id == last),
                    None,
                )
                if idx is not None:
                    return [active[idx]] + active[:idx] + active[idx + 1 :]
            return active

        case Strategy.CONTEXT_OPTIMIZED:
            return sorted(
                active,
                key=lambda t: _safe_int(t.metadata.get("context_window")),
                reverse=True,
            )

        case Strategy.CONTEXT_RELAY:
            last = _last_good.get(combo_id)
            if last is not None:
                idx = next(
                    (i for i, t in enumerate(active) if t.provider + ":" + t.model_id == last),
                    None,
                )
                if idx is not None:
                    return [active[idx]] + active[:idx] + active[idx + 1 :]
            return active

        case Strategy.AUTO:
            return sorted(
                active,
                key=lambda t: (_safe_float(t.metadata.get("cost")),),
            )


def _record_good(combo_id: str, provider: str, model_id: str) -> None:
    """Record a successful target for stateful strategies."""
    _last_good[combo_id] = provider + ":" + model_id
