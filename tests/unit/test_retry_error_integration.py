"""Integration test: Retry orchestrator + error mapping (Issues #2 + #3)."""

import pytest

from css.core.types.api_services import ProviderType
from css.core.retry import RetryOrchestrator, RetryConfig
from css.core.exceptions import (
    AuthError,
    RateLimitError,
)


class TestRetryOrchestrationWithErrorMapping:
    """Test retry orchestrator integration with error mapping."""
    
    @pytest.mark.asyncio
    async def test_retry_with_rate_limit_mapping(self):
        """Test that rate limit errors are caught and mapped."""
        orchestrator = RetryOrchestrator(RetryConfig(max_retries=2))
        
        # Mock API call that fails with rate limit
        call_count = 0
        
        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("429 Rate limit exceeded")
            return {"response": "success"}
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_api_call,
            provider_id=ProviderType.OPENAI,
        )
        
        assert result.success
        assert call_count == 3
        assert result.attempt_count == 3
        assert len(result.attempts) == 3
    
    @pytest.mark.asyncio
    async def test_retry_fails_on_auth_error(self):
        """Test that auth errors are NOT retried."""
        orchestrator = RetryOrchestrator()
        
        async def mock_api_call(*args, **kwargs):
            raise Exception("401 Unauthorized: invalid_api_key")
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_api_call,
            provider_id=ProviderType.ANTHROPIC,
        )
        
        assert not result.success
        assert result.attempt_count == 1  # No retries
        assert "401" in str(result.error) or "invalid" in str(result.error).lower()
    
    @pytest.mark.asyncio
    async def test_timeout_error_is_retryable(self):
        """Test that timeout errors trigger retries."""
        orchestrator = RetryOrchestrator(RetryConfig(max_retries=1))
        
        call_count = 0
        
        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Connection timed out")
            return {"response": "recovered"}
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_api_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        assert result.success
        assert call_count == 2
        assert result.total_retries == 1
    
    @pytest.mark.asyncio
    async def test_gateway_error_is_retryable(self):
        """Test that 5xx gateway errors trigger retries."""
        orchestrator = RetryOrchestrator(RetryConfig(max_retries=2))
        
        call_count = 0
        
        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("502 Bad Gateway")
            return {"response": "recovered"}
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_api_call,
            provider_id=ProviderType.GEMINI,
        )
        
        assert result.success
        assert call_count == 3
        assert result.attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that we fail after max retries exceeded."""
        orchestrator = RetryOrchestrator(RetryConfig(max_retries=2))
        
        async def mock_api_call(*args, **kwargs):
            raise Exception("503 Service unavailable")
        
        result = await orchestrator.execute_with_retry(
            api_call=mock_api_call,
            provider_id=ProviderType.GROQ,
        )
        
        assert not result.success
        assert result.attempt_count == 3  # Initial + 2 retries
        assert result.total_retries == 2


class TestErrorClassification:
    """Test error classification for retryability."""
    
    def test_classify_timeout(self):
        """Test timeout classification."""
        orchestrator = RetryOrchestrator()
        error = Exception("Connection timed out")
        from core.retry.config import RetryableErrorType
        assert orchestrator.classify_error(error) == RetryableErrorType.TIMEOUT
    
    def test_classify_rate_limit(self):
        """Test rate limit classification."""
        orchestrator = RetryOrchestrator()
        error = Exception("429 Rate limit exceeded")
        from core.retry.config import RetryableErrorType
        assert orchestrator.classify_error(error) == RetryableErrorType.RATE_LIMIT
    
    def test_classify_auth_error_as_non_retryable(self):
        """Test auth errors classified as non-retryable."""
        orchestrator = RetryOrchestrator()
        error = Exception("401 Unauthorized")
        from core.retry.config import RetryableErrorType
        assert orchestrator.classify_error(error) == RetryableErrorType.AUTHENTICATION
        assert not orchestrator.is_retryable(error)
    
    def test_classify_gateway_error_as_retryable(self):
        """Test gateway errors classified as retryable."""
        orchestrator = RetryOrchestrator()
        error = Exception("502 Bad Gateway")
        from core.retry.config import RetryableErrorType
        assert orchestrator.classify_error(error) == RetryableErrorType.GATEWAY_ERROR
        assert orchestrator.is_retryable(error)


class TestErrorMappingIntegration:
    """Test error mapping integration with retry."""
    
    def test_map_error_on_retry_failure(self):
        """Test that errors are mapped to unified types."""
        orchestrator = RetryOrchestrator()
        error = Exception("401 Unauthorized: invalid key")
        
        mapped = orchestrator.map_error_to_unified(error, ProviderType.ANTHROPIC)
        assert isinstance(mapped, AuthError)
        assert mapped.provider == "anthropic"
    
    def test_map_rate_limit_error(self):
        """Test rate limit error mapping."""
        orchestrator = RetryOrchestrator()
        error = Exception("429 Rate limit: retry-after 60")
        
        mapped = orchestrator.map_error_to_unified(error, ProviderType.OPENAI)
        assert isinstance(mapped, RateLimitError)
        assert mapped.provider == "openai"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
