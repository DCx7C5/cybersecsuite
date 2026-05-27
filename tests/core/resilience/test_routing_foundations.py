"""Tests for routing strategy and combo foundation models."""

from css.core.resilience.routing import (
    ComboConfig,
    ComboTarget,
    PROVIDER_TIER_LIST,
    ResolvedTarget,
    Strategy,
    _apply_strategy,
)


def test_strategy_enum_and_provider_tiers_contract() -> None:
    assert len(Strategy) == 13
    assert PROVIDER_TIER_LIST[0].name == "LOCAL_MINIMAL"
    assert PROVIDER_TIER_LIST[-1].name == "S_PLUS"
    assert PROVIDER_TIER_LIST[-1].is_terminal is True


def test_combo_models_roundtrip_contract() -> None:
    combo = ComboConfig(
        id="default",
        name="Default",
        strategy=Strategy.PRIORITY,
        targets=[ComboTarget(provider_id="openai", model_id="gpt-4o")],
        budget_usd=1.0,
    )
    assert combo.targets[0].provider_id == "openai"

    resolved = ResolvedTarget(provider="openai", model_id="gpt-4o", weight=1.0, enabled=True)
    assert resolved.provider == "openai"


def test_apply_strategy_priority_and_cost_optimized() -> None:
    targets = [
        ComboTarget(provider_id="a", model_id="m1", weight=1.0, metadata={"input_cost_per_mtok": 1.0}),
        ComboTarget(provider_id="b", model_id="m2", weight=2.0, metadata={"input_cost_per_mtok": 0.1}),
    ]
    priority = _apply_strategy(targets, Strategy.PRIORITY, "combo-priority")
    assert priority[0].model_id == "m1"

    cost = _apply_strategy(targets, Strategy.COST_OPTIMIZED, "combo-cost")
    assert cost[0].model_id == "m2"


def test_apply_strategy_round_robin_rotates() -> None:
    targets = [
        ComboTarget(provider_id="a", model_id="m1"),
        ComboTarget(provider_id="b", model_id="m2"),
    ]
    first = _apply_strategy(targets, Strategy.ROUND_ROBIN, "combo-rr")
    second = _apply_strategy(targets, Strategy.ROUND_ROBIN, "combo-rr")
    assert first[0].model_id == "m1"
    assert second[0].model_id == "m2"
