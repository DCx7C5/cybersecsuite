"""Retry configuration and strategies for API services."""

from dataclasses import dataclass, field
from enum import Enum
import random


class RetryStrategy(str, Enum):
    """Retry strategy for a provider."""
    SKIP = "skip"           # Provider has built-in retry, don't wrap
    WRAP = "wrap"           # Provider lacks retry, wrap it
    PRESERVE = "preserve"   # Provider retry is configurable, preserve it


class RetryableErrorType(str, Enum):
    """Error types that warrant retrying."""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    GATEWAY_ERROR = "gateway_error"
    CONNECTION_ERROR = "connection_error"
    
    # Non-retryable
    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"


@dataclass
class RetryConfig:
    """Configuration for retry behavior across all providers."""
    max_retries: int = 3
    base_delay_ms: float = 1000.0
    max_delay_ms: float = 60000.0
    exponential_base: float = 2.0
    
    # Jitter: random multiplier 0.9-1.1 to avoid thundering herd
    jitter_min: float = 0.9
    jitter_max: float = 1.1
    
    # Which error types trigger retries
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
        """
        Calculate backoff time (milliseconds) for this attempt.
        
        Uses exponential backoff with jitter:
          delay = base_delay_ms * (exponential_base ** attempt) * jitter
        
        Args:
            attempt: Attempt number (0-indexed)
        
        Returns:
            Backoff time in milliseconds
        """
        # Calculate exponential delay
        delay = self.base_delay_ms * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay_ms)
        
        # Add jitter to avoid thundering herd
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        return delay * jitter
