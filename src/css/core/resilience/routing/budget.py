"""Per-combo in-memory spend guard for provider routing."""

from threading import Lock


class BudgetGuard:
    """Track per-combo spend and enforce soft budget caps."""

    def __init__(self) -> None:
        self._spent_by_combo: dict[str, float] = {}
        self._lock = Lock()

    @staticmethod
    def _normalize_cost(cost_usd: float | None) -> float:
        if cost_usd is None:
            return 0.0
        normalized = float(cost_usd)
        if normalized < 0.0:
            return 0.0
        return normalized

    def record_cost(self, combo_id: str, cost_usd: float | None) -> float:
        """Add cost to combo spend and return updated total."""
        normalized_cost = self._normalize_cost(cost_usd)
        with self._lock:
            current = self._spent_by_combo.get(combo_id, 0.0)
            updated = current + normalized_cost
            self._spent_by_combo[combo_id] = updated
        return updated

    def check_budget(self, combo_id: str, budget_usd: float) -> bool:
        """Return True when current spend is within budget."""
        return self.get_spent(combo_id) <= budget_usd

    def get_spent(self, combo_id: str) -> float:
        """Return current spend for combo, defaulting to 0.0."""
        with self._lock:
            return self._spent_by_combo.get(combo_id, 0.0)

    def get_all(self) -> dict[str, float]:
        """Return a shallow copy of all tracked spends."""
        with self._lock:
            return dict(self._spent_by_combo)

    def reset(self, combo_id: str | None = None) -> None:
        """Reset spend for one combo or all combos."""
        with self._lock:
            if combo_id is None:
                self._spent_by_combo.clear()
                return
            self._spent_by_combo.pop(combo_id, None)


budget_guard = BudgetGuard()
