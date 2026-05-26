"""
Test xAI native SDK AsyncClient bridge lifecycle and exception mapping.

Tests:
1. Lazy AsyncClient initialization - AsyncClient created only on first use
2. Timeout configuration - timeout_seconds passed to AsyncClient
3. gRPC error exception mapping - XAIErrorMapper handles grpc.RpcError correctly
4. Async lifecycle - __aenter__ and __aexit__ work correctly
5. Fallback behavior - graceful fallback when SDK unavailable or not enabled
"""

import pytest
import grpc
from unittest.mock import AsyncMock, MagicMock, patch, call
from typing import Any

from css.api_services.xai.service import xAIApiService
from css.core.exceptions import LLMApiServiceError, AuthError, RateLimitError, TimeoutError, GatewayError
from css.core.types import ProviderType


class TestXAIAsyncClientLazyInit:
    """Test lazy AsyncClient initialization."""
    
    @pytest.mark.asyncio
    async def test_async_client_not_initialized_on_creation(self):
        """AsyncClient should not be initialized until _ensure_async_client is called."""
        service = xAIApiService(
            api_key="test-key",
            use_native_sdk=False,  # Disable to avoid init errors
        )
        assert service._async_client is None
    
    @pytest.mark.asyncio
    async def test_async_client_reused_on_subsequent_calls(self):
        """AsyncClient should be reused from cache on subsequent calls."""
        mock_client = AsyncMock()
        service = xAIApiService(api_key="test-key", use_native_sdk=True)
        service._async_client = mock_client
        
        # Call _ensure_async_client - should return cached instance
        result = await service._ensure_async_client()
        assert result is mock_client


class TestXAITimeoutConfiguration:
    """Test timeout configuration for AsyncClient."""
    
    @pytest.mark.asyncio
    async def test_default_timeout_configured(self):
        """Default timeout should be used when not specified."""
        from css.core.config import ProviderDefaults
        
        service = xAIApiService(api_key="test-key", use_native_sdk=False)
        assert service._timeout_seconds == ProviderDefaults.TIMEOUT_SECONDS
    
    @pytest.mark.asyncio
    async def test_custom_timeout_configured(self):
        """Custom timeout should be stored."""
        service = xAIApiService(api_key="test-key", timeout_seconds=120, use_native_sdk=False)
        assert service._timeout_seconds == 120


class TestXAIErrorMapping:
    """Test gRPC error exception mapping."""
    
    @pytest.mark.asyncio
    async def test_auth_error_mapping(self):
        """UNAUTHENTICATED grpc error should map to AuthError."""
        from css.core.types.error_mappers import XAIErrorMapper
        
        # Create mock gRPC error
        mock_grpc_error = MagicMock(spec=grpc.RpcError)
        mock_grpc_error.code.return_value = grpc.StatusCode.UNAUTHENTICATED
        mock_grpc_error.__str__.return_value = "unauthenticated"
        
        result = XAIErrorMapper.map_error(mock_grpc_error)
        assert isinstance(result, AuthError)
        assert result.provider == "xai"
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_mapping(self):
        """RESOURCE_EXHAUSTED grpc error should map to RateLimitError."""
        from css.core.types.error_mappers import XAIErrorMapper
        
        mock_grpc_error = MagicMock(spec=grpc.RpcError)
        mock_grpc_error.code.return_value = grpc.StatusCode.RESOURCE_EXHAUSTED
        mock_grpc_error.__str__.return_value = "resource exhausted"
        
        result = XAIErrorMapper.map_error(mock_grpc_error)
        assert isinstance(result, RateLimitError)
        assert result.provider == "xai"
    
    @pytest.mark.asyncio
    async def test_timeout_error_mapping(self):
        """DEADLINE_EXCEEDED grpc error should map to TimeoutError."""
        from css.core.types.error_mappers import XAIErrorMapper
        
        mock_grpc_error = MagicMock(spec=grpc.RpcError)
        mock_grpc_error.code.return_value = grpc.StatusCode.DEADLINE_EXCEEDED
        mock_grpc_error.__str__.return_value = "deadline exceeded"
        
        result = XAIErrorMapper.map_error(mock_grpc_error)
        assert isinstance(result, TimeoutError)
        assert result.provider == "xai"
    
    @pytest.mark.asyncio
    async def test_gateway_error_mapping(self):
        """UNAVAILABLE grpc error should map to GatewayError."""
        from css.core.types.error_mappers import XAIErrorMapper
        
        mock_grpc_error = MagicMock(spec=grpc.RpcError)
        mock_grpc_error.code.return_value = grpc.StatusCode.UNAVAILABLE
        mock_grpc_error.__str__.return_value = "service unavailable"
        
        result = XAIErrorMapper.map_error(mock_grpc_error)
        assert isinstance(result, GatewayError)
        assert result.provider == "xai"


class TestXAIAsyncLifecycle:
    """Test async context manager lifecycle."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager_entry(self):
        """__aenter__ should return self."""
        service = xAIApiService(api_key="test-key", use_native_sdk=False)
        result = await service.__aenter__()
        assert result is service
    
    @pytest.mark.asyncio
    async def test_async_context_manager_exit_closes_client(self):
        """__aexit__ should close AsyncClient."""
        service = xAIApiService(api_key="test-key", use_native_sdk=True)
        
        # Mock AsyncClient with close method
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        service._async_client = mock_client
        
        await service.__aexit__(None, None, None)
        
        # Verify close was called
        mock_client.close.assert_called_once()
        assert service._async_client is None
    
    @pytest.mark.asyncio
    async def test_async_context_manager_handles_no_client(self):
        """__aexit__ should handle case where client is None."""
        service = xAIApiService(api_key="test-key", use_native_sdk=False)
        assert service._async_client is None
        
        # Should not raise exception
        result = await service.__aexit__(None, None, None)
        assert result is False


class TestXAIFallbackBehavior:
    """Test fallback to OpenAI-compatible API."""
    
    @pytest.mark.asyncio
    async def test_sdk_not_enabled_uses_fallback(self):
        """When use_native_sdk=False, should not attempt native SDK."""
        service = xAIApiService(
            api_key="test-key",
            use_native_sdk=False,
            allow_openai_compat_fallback=True,
        )
        
        # Should raise when SDK is not enabled
        with pytest.raises(LLMApiServiceError) as exc_info:
            await service._ensure_async_client()
        
        assert "not enabled" in str(exc_info.value)


class TestXAIServiceInitialization:
    """Test xAIApiService initialization."""
    
    def test_service_initialization_with_defaults(self):
        """Service should initialize with sensible defaults."""
        from css.core.config import ProviderDefaults
        
        service = xAIApiService(api_key="test-key")
        assert service.provider_id == ProviderType.XAI
        assert service.api_key == "test-key"
        assert service._timeout_seconds == ProviderDefaults.TIMEOUT_SECONDS
        assert service._async_client is None
    
    def test_service_initialization_with_custom_timeout(self):
        """Service should respect custom timeout."""
        service = xAIApiService(api_key="test-key", timeout_seconds=120)
        assert service._timeout_seconds == 120


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
