"""Retry configuration and strategy primitives."""

from dataclasses import dataclass, field
from enum import Enum
import random


class RetryStrategy(str, Enum):
    SKIP = "skip"
    WRAP = "wrap"
    PRESERVE = "preserve"


class RetryableErrorType(str, Enum):
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    GATEWAY_ERROR = "gateway_error"
    CONNECTION_ERROR = "connection_error"
    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"


@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay_ms: float = 1000.0
    max_delay_ms: float = 60000.0
    exponential_base: float = 2.0
    jitter_min: float = 0.9
    jitter_max: float = 1.1
    retryable_errors: list[RetryableErrorType] = field(
        default_factory=lambda: [
            RetryableErrorType.TIMEOUT,
            RetryableErrorType.RATE_LIMIT,
            RetryableErrorType.SERVICE_UNAVAILABLE,
            RetryableErrorType.GATEWAY_ERROR,
            RetryableErrorType.CONNECTION_ERROR,
        ]
    )

    def backoff_for_attempt(self, attempt: int) -> float:
        delay = self.base_delay_ms * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay_ms)
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        return delay * jitter
