"""Retry orchestrator with hybrid provider-aware strategy selection."""

from css.core.logger import getLogger
import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Generic, TypeVar

from css.core.types.enums import ProviderType
from css.core.types.error_mappers import map_provider_error

from .config import RetryConfig, RetryStrategy, RetryableErrorType
from .detection import RetryDetector

logger = getLogger(__name__)

T = TypeVar("T")


class RetryAttempt:
    def __init__(
        self,
        attempt_number: int,
        start_time: datetime,
        end_time: datetime | None = None,
        error: Exception | None = None,
        latency_ms: float = 0.0,
        success: bool = False,
    ) -> None:
        self.attempt_number = attempt_number
        self.start_time = start_time
        self.end_time = end_time
        self.error = error
        self.latency_ms = latency_ms
        self.success = success

    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


class RetryResult(Generic[T]):
    def __init__(
        self,
        success: bool,
        result: T | None = None,
        error: Exception | None = None,
        attempts: list[RetryAttempt] | None = None,
        total_retries: int = 0,
        total_latency_ms: float = 0.0,
    ) -> None:
        self.success = success
        self.result = result
        self.error = error
        self.attempts = attempts or []
        self.total_retries = total_retries
        self.total_latency_ms = total_latency_ms

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)


class RetryOrchestrator:
    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()

    def get_strategy(self, provider_id: ProviderType) -> RetryStrategy:
        return RetryDetector.get_strategy(provider_id)

    def classify_error(self, error: Exception) -> RetryableErrorType:
        error_str = str(error).lower()
        if any(word in error_str for word in ("timeout", "timed out", "read timed out")):
            return RetryableErrorType.TIMEOUT
        if any(word in error_str for word in ("rate limit", "429", "rate-limited")):
            return RetryableErrorType.RATE_LIMIT
        if any(word in error_str for word in ("503", "unavailable", "service down", "service unavailable")):
            return RetryableErrorType.SERVICE_UNAVAILABLE
        if any(word in error_str for word in ("502", "504", "gateway", "bad gateway")):
            return RetryableErrorType.GATEWAY_ERROR
        if any(word in error_str for word in ("connection", "refused", "unreachable", "econnrefused")):
            return RetryableErrorType.CONNECTION_ERROR
        if any(word in error_str for word in ("401", "unauthorized", "authentication", "invalid_api_key")):
            return RetryableErrorType.AUTHENTICATION
        if any(word in error_str for word in ("404", "not found", "model not found")):
            return RetryableErrorType.NOT_FOUND
        return RetryableErrorType.INVALID_REQUEST

    def map_error_to_unified(self, error: Exception, provider_id: ProviderType) -> Exception:
        return map_provider_error(provider_id, error)

    def is_retryable(self, error: Exception) -> bool:
        return self.classify_error(error) in self.config.retryable_errors

    async def execute_with_retry(
        self,
        api_call: Callable[..., Awaitable[T]],
        provider_id: ProviderType,
        *args,
        **kwargs,
    ) -> RetryResult[T]:
        strategy = self.get_strategy(provider_id)
        if strategy == RetryStrategy.SKIP:
            attempt = RetryAttempt(attempt_number=0, start_time=datetime.now())
            try:
                result = await api_call(*args, **kwargs)
                attempt.end_time = datetime.now()
                attempt.success = True
                return RetryResult(success=True, result=result, attempts=[attempt])
            except Exception as exc:
                attempt.end_time = datetime.now()
                attempt.error = exc
                return RetryResult(success=False, error=exc, attempts=[attempt])

        attempts: list[RetryAttempt] = []
        total_latency = 0.0
        for attempt_number in range(self.config.max_retries + 1):
            attempt = RetryAttempt(attempt_number=attempt_number, start_time=datetime.now())
            attempts.append(attempt)
            try:
                result = await api_call(*args, **kwargs)
                attempt.end_time = datetime.now()
                attempt.success = True
                total_latency += attempt.duration_ms
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempts,
                    total_retries=attempt_number,
                    total_latency_ms=total_latency,
                )
            except Exception as exc:
                attempt.end_time = datetime.now()
                attempt.error = exc
                total_latency += attempt.duration_ms
                if not self.is_retryable(exc) or attempt_number >= self.config.max_retries:
                    return RetryResult(
                        success=False,
                        error=exc,
                        attempts=attempts,
                        total_retries=attempt_number,
                        total_latency_ms=total_latency,
                    )
                backoff_ms = self.config.backoff_for_attempt(attempt_number)
                await asyncio.sleep(backoff_ms / 1000.0)

        return RetryResult(
            success=False,
            error=RuntimeError("retry loop exited unexpectedly"),
            attempts=attempts,
            total_retries=self.config.max_retries,
            total_latency_ms=total_latency,
        )
