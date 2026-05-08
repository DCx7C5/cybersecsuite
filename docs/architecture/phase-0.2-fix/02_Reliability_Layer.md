# 02: Reliability Layer (Issues #2, #3, #7, #8)

**Document Purpose:** Implementation guides for retry, error handling, token counting, resource cleanup  
**Covers:** Issue #2 (Retry Logic), #3 (Error Codes), #7 (Resource Cleanup), #8 (Token Counting)  
**Weeks:** 1-5  
**Last Updated:** 2026-04-30

---

## Issue #2: Retry Logic (Custom Hybrid)

### Problem Statement

**Current State:**
- Anthropic SDK: Built-in retry with sophisticated backoff (exponential with jitter)
- OpenAI SDK: Configurable retry with custom behavior
- Ollama: No built-in retry (pure pass-through to local model)
- Other providers: Mixed (some have retry, some don't)

**Issues with Naive Wrapping:**
- If we wrap ALL providers: Anthropic will double-retry (wasted API calls, extra latency)
- If we wrap NONE: Ollama calls fail on transient errors (no resilience)
- Need provider-specific strategy, not one-size-fits-all

### Solution: Custom Hybrid Orchestrator

#### Design Pattern

```
Custom RetryOrchestrator
├─ DetectSdkRetryCapability(provider) → bool
│  ├─ Anthropic: true (has built-in retry)
│  ├─ OpenAI: true (has built-in retry)
│  ├─ Ollama: false (no retry)
│  └─ Others: detect based on SDK inspection
│
├─ DecideRetryStrategy(provider) → Strategy
│  ├─ If has_retry: SKIP (let SDK handle)
│  ├─ If no_retry: WRAP (we implement)
│  └─ If configurable: PRESERVE (let user config override)
│
└─ ExecuteWithRetry(api_call, strategy, max_retries=3)
   ├─ Attempt 0: try call, record latency
   ├─ Failure: classify error (retryable? timeout vs. auth vs. rate limit?)
   ├─ Retryable: backoff_ms = base_delay * (2 ** attempt_number)
   │  ├─ Attempt 1: wait, retry
   │  ├─ Attempt 2: wait longer, retry
   │  └─ Attempt 3: give up, raise
   └─ Non-retryable: raise immediately (no point retrying auth errors)
```

#### 2.1: Retry Configuration

**File:** `src/css/core/resilience/config.py`

```python
from dataclasses import dataclass, field
from enum import Enum

class RetryStrategy(str, Enum):
    """Retry strategy for a provider."""
    SKIP = "skip"           # Provider has retry, don't wrap
    WRAP = "wrap"           # Provider lacks retry, wrap it
    PRESERVE = "preserve"   # Provider retry is configurable, preserve it

class RetryableErrorType(str, Enum):
    """Error types.py that warrant retrying."""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    GATEWAY_ERROR = "gateway_error"
    CONNECTION_ERROR = "connection_error"
    
    # Non-retryable
    AUTHENTICATION = "authentication"  # Don't retry
    INVALID_REQUEST = "invalid_request"  # Don't retry
    NOT_FOUND = "not_found"  # Don't retry

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    
    # Jitter: random multiplier 0.9-1.1 to avoid thundering herd
    jitter_min: float = 0.9
    jitter_max: float = 1.1
    
    # Which errors to retry
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
        """Calculate backoff time for this attempt."""
        delay = self.base_delay_seconds * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay_seconds)
        
        # Add jitter
        import random
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        return delay * jitter
```

#### 2.2: Retry Detection

**File:** `src/css/core/resilience/detection.py`

```python
from core.types import ProviderType
from .config import RetryStrategy
import inspect

class RetryDetector:
    """Auto-detect SDK retry capabilities."""
    
    # Known retry capabilities (can be discovered at runtime)
    KNOWN_STRATEGIES = {
        ProviderType.ANTHROPIC: RetryStrategy.SKIP,      # Has built-in retry
        ProviderType.OPENAI: RetryStrategy.SKIP,         # Has built-in retry
        ProviderType.GEMINI: RetryStrategy.SKIP,         # Has built-in retry
        ProviderType.GROQ: RetryStrategy.SKIP,           # Has built-in retry
        ProviderType.MISTRAL: RetryStrategy.SKIP,        # Has built-in retry
        
        ProviderType.OLLAMA: RetryStrategy.WRAP,         # No retry
        ProviderType.NVIDIA: RetryStrategy.WRAP,         # No retry (custom)
    }
    
    @staticmethod
    def get_strategy(provider_id: ProviderType) -> RetryStrategy:
        """Get retry strategy for provider."""
        if provider_id in RetryDetector.KNOWN_STRATEGIES:
            return RetryDetector.KNOWN_STRATEGIES[provider_id]
        
        # Default: WRAP (safe default, implement retry for unknown providers)
        return RetryStrategy.WRAP
    
    @staticmethod
    def detect_sdk_has_retry(sdk_instance) -> bool:
        """Heuristic: check if SDK has retry capability."""
        # Look for retry-related attributes
        retry_indicators = ['retry', 'max_retries', 'retries', '_retry']
        
        for attr in dir(sdk_instance):
            if any(indicator in attr.lower() for indicator in retry_indicators):
                return True
        
        # Check __init__ signature for max_retries parameter
        init_sig = inspect.signature(sdk_instance.__init__)
        if 'max_retries' in init_sig.parameters:
            return True
        
        return False
```

#### 2.3: Retry Orchestrator

**File:** `src/css/core/resilience/orchestrator.py`

```python
import asyncio
import logging
import random
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from core.types import ProviderType
from .config import RetryConfig, RetryStrategy, RetryableErrorType
from .detection import RetryDetector

logger = logging.getLogger(__name__)

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
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

@dataclass
class RetryResult:
    """Result of retry attempt(s)."""
    success: bool
    result: Optional[Any] = None
    error: Optional[Exception] = None
    attempts: list[RetryAttempt] = None
    total_retries: int = 0
    total_latency_ms: float = 0.0

class RetryOrchestrator:
    """Orchestrates retries across all providers (custom hybrid approach)."""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def get_strategy(self, provider_id: ProviderType) -> RetryStrategy:
        """Get retry strategy for provider."""
        return RetryDetector.get_strategy(provider_id)
    
    def classify_error(self, error: Exception) -> RetryableErrorType:
        """Classify error to determine if retryable."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Map error patterns to types.py
        if any(word in error_str for word in ['timeout', 'timed out']):
            return RetryableErrorType.TIMEOUT
        
        if any(word in error_str for word in ['rate limit', '429']):
            return RetryableErrorType.RATE_LIMIT
        
        if any(word in error_str for word in ['503', 'unavailable', 'service down']):
            return RetryableErrorType.SERVICE_UNAVAILABLE
        
        if any(word in error_str for word in ['502', '504', 'gateway', 'bad gateway']):
            return RetryableErrorType.GATEWAY_ERROR
        
        if any(word in error_str for word in ['connection', 'refused', 'unreachable']):
            return RetryableErrorType.CONNECTION_ERROR
        
        if any(word in error_str for word in ['401', 'unauthorized', 'auth']):
            return RetryableErrorType.AUTHENTICATION
        
        if any(word in error_str for word in ['400', 'invalid', 'bad request']):
            return RetryableErrorType.INVALID_REQUEST
        
        if any(word in error_str for word in ['404', 'not found']):
            return RetryableErrorType.NOT_FOUND
        
        # Default: treat as non-retryable (safe default)
        return RetryableErrorType.INVALID_REQUEST
    
    def is_retryable(self, error: Exception) -> bool:
        """Check if error should trigger retry."""
        error_type = self.classify_error(error)
        return error_type in self.config.retryable_errors
    
    async def execute_with_retry(
        self,
        api_call: Callable,
        provider_id: ProviderType,
        *args,
        **kwargs
    ) -> RetryResult:
        """
        Execute API call with retry logic.
        
        Usage:
            orchestrator = RetryOrchestrator()
            result = await orchestrator.execute_with_retry(
                api_call=sdk.call_llm,
                provider_id=ProviderType.OLLAMA,
                model_id="mistral",
                messages=messages
            )
            
            if result.success:
                response = result.result
            else:
                raise result.error
        """
        
        strategy = self.get_strategy(provider_id)
        
        # If provider has built-in retry, don't wrap
        if strategy == RetryStrategy.SKIP:
            logger.debug(f"{provider_id}: Skipping custom retry (SDK has built-in)")
            try:
                result = await api_call(*args, **kwargs)
                return RetryResult(success=True, result=result, attempts=[
                    RetryAttempt(attempt_number=0, start_time=datetime.now(), success=True)
                ])
            except Exception as e:
                return RetryResult(success=False, error=e, attempts=[
                    RetryAttempt(attempt_number=0, start_time=datetime.now(), error=e)
                ])
        
        # Otherwise, implement custom retry
        attempts: list[RetryAttempt] = []
        total_latency = 0.0
        
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
                
                # Check if retryable
                if not self.is_retryable(e):
                    logger.warning(f"{provider_id}: Non-retryable error: {e}")
                    return RetryResult(
                        success=False,
                        error=e,
                        attempts=attempts,
                        total_retries=attempt,
                        total_latency_ms=total_latency
                    )
                
                # If this was last attempt, return error
                if attempt >= self.config.max_retries:
                    logger.error(f"{provider_id}: Max retries exceeded after {attempt + 1} attempts")
                    return RetryResult(
                        success=False,
                        error=e,
                        attempts=attempts,
                        total_retries=attempt,
                        total_latency_ms=total_latency
                    )
                
                # Calculate backoff and wait
                backoff_ms = self.config.backoff_for_attempt(attempt)
                logger.warning(f"{provider_id}: Retryable error, waiting {backoff_ms:.1f}ms before retry: {e}")
                
                await asyncio.sleep(backoff_ms / 1000.0)
        
        # Should not reach here
        return RetryResult(
            success=False,
            error=RuntimeError("Retry loop completed without result"),
            attempts=attempts,
            total_retries=self.config.max_retries,
            total_latency_ms=total_latency
        )
```

#### 2.4: Integration with BaseApiServiceClient

The retry orchestrator should be used by each provider, OR by a wrapper layer above all providers. 

**Option A: Wrapper Layer (Recommended)**
```python
# src/api_services/retry_wrapper.py
class RetryWrappedApiService:
    """Wraps any API service with retry logic."""
    
    def __init__(self, service: BaseApiServiceClient, orchestrator: RetryOrchestrator):
        self.service = service
        self.orchestrator = orchestrator
    
    async def call_llm(self, model_id: str, messages: list[Message], **kwargs):
        """Call LLM with retry."""
        result = await self.orchestrator.execute_with_retry(
            api_call=self.service.call_llm,
            provider_id=self.service.provider_id,
            model_id=model_id,
            messages=messages,
            **kwargs
        )
        
        if result.success:
            return result.result
        else:
            raise result.error
```

### Testing Requirements

- [ ] Detect Anthropic SDK has retry → strategy = SKIP
- [ ] Detect OpenAI SDK has retry → strategy = SKIP
- [ ] Detect Ollama SDK no retry → strategy = WRAP
- [ ] Classify timeout error → RetryableErrorType.TIMEOUT
- [ ] Classify auth error → RetryableErrorType.AUTHENTICATION (non-retryable)
- [ ] Classify rate limit error → RetryableErrorType.RATE_LIMIT
- [ ] Execute with retry: success on first attempt
- [ ] Execute with retry: success after 2 failures
- [ ] Execute with retry: fail after max retries exceeded
- [ ] Backoff calculation: exponential with jitter
- [ ] Non-retryable errors raise immediately
- [ ] Metrics: track attempt count, total latency

---

## Issue #3: Error Code Mapping (Days 3-4)

### Problem Statement

**Current State:**
- Each SDK throws different exception types
- No unified error classification
- Hard to write error handling logic that works across providers

**Goal:**
Map all SDK errors to a unified 5-type hierarchy:
- `AuthError` — Authentication/authorization failed
- `RateLimitError` — Rate limit exceeded
- `TimeoutError` — Request timed out
- `GatewayError` — Provider error (5xx)
- `UnknownError` — Everything else

### Solution: Exception Hierarchy + Per-SDK Mappers

#### 3.1: Exception Hierarchy

**File:** `src/core/exceptions.py` (extend existing)

```python
from typing import Optional, Any

class CyberSecSuiteError(Exception):
    """Base exception for all framework errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        provider: Optional[str] = None,
        original_error: Optional[Exception] = None,
        metadata: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.provider = provider
        self.original_error = original_error
        self.metadata = metadata or {}
        super().__init__(message)

class AuthError(CyberSecSuiteError):
    """Authentication or authorization failed."""
    pass

class RateLimitError(CyberSecSuiteError):
    """Rate limit exceeded."""
    retry_after_seconds: Optional[float] = None

class TimeoutError(CyberSecSuiteError):
    """Request timed out."""
    pass

class GatewayError(CyberSecSuiteError):
    """Provider returned 5xx or service unavailable."""
    pass

class UnknownError(CyberSecSuiteError):
    """Unclassified error."""
    pass
```

#### 3.2: Per-SDK Error Mappers

**File:** `src/api_services/error_mappers.py`

```python
from core.exceptions import (
    AuthError, RateLimitError, TimeoutError, GatewayError, UnknownError
)
from core.types import ProviderType

def map_anthropic_error(error: Exception) -> CyberSecSuiteError:
    """Map Anthropic SDK errors to framework errors."""
    # Anthropic uses anthropic.APIError, anthropic.AuthenticationError, etc.
    error_str = str(error).lower()
    
    if 'authentication' in error_str or 'unauthorized' in error_str:
        return AuthError(str(error), provider="anthropic", original_error=error)
    
    if 'rate limit' in error_str:
        err = RateLimitError(str(error), provider="anthropic", original_error=error)
        # Try to extract retry-after
        if 'retry-after' in error_str:
            # Parse retry-after from error message
            pass
        return err
    
    if 'timeout' in error_str:
        return TimeoutError(str(error), provider="anthropic", original_error=error)
    
    if any(code in error_str for code in ['500', '502', '503', '504']):
        return GatewayError(str(error), provider="anthropic", original_error=error)
    
    return UnknownError(str(error), provider="anthropic", original_error=error)

def map_openai_error(error: Exception) -> CyberSecSuiteError:
    """Map OpenAI SDK errors to framework errors."""
    # Similar pattern for OpenAI
    ...

def map_ollama_error(error: Exception) -> CyberSecSuiteError:
    """Map Ollama errors (usually aiohttp exceptions)."""
    # Similar pattern
    ...

# Dispatcher
ERROR_MAPPERS = {
    ProviderType.ANTHROPIC: map_anthropic_error,
    ProviderType.OPENAI: map_openai_error,
    ProviderType.OLLAMA: map_ollama_error,
    # ... other providers
}

def map_provider_error(provider_id: ProviderType, error: Exception) -> CyberSecSuiteError:
    """Map any provider error to framework error."""
    mapper = ERROR_MAPPERS.get(provider_id)
    if mapper:
        return mapper(error)
    
    # Default: wrap as UnknownError
    return UnknownError(str(error), provider=provider_id.value, original_error=error)
```

### Testing Requirements

- [ ] Anthropic "Unauthorized" → AuthError
- [ ] OpenAI 401 → AuthError
- [ ] Anthropic "Rate limit exceeded" → RateLimitError
- [ ] OpenAI 429 → RateLimitError
- [ ] Timeout exception → TimeoutError
- [ ] 503 Service Unavailable → GatewayError
- [ ] Unknown error → UnknownError
- [ ] Metadata preserved (original_error, provider)

---

## Issue #7: Resource Cleanup + Connection Pooling

### (Details deferred until Week 6 when StreamController design complete)

---

## Issue #8: Token Counting Framework

### (Details deferred until Week 5 when FallbackChain complete)

---

## Integration Points

- Issue #2 (Retry) → Used by all provider calls in BaseApiServiceClient
- Issue #3 (Errors) → Raised by all provider calls, caught by retry orchestrator
- Issue #7 (Cleanup) → Applied to connection pooling in BaseApiServiceClient context manager
- Issue #8 (Tokens) → Called during stream processing to estimate token counts
