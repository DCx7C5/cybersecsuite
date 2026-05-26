"""Team metrics and monitoring."""

from __future__ import annotations

from collections import defaultdict


class BudgetState:
    """Token budget state for one scope."""

    def __init__(self, limit: int, used: int = 0) -> None:
        self.limit = limit
        self.used = used

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)


class TokenBudgetTracker:
    """Track token budgets per team and per session."""

    def __init__(self, default_team_limit: int = 200_000, default_session_limit: int = 80_000):
        self.default_team_limit = default_team_limit
        self.default_session_limit = default_session_limit
        self._team_budget: dict[str, BudgetState] = {}
        self._session_budget: dict[str, BudgetState] = {}
        self._provider_usage: dict[tuple[str, str], int] = defaultdict(int)

    def ensure_team(self, team_id: str, limit: int | None = None) -> BudgetState:
        if team_id not in self._team_budget:
            self._team_budget[team_id] = BudgetState(limit=limit or self.default_team_limit)
        return self._team_budget[team_id]

    def ensure_session(self, session_id: str, limit: int | None = None) -> BudgetState:
        if session_id not in self._session_budget:
            self._session_budget[session_id] = BudgetState(limit=limit or self.default_session_limit)
        return self._session_budget[session_id]

    def can_consume(self, team_id: str, session_id: str, tokens: int) -> bool:
        team = self.ensure_team(team_id)
        session = self.ensure_session(session_id)
        return team.remaining >= tokens and session.remaining >= tokens

    def consume(self, team_id: str, session_id: str, provider: str, tokens: int) -> None:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")
        if not self.can_consume(team_id, session_id, tokens):
            raise ValueError("token budget exceeded")
        self._team_budget[team_id].used += tokens
        self._session_budget[session_id].used += tokens
        self._provider_usage[(team_id, provider)] += tokens

    def snapshot(self, team_id: str, session_id: str) -> dict:
        team = self.ensure_team(team_id)
        session = self.ensure_session(session_id)
        return {
            "team": {"limit": team.limit, "used": team.used, "remaining": team.remaining},
            "session": {"limit": session.limit, "used": session.used, "remaining": session.remaining},
        }

    def provider_usage(self, team_id: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for (candidate_team_id, provider), used in self._provider_usage.items():
            if candidate_team_id == team_id:
                result[provider] = used
        return result


class TeamMetrics:
    """Track team performance metrics."""

    def __init__(self):
        self._tracker = TokenBudgetTracker()

    async def get_team_metrics(self, team_id: int):
        """Get team metrics."""
        team_key = str(team_id)
        # Session-specific details are delivered through snapshot calls.
        return {
            "team_id": team_key,
            "provider_token_usage": self._tracker.provider_usage(team_key),
        }

    def get_budget_tracker(self) -> TokenBudgetTracker:
        """Expose token budget tracker for orchestrator/runtime wiring."""
        return self._tracker
