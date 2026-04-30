"""Retry orchestrator: Custom hybrid retry logic for all providers."""

import asyncio
import logging
from typing import Callable, Optional, TypeVar, Generic, Awaitable
from dataclasses import dataclass, field
from datetime import datetime

from core.types.api_services import ProviderType
from .config import RetryConfig, RetryStrategy, RetryableErrorType
from .detection import RetryDetector

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type variable for return values


@dataclass
class RetryAttempt:
    """Single retry attempt metadata."""
    attempt_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[Exception] = None
    latency_ms: float = 0.0
    success: bool = False
    
    @property
    def duration_ms(self) -> float:
        """Duration of this attempt in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


@dataclass
class RetryResult(Generic[T]):
    """Result of retry attempt(s)."""
    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None
    attempts: list[RetryAttempt] = field(default_factory=list)
    total_retries: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def attempt_count(self) -> int:
        """Total number of attempts (including first try)."""
        return len(self.attempts)


class RetryOrchestrator:
    """
    Orchestrates retries across all providers using custom hybrid approach.
    
    Strategy:
    - Providers with built-in retry: SKIP (don't wrap)
    - Providers without retry: WRAP (implement custom retry)
    - Result: No double-retry on sophisticated SDKs, resilience for local SDKs
    """
    
    def __init__(self, config: RetryConfig = None):
        """
        Initialize orchestrator.
        
        Args:
            config: RetryConfig instance (uses defaults if None)
        """
        self.config = config or RetryConfig()
    
    def get_strategy(self, provider_id: ProviderType) -> RetryStrategy:
        """Get retry strategy for provider."""
        return RetryDetector.get_strategy(provider_id)
    
    def classify_error(self, error: Exception) -> RetryableErrorType:
        """
        Classify error to determine if retryable.
        
        Args:
            error: Exception to classify
        
        Returns:
            RetryableErrorType indicating error category
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Timeout errors
        if any(word in error_str for word in ['timeout', 'timed out', 'read timed out']):
            return RetryableErrorType.TIMEOUT
        
        # Rate limit errors
        if any(word in error_str for word in ['rate limit', '429', 'rate-limited']):
            return RetryableErrorType.RATE_LIMIT
        
        # Service unavailable errors
        if any(word in error_str for word in ['503', 'unavailable', 'service down', 'service unavailable']):
            return RetryableErrorType.SERVICE_UNAVAILABLE
        
        # Gateway/Bad Gateway errors
        if any(word in error_str for word in ['502', '504', 'gateway', 'bad gateway']):
            return RetryableErrorType.GATEWAY_ERROR
        
        # Connection errors
        if any(word in error_str for word in ['connection', 'refused', 'unreachable', 'econnrefused']):
            return RetryableErrorType.CONNECTION_ERROR
        
        # Authentication errors (NOT retryable)
        if any(word in error_str for word in ['401', 'unauthorized', 'authentication', 'invalid_api_key']):
            return RetryableErrorType.AUTHENTICATION
        
        # Invalid request errors (NOT retryable)
        if any(word in error_str for word in ['400', 'invalid', 'bad request', 'request_invalid']):
            return RetryableErrorType.INVALID_REQUEST
        
        # Not found errors (NOT retryable)
        if any(word in error_str for word in ['404', 'not found', 'model not found']):
            return RetryableErrorType.NOT_FOUND
        
        # Default: treat as non-retryable (safe default)
        return RetryableErrorType.INVALID_REQUEST
    
    def map_error_to_unified(self, error: Exception, provider_id: ProviderType) -> Exception:
        """
        Map provider-specific error to unified 5-type hierarchy (Issue #3).
        
        Unified types: AuthError, RateLimitError, TimeoutError, GatewayError, UnknownError
        
        Args:
            error: Original exception from SDK
            provider_id: Provider type
        
        Returns:
            Mapped exception (unified error subclass) with provider metadata
        
        Note:
            This enables uniform error handling across all 25+ providers.
            Use isinstance() to detect error type, regardless of provider.
        """
        try:
            from api_services.error_mappers import map_provider_error
            return map_provider_error(provider_id, error)
        except ImportError:
            logger.warning("error_mappers not available, returning original error")
            return error
    
    def is_retryable(self, error: Exception) -> bool:
        """
        Check if error should trigger retry.
        
        Args:
            error: Exception to check
        
        Returns:
            True if error is retryable
        """
        error_type = self.classify_error(error)
        return error_type in self.config.retryable_errors
    
    async def execute_with_retry(
        self,
        api_call: Callable[..., Awaitable[T]],
        provider_id: ProviderType,
        *args,
        **kwargs
    ) -> RetryResult[T]:
        """
        Execute API call with retry logic.
        
        Strategy depends on provider:
        - SKIP: Call once, no retry (provider has its own)
        - WRAP: Implement custom retry with backoff
        - PRESERVE: Call once, let provider handle
        
        Args:
            api_call: Async function to call (e.g., sdk.call_llm)
            provider_id: Provider type
            *args: Positional args for api_call
            **kwargs: Keyword args for api_call
        
        Returns:
            RetryResult with success, result/error, and attempt history
        
        Example:
            orchestrator = RetryOrchestrator()
            result = await orchestrator.execute_with_retry(
                api_call=sdk.call_llm,
                provider_id=ProviderType.OLLAMA,
                model_id="mistral",
                messages=messages
            )
            if result.success:
                return result.result
            else:
                raise result.error
        """
        
        strategy = self.get_strategy(provider_id)
        
        # If provider has built-in retry, don't wrap
        if strategy == RetryStrategy.SKIP:
            logger.debug(f"{provider_id}: Skipping custom retry (SDK has built-in)")
            attempt_obj = RetryAttempt(
                attempt_number=0,
                start_time=datetime.now()
            )
            try:
                result = await api_call(*args, **kwargs)
                attempt_obj.end_time = datetime.now()
                attempt_obj.success = True
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=[attempt_obj]
                )
            except Exception as e:
                attempt_obj.end_time = datetime.now()
                attempt_obj.error = e
                return RetryResult(
                    success=False,
                    error=e,
                    attempts=[attempt_obj]
                )
        
        # Otherwise, implement custom retry
        attempts: list[RetryAttempt] = []
        total_latency = 0.0
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            attempt_obj = RetryAttempt(
                attempt_number=attempt,
                start_time=datetime.now()
            )
            attempts.append(attempt_obj)
            
            try:
                logger.debug(f"{provider_id}: Attempt {attempt + 1}/{self.config.max_retries + 1}")
                result = await api_call(*args, **kwargs)
                
                attempt_obj.end_time = datetime.now()
                attempt_obj.success = True
                total_latency += attempt_obj.duration_ms
                
                if attempt > 0:
                    logger.info(f"{provider_id}: Succeeded after {attempt} retries")
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempts,
                    total_retries=attempt,
                    total_latency_ms=total_latency
                )
            
            except Exception as e:
                attempt_obj.end_time = datetime.now()
                attempt_obj.error = e
                total_latency += attempt_obj.duration_ms
                last_error = e
                
                # Check if retryable
                if not self.is_retryable(e):
                    logger.warning(f"{provider_id}: Non-retryable error, failing immediately: {type(e).__name__}")
                    return RetryResult(
                        success=False,
                        error=e,
                        attempts=attempts,
                        total_retries=attempt,
                        total_latency_ms=total_latency
                    )
                
                # If this was last attempt, return error
                if attempt >= self.config.max_retries:
                    logger.error(
                        f"{provider_id}: Max retries exceeded after {attempt + 1} attempts. "
                        f"Total latency: {total_latency:.1f}ms"
                    )
                    return RetryResult(
                        success=False,
                        error=e,
                        attempts=attempts,
                        total_retries=attempt,
                        total_latency_ms=total_latency
                    )
                
                # Calculate backoff and wait
                backoff_ms = self.config.backoff_for_attempt(attempt)
                logger.warning(
                    f"{provider_id}: Retryable error (attempt {attempt + 1}), "
                    f"waiting {backoff_ms:.1f}ms before retry: {type(e).__name__}"
                )
                
                await asyncio.sleep(backoff_ms / 1000.0)
        
        # Should not reach here, but defensive
        if last_error:
            return RetryResult(
                success=False,
                error=last_error,
                attempts=attempts,
                total_retries=self.config.max_retries,
                total_latency_ms=total_latency
            )
        
        return RetryResult(
            success=False,
            error=RuntimeError("Retry loop completed without result"),
            attempts=attempts,
            total_retries=self.config.max_retries,
            total_latency_ms=total_latency
        )
