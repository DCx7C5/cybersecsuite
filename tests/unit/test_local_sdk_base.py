"""Tests for LocalSDK base class (Issue #5)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from css.core.types.api_services import ProviderType, StreamChunk, BaseMessage, MessageRole, LLMResponse
from css.core.exceptions import GatewayError
from css.core.types.sdk_local import LocalSDKBase


class MockLocalSDK(LocalSDKBase):
    """Concrete mock implementation for testing."""
    
    async def _fetch_available_models(self):
        """Mock model fetching."""
        return []
    
    async def _prepare_call_body(
        self,
        model_id,
        messages,
        tools,
        temperature,
        max_tokens,
        system_prompt,
        streaming,
        **kwargs,
    ):
        """Mock call body preparation."""
        return {
            "model": model_id,
            "messages": [{"role": msg.role.value, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "stream": streaming,
        }
    
    async def _execute_call(self, call_body, streaming):
        """Mock call execution."""
        if streaming:
            async def stream_response():
                yield StreamChunk(type="content_block_delta", content="Hello")
                yield StreamChunk(type="message_stop")
            return stream_response()
        else:
            return LLMResponse(
                text="Hello",
                stop_reason="stop",
                usage={},
            )


class TestLocalSDKBaseInitialization:
    """Test LocalSDK base initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        assert sdk.provider_id == ProviderType.OLLAMA
        assert sdk.base_url == "http://localhost:11434"
        assert sdk.timeout_seconds == 120
        assert sdk.max_retries == 3
        assert sdk.enable_model_auto_load is True
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.NSCALE,
            base_url="http://localhost:8000",
            timeout_seconds=300,
            max_retries=5,
            enable_model_auto_load=False,
        )
        
        assert sdk.provider_id == ProviderType.NSCALE
        assert sdk.timeout_seconds == 300
        assert sdk.max_retries == 5
        assert sdk.enable_model_auto_load is False


class TestLocalSDKBaseGetModels:
    """Test model discovery."""
    
    @pytest.mark.asyncio
    async def test_get_models_caching(self):
        """Test that models are cached after first fetch."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        mock_models = []
        
        with patch.object(sdk, '_fetch_available_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_models
            
            # First call
            models1 = await sdk.get_models()
            # Second call (should use cache)
            models2 = await sdk.get_models()
            
            # _fetch_available_models should only be called once
            assert mock_fetch.call_count == 1
            assert models1 == models2


class TestLocalSDKBaseCallLLM:
    """Test LLM calls."""
    
    @pytest.mark.asyncio
    async def test_call_llm_streaming(self):
        """Test streaming LLM call."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        chunks = []
        async for chunk in sdk.call_llm("llama2", messages, streaming=True):
            chunks.append(chunk)
        
        assert len(chunks) == 2  # content + stop
        assert chunks[0].type == "content_block_delta"
        assert chunks[1].type == "message_stop"
    
    @pytest.mark.asyncio
    async def test_call_llm_buffered(self):
        """Test buffered (non-streaming) LLM call."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        response = await sdk.call_llm("llama2", messages, streaming=False)
        
        assert isinstance(response, LLMResponse)
        assert response.text == "Hello"
        assert response.stop_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_call_llm_with_auto_load(self):
        """Test that model auto-load is called when enabled."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
            enable_model_auto_load=True,
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        with patch.object(sdk, '_ensure_model_loaded', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = True
            
            chunks = []
            async for chunk in sdk.call_llm("llama2", messages, streaming=True):
                chunks.append(chunk)
            
            mock_load.assert_called_once_with("llama2")
    
    @pytest.mark.asyncio
    async def test_call_llm_model_not_loaded(self):
        """Test that call fails if model cannot be loaded."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
            enable_model_auto_load=True,
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        with patch.object(sdk, '_ensure_model_loaded', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = False  # Cannot load
            
            with pytest.raises(GatewayError):
                async for _ in sdk.call_llm("nonexistent", messages):
                    pass
    
    @pytest.mark.asyncio
    async def test_call_llm_no_auto_load(self):
        """Test that model auto-load is skipped when disabled."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
            enable_model_auto_load=False,
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        with patch.object(sdk, '_ensure_model_loaded', new_callable=AsyncMock) as mock_load:
            chunks = []
            async for chunk in sdk.call_llm("llama2", messages, streaming=True):
                chunks.append(chunk)
            
            # Should NOT be called when auto-load disabled
            mock_load.assert_not_called()


class TestLocalSDKBaseErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_call_llm_error_mapping(self):
        """Test that errors are mapped to unified types."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        messages = [BaseMessage(role=MessageRole.USER, content="Hello")]
        
        # Mock execute_with_retry to return error
        with patch.object(sdk.retry_orchestrator, 'execute_with_retry', new_callable=AsyncMock) as mock_retry:
            mock_retry.return_value = MagicMock(
                success=False,
                error=Exception("503 Service unavailable"),
            )
            
            with pytest.raises(GatewayError):
                async for _ in sdk.call_llm("llama2", messages):
                    pass


class TestLocalSDKBaseHealthCheck:
    """Test health check."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        with patch.object(sdk, 'session') as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_session.get = AsyncMock()
            mock_session.get.return_value.__aenter__.return_value = mock_resp
            
            result = await sdk.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure_500(self):
        """Test health check failure on 500."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        with patch.object(sdk, 'session') as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 500
            mock_session.get = AsyncMock()
            mock_session.get.return_value.__aenter__.return_value = mock_resp
            
            result = await sdk.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check handles connection exceptions."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        with patch.object(sdk, 'session') as mock_session:
            mock_session.get = AsyncMock(side_effect=Exception("Connection refused"))
            
            result = await sdk.health_check()
            
            assert result is False


class TestLocalSDKBaseCacheManagement:
    """Test cache management."""
    
    @pytest.mark.asyncio
    async def test_clear_model_cache(self):
        """Test clearing model cache."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        # Set cache
        sdk._cached_models = ["model1", "model2"]
        assert sdk._cached_models is not None
        
        # Clear cache
        sdk.clear_model_cache()
        assert sdk._cached_models is None


class TestLocalSDKBaseFormatting:
    """Test error response formatting."""
    
    def test_format_error_response(self):
        """Test error formatting as StreamChunk."""
        sdk = MockLocalSDK(
            provider_id=ProviderType.OLLAMA,
            base_url="http://localhost:11434",
        )
        
        error_chunk = sdk._format_error_response("Something went wrong")
        
        assert error_chunk.type == "error"
        assert error_chunk.metadata["error"] == "Something went wrong"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
