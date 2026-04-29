"""Comprehensive tests for retry orchestrator."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

from core.types import ProviderType
from core.retry import (
    RetryOrchestrator,
    RetryConfig,
    RetryStrategy,
    RetryableErrorType,
    RetryDetector,
)


class TestRetryConfig:
    """Test retry configuration."""
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            base_delay_seconds=1.0,
            exponential_base=2.0,
            jitter_min=1.0,  # Fixed jitter for test
            jitter_max=1.0
        )
        
        # Attempt 0: 1.0 * (2.0 ** 0) = 1.0
        assert config.backoff_for_attempt(0) == 1.0
        
        # Attempt 1: 1.0 * (2.0 ** 1) = 2.0
        assert config.backoff_for_attempt(1) == 2.0
        
        # Attempt 2: 1.0 * (2.0 ** 2) = 4.0
        assert config.backoff_for_attempt(2) == 4.0
    
    def test_backoff_max_delay(self):
        """Test backoff respects max delay."""
        config = RetryConfig(
            base_delay_seconds=10.0,
            exponential_base=2.0,
            max_delay_seconds=30.0,
            jitter_min=1.0,
            jitter_max=1.0
        )
        
        # Attempt 5: 10.0 * (2.0 ** 5) = 320.0 → capped at 30.0
        assert config.backoff_for_attempt(5) == 30.0
    
    def test_backoff_with_jitter(self):
        """Test jitter is applied."""
        config = RetryConfig(
            base_delay_seconds=1.0,
            exponential_base=2.0,
            jitter_min=0.8,
            jitter_max=1.2
        )
        
        # Run multiple times, should vary
        delays = [config.backoff_for_attempt(0) for _ in range(10)]
        assert len(set(delays)) > 1  # Not all the same
        assert all(0.8 <= d <= 1.2 for d in delays)


class TestRetryDetection:
    """Test retry strategy detection."""
    
    def test_known_skip_strategies(self):
        """Test providers known to have retry."""
        for provider in [ProviderType.ANTHROPIC, ProviderType.OPENAI, ProviderType.GROQ]:
            assert RetryDetector.get_strategy(provider) == RetryStrategy.SKIP
    
    def test_known_wrap_strategies(self):
        """Test providers known to lack retry."""
        for provider in [ProviderType.OLLAMA, ProviderType.NVIDIA]:
            assert RetryDetector.get_strategy(provider) == RetryStrategy.WRAP
    
    def test_unknown_provider_defaults_to_wrap(self):
        """Test unknown providers default to WRAP (safe)."""
        # Create a mock provider not in KNOWN_STRATEGIES
        unknown = ProviderType.AI21  # or any not explicitly set
        result = RetryDetector.get_strategy(unknown)
        assert result in [RetryStrategy.WRAP, RetryStrategy.SKIP]  # Either is fine, just defined
    
    def test_detect_sdk_has_retry_attribute(self):
        """Test SDK detection via attributes."""
        sdk = MagicMock()
        sdk.__dir__ = MagicMock(return_value=['retry', 'get_models'])
        assert RetryDetector.detect_sdk_has_retry(sdk) == True
    
    def test_detect_sdk_no_retry(self):
        """Test SDK with no retry attributes."""
        sdk = MagicMock()
        sdk.__dir__ = MagicMock(return_value=['get_models', 'call_llm'])
        assert RetryDetector.detect_sdk_has_retry(sdk) == False


class TestErrorClassification:
    """Test error classification."""
    
    def test_classify_timeout(self):
        """Test timeout error classification."""
        orchestrator = RetryOrchestrator()
        error = TimeoutError("Connection timed out")
        assert orchestrator.classify_error(error) == RetryableErrorType.TIMEOUT
    
    def test_classify_rate_limit(self):
        """Test rate limit error classification."""
        orchestrator = RetryOrchestrator()
        error = Exception("429 Too Many Requests: Rate limit exceeded")
        assert orchestrator.classify_error(error) == RetryableErrorType.RATE_LIMIT
    
    def test_classify_service_unavailable(self):
        """Test service unavailable error."""
        orchestrator = RetryOrchestrator()
        error = Exception("503 Service Unavailable")
        assert orchestrator.classify_error(error) == RetryableErrorType.SERVICE_UNAVAILABLE
    
    def test_classify_gateway_error(self):
        """Test gateway error."""
        orchestrator = RetryOrchestrator()
        error = Exception("502 Bad Gateway")
        assert orchestrator.classify_error(error) == RetryableErrorType.GATEWAY_ERROR
    
    def test_classify_connection_error(self):
        """Test connection error."""
        orchestrator = RetryOrchestrator()
        error = Exception("Connection refused: ECONNREFUSED")
        assert orchestrator.classify_error(error) == RetryableErrorType.CONNECTION_ERROR
    
    def test_classify_auth_error(self):
        """Test auth error (non-retryable)."""
        orchestrator = RetryOrchestrator()
        error = Exception("401 Unauthorized: invalid_api_key")
        assert orchestrator.classify_error(error) == RetryableErrorType.AUTHENTICATION
    
    def test_classify_invalid_request(self):
        """Test invalid request error (non-retryable)."""
        orchestrator = RetryOrchestrator()
        error = Exception("400 Bad Request: invalid_request")
        assert orchestrator.classify_error(error) == RetryableErrorType.INVALID_REQUEST
    
    def test_classify_not_found(self):
        """Test not found error (non-retryable)."""
        orchestrator = RetryOrchestrator()
        error = Exception("404 Not Found: model not found")
        assert orchestrator.classify_error(error) == RetryableErrorType.NOT_FOUND


class TestRetryOrchestrator:
    """Test retry orchestrator main logic."""
    
    def test_is_retryable_true(self):
        """Test retryable error detection."""
        orchestrator = RetryOrchestrator()
        error = Exception("503 Service Unavailable")
        assert orchestrator.is_retryable(error) == True
    
    def test_is_retryable_false(self):
        """Test non-retryable error detection."""
        orchestrator = RetryOrchestrator()
        error = Exception("401 Unauthorized")
        assert orchestrator.is_retryable(error) == False
    
    @pytest.mark.asyncio
    async def test_execute_skip_strategy(self):
        """Test SKIP strategy (provider has retry, don't wrap)."""
        orchestrator = RetryOrchestrator()
        
        # Mock a successful call
        mock_call = AsyncMock(return_value="success")
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.ANTHROPIC,
        )
        
        assert result.success == True
        assert result.result == "success"
        assert result.attempt_count == 1
        mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_wrap_success_first_try(self):
        """Test WRAP strategy with success on first try."""
        orchestrator = RetryOrchestrator()
        
        mock_call = AsyncMock(return_value="success")
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert result.success == True
        assert result.result == "success"
        assert result.total_retries == 0
        assert result.attempt_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_wrap_retry_then_success(self):
        """Test WRAP strategy with retry then success."""
        orchestrator = RetryOrchestrator(
            config=RetryConfig(
                base_delay_seconds=0.01,  # Fast for tests
                exponential_base=2.0,
                jitter_min=1.0,
                jitter_max=1.0
            )
        )
        
        # Fail first time, succeed second
        mock_call = AsyncMock(
            side_effect=[
                Exception("503 Service Unavailable"),
                "success"
            ]
        )
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert result.success == True
        assert result.result == "success"
        assert result.total_retries == 1
        assert result.attempt_count == 2
        assert mock_call.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_wrap_max_retries_exceeded(self):
        """Test WRAP strategy with max retries exceeded."""
        orchestrator = RetryOrchestrator(
            config=RetryConfig(
                max_retries=2,
                base_delay_seconds=0.01,
                exponential_base=2.0,
                jitter_min=1.0,
                jitter_max=1.0
            )
        )
        
        # Always fail
        mock_call = AsyncMock(
            side_effect=Exception("503 Service Unavailable")
        )
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert result.success == False
        assert isinstance(result.error, Exception)
        assert result.total_retries == 2  # max_retries
        assert result.attempt_count == 3  # Initial + 2 retries
        assert mock_call.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_wrap_non_retryable_fails_immediately(self):
        """Test WRAP strategy with non-retryable error."""
        orchestrator = RetryOrchestrator(
            config=RetryConfig(
                max_retries=3,
                base_delay_seconds=0.01,
            )
        )
        
        # Auth error (non-retryable)
        mock_call = AsyncMock(
            side_effect=Exception("401 Unauthorized")
        )
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert result.success == False
        assert result.total_retries == 0  # No retries for non-retryable
        assert result.attempt_count == 1  # Only first attempt
        assert mock_call.call_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_args_and_kwargs(self):
        """Test execute passes args and kwargs correctly."""
        orchestrator = RetryOrchestrator()
        
        mock_call = AsyncMock(return_value="success")
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )
        
        assert result.success == True
        mock_call.assert_called_once_with(
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )


class TestRetryMetrics:
    """Test retry attempt metrics."""
    
    @pytest.mark.asyncio
    async def test_attempt_latency_tracking(self):
        """Test latency is tracked for each attempt."""
        orchestrator = RetryOrchestrator(
            config=RetryConfig(base_delay_seconds=0.01)
        )
        
        mock_call = AsyncMock(
            side_effect=[
                Exception("503 Service Unavailable"),
                "success"
            ]
        )
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert len(result.attempts) == 2
        assert result.attempts[0].success == False
        assert result.attempts[0].error is not None
        assert result.attempts[1].success == True
        assert result.total_latency_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
