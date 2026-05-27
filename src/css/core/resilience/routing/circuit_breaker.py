"""Circuit breaker per provider:model target."""

from time import time


class _CircuitState:
    __slots__ = ("failure_count", "last_failure_ts", "window_seconds", "threshold")

    def __init__(self, window_seconds: int = 60, threshold: int = 5) -> None:
        self.failure_count = 0
        self.last_failure_ts = 0.0
        self.window_seconds = window_seconds
        self.threshold = threshold

    def is_open(self) -> bool:
        if self.failure_count < self.threshold:
            return False
        return (time() - self.last_failure_ts) <= self.window_seconds

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_ts = time()

    def record_success(self) -> None:
        self.failure_count = 0

    def reset(self) -> None:
        self.failure_count = 0
        self.last_failure_ts = 0.0


class CircuitBreaker:
    """Per-target circuit breaker with rolling failure window."""

    def __init__(self, window_seconds: int = 60, threshold: int = 5) -> None:
        self._window = window_seconds
        self._threshold = threshold
        self._states: dict[str, _CircuitState] = {}

    def _get_state(self, target_key: str) -> _CircuitState:
        state = self._states.get(target_key)
        if state is None:
            state = _CircuitState(self._window, self._threshold)
            self._states[target_key] = state
        return state

    def is_open(self, target_key: str) -> bool:
        return self._get_state(target_key).is_open()

    def record_failure(self, target_key: str) -> None:
        self._get_state(target_key).record_failure()

    def record_success(self, target_key: str) -> None:
        state = self._states.get(target_key)
        if state is not None:
            state.record_success()

    def reset(self, target_key: str | None = None) -> None:
        if target_key is not None:
            state = self._states.get(target_key)
            if state is not None:
                state.reset()
        else:
            for state in self._states.values():
                state.reset()

    def get_all(self) -> dict[str, dict[str, int | float | bool]]:
        now = time()
        result: dict[str, dict[str, int | float | bool]] = {}
        stale_keys: list[str] = []
        for key, state in self._states.items():
            if state.failure_count > 0 and (now - state.last_failure_ts) > state.window_seconds:
                stale_keys.append(key)
                continue
            result[key] = {
                "failure_count": state.failure_count,
                "is_open": state.is_open(),
                "window_seconds": state.window_seconds,
            }
        for k in stale_keys:
            del self._states[k]
        return result


circuit_breaker: CircuitBreaker = CircuitBreaker()
