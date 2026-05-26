"""Tests for OllamaModelManager lifecycle and caching.

Tests core functionality:
- Manager initialization
- Error types (daemon unavailable, model not found, pull failed)
- Async context manager
"""

import pytest

from css.api_services.ollama import (
    OllamaModelManager,
    OllamaDaemonUnavailableError,
    OllamaModelNotFoundError,
    OllamaModelPullError,
)


class TestOllamaModelManagerInit:
    """Test manager initialization."""

    def test_init_default_url(self):
        """Initialize with default URL."""
        manager = OllamaModelManager()
        assert manager.base_url == "http://localhost:11434"

    def test_init_custom_url(self):
        """Initialize with custom URL."""
        manager = OllamaModelManager(base_url="http://192.168.1.100:11434")
        assert manager.base_url == "http://192.168.1.100:11434"

    def test_init_strips_trailing_slash(self):
        """Remove trailing slash from base_url."""
        manager = OllamaModelManager(base_url="http://localhost:11434/")
        assert manager.base_url == "http://localhost:11434"


class TestOllamaModelManagerErrors:
    """Test exception types."""

    def test_daemon_unavailable_error(self):
        """OllamaDaemonUnavailableError is defined."""
        exc = OllamaDaemonUnavailableError("Test")
        assert isinstance(exc, Exception)
        assert str(exc) == "Test"

    def test_model_not_found_error(self):
        """OllamaModelNotFoundError is defined."""
        exc = OllamaModelNotFoundError("Test")
        assert isinstance(exc, Exception)

    def test_model_pull_error(self):
        """OllamaModelPullError is defined."""
        exc = OllamaModelPullError("Test")
        assert isinstance(exc, Exception)


class TestOllamaModelManagerContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_async_context_manager_entry(self):
        """Enter async context manager."""
        async with OllamaModelManager() as manager:
            assert manager is not None
            assert isinstance(manager, OllamaModelManager)

    @pytest.mark.asyncio
    async def test_async_context_manager_exit(self):
        """Exit async context manager properly."""
        manager = OllamaModelManager()
        async with manager:
            pass
        # Session should be closed or None after exit


class TestOllamaModelManagerMethods:
    """Test manager methods are callable."""

    @pytest.mark.asyncio
    async def test_is_available_exists(self):
        """is_available method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "is_available")
        assert callable(manager.is_available)

    @pytest.mark.asyncio
    async def test_list_exists(self):
        """list method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "list")
        assert callable(manager.list)

    @pytest.mark.asyncio
    async def test_pull_exists(self):
        """pull method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "pull")
        assert callable(manager.pull)

    @pytest.mark.asyncio
    async def test_delete_exists(self):
        """delete method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "delete")
        assert callable(manager.delete)

    @pytest.mark.asyncio
    async def test_copy_exists(self):
        """copy method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "copy")
        assert callable(manager.copy)

    @pytest.mark.asyncio
    async def test_show_exists(self):
        """show method exists and is callable."""
        manager = OllamaModelManager()
        assert hasattr(manager, "show")
        assert callable(manager.show)


class TestOllamaModelManagerEmitter:
    """Test event emitter integration."""

    def test_emitter_initialized(self):
        """Event emitter is initialized with correct namespace."""
        manager = OllamaModelManager()
        assert manager._emitter is not None
        assert manager._emitter._namespace == "ollama.models"

    @pytest.mark.asyncio
    async def test_emitter_has_emit_method(self):
        """Emitter has emit method."""
        manager = OllamaModelManager()
        assert hasattr(manager._emitter, "emit")
        assert callable(manager._emitter.emit)


class TestOllamaModelManagerCache:
    """Test cache integration."""

    def test_cache_initialized(self):
        """Cache backend is initialized."""
        manager = OllamaModelManager()
        assert manager._cache is not None

    def test_cache_namespace(self):
        """Cache has correct namespace."""
        manager = OllamaModelManager()
        assert manager._cache.namespace == "ollama_models"

    def test_cache_ttl(self):
        """Cache TTL is configurable."""
        manager = OllamaModelManager(cache_ttl_seconds=1800)
        assert manager.cache_ttl_seconds == 1800

    def test_cache_default_ttl(self):
        """Cache TTL defaults to 3600 seconds."""
        manager = OllamaModelManager()
        assert manager.cache_ttl_seconds == 3600


__all__ = [
    "TestOllamaModelManagerInit",
    "TestOllamaModelManagerErrors",
    "TestOllamaModelManagerContextManager",
    "TestOllamaModelManagerMethods",
    "TestOllamaModelManagerEmitter",
    "TestOllamaModelManagerCache",
]
