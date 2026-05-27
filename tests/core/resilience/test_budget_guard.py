"""Tests for routing budget guard."""

from css.core.resilience.routing.budget import BudgetGuard


def test_budget_guard_records_and_checks_budget() -> None:
    guard = BudgetGuard()
    guard.record_cost("default", 0.25)

    assert guard.get_spent("default") == 0.25
    assert guard.check_budget("default", 1.0) is True
    assert guard.check_budget("default", 0.2) is False


def test_budget_guard_clamps_none_and_negative_costs() -> None:
    guard = BudgetGuard()
    guard.record_cost("combo", None)
    guard.record_cost("combo", -5.0)
    guard.record_cost("combo", 0.1)

    assert guard.get_spent("combo") == 0.1


def test_budget_guard_get_all_and_reset() -> None:
    guard = BudgetGuard()
    guard.record_cost("a", 0.2)
    guard.record_cost("b", 0.3)
    snapshot = guard.get_all()

    assert snapshot == {"a": 0.2, "b": 0.3}

    guard.reset("a")
    assert guard.get_spent("a") == 0.0
    assert guard.get_spent("b") == 0.3

    guard.reset()
    assert guard.get_all() == {}

