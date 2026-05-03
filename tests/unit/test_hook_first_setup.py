"""Tests for execute_on_first_setup: atomic marker implementation."""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks.events import HookContext
from core.registries.hooks import HookRegistry


class TestIdempotency:
    """Test marker exists → skip immediately behavior."""

    @pytest.mark.asyncio
    async def test_marker_exists_skip_immediately(self, tmp_path, monkeypatch):
        """When marker exists, execute_on_first_setup should skip immediately."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"
        marker_path.touch()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result.get("skipped") is True
        assert result.get("reason") == "already_initialized"

    @pytest.mark.asyncio
    async def test_return_value_format_skip(self, tmp_path, monkeypatch):
        """When skipping, return value should be exactly {'skipped': True, 'reason': 'already_initialized'}."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"
        marker_path.touch()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result["skipped"] is True
        assert result["reason"] == "already_initialized"
        assert "marker_path" in result

    @pytest.mark.asyncio
    async def test_no_hooks_execute_on_skip(self, tmp_path, monkeypatch):
        """When marker exists, no hooks should execute."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"
        marker_path.touch()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        # Mock the hook execution
        with patch.object(HookRegistry, "get_hooks_for_event", return_value=[]):
            registry = HookRegistry()
            context = HookContext(
                correlation_id="test-corr",
                session_id="test-sess",
                timestamp=time.time(),
            )
            event: dict = {
                "project_root": "/test",
                "app_home": str(app_home),
                "hostname": "test-host",
                "triggered_by": "user",
                "hook_event_name": "OnFirstSetup",
            }

            result = await registry.execute_on_first_setup(event, context)

            assert result["skipped"] is True


class TestAtomicRaceCondition:
    """Test two concurrent calls to execute_on_first_setup."""

    @pytest.mark.asyncio
    async def test_concurrent_calls_one_initializes(self, tmp_path, monkeypatch):
        """Two concurrent calls: one should initialize, one should skip."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        # Run two concurrent calls
        result1_coro = registry.execute_on_first_setup(event, context)
        result2_coro = registry.execute_on_first_setup(event, context)

        result1, result2 = await asyncio.gather(result1_coro, result2_coro)

        # One should initialize, one should skip
        results = [result1, result2]
        initialized_count = sum(1 for r in results if r.get("initialized") is True)
        skipped_count = sum(1 for r in results if r.get("skipped") is True)

        assert initialized_count + skipped_count == 2, "Both calls should complete"

    @pytest.mark.asyncio
    async def test_marker_created_exactly_once(self, tmp_path, monkeypatch):
        """Marker file should be created exactly once even with concurrent calls."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        # Run multiple concurrent calls
        tasks = [
            registry.execute_on_first_setup(event, context) for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        # Marker should exist exactly once
        assert marker_path.exists()
        # Count initialized vs skipped
        initialized = sum(1 for r in results if r.get("initialized") is True)
        skipped = sum(1 for r in results if r.get("skipped") is True)
        assert initialized == 1
        assert skipped == 4

    @pytest.mark.asyncio
    async def test_concurrent_both_return_correctly(self, tmp_path, monkeypatch):
        """Both concurrent calls should return correct result format."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result1_coro = registry.execute_on_first_setup(event, context)
        result2_coro = registry.execute_on_first_setup(event, context)

        result1, result2 = await asyncio.gather(result1_coro, result2_coro)

        # Both should return dict with expected keys
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

        # One has "initialized": True, other has "skipped": True
        assert ("initialized" in result1 or "skipped" in result1)
        assert ("initialized" in result2 or "skipped" in result2)


class TestPartialFailure:
    """Test hook exception prevents marker write."""

    @pytest.mark.asyncio
    async def test_hook_exception_prevents_marker_write(self, tmp_path, monkeypatch):
        """If hook raises, marker file should not be created."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        # Create a mock hook that raises
        async def failing_hook(event):
            raise ValueError("Hook failed")

        registry = HookRegistry()
        # Force the hooks dict
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        # Check that marker was deleted on error
        assert not marker_path.exists()
        assert result.get("had_errors") is True

    @pytest.mark.asyncio
    async def test_marker_deleted_on_error(self, tmp_path, monkeypatch):
        """When error occurs, marker file should be deleted."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        # Create a mock hook that raises
        async def failing_hook(event):
            raise RuntimeError("Setup failed")

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        await registry.execute_on_first_setup(event, context)

        # Marker should be deleted after error
        assert not marker_path.exists()

    @pytest.mark.asyncio
    async def test_had_errors_in_return_value(self, tmp_path, monkeypatch):
        """Return value should have had_errors=True on failure."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        async def failing_hook(event):
            raise Exception("Hook error")

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result.get("had_errors") is True
        assert result.get("initialized") is False

    @pytest.mark.asyncio
    async def test_subsequent_call_after_failure_can_retry(self, tmp_path, monkeypatch):
        """After failure, subsequent call should be able to retry (marker doesn't exist)."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        marker_path = app_home / ".initialized"

        # First call fails
        async def failing_hook(event):
            raise Exception("First try failed")

        # First attempt with failing hook
        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result1 = await registry.execute_on_first_setup(event, context)
        assert result1.get("had_errors") is True
        # Marker should be deleted on error
        assert not marker_path.exists()

        # Second attempt should be able to run (no existing marker)
        async def success_hook(event):
            return {"result": "success"}

        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[success_hook])]}
        result2 = await registry.execute_on_first_setup(event, context)

        # Should succeed on retry
        assert result2.get("initialized") is True

    @pytest.mark.asyncio
    async def test_exception_context_preserved(self, tmp_path, monkeypatch):
        """Exception context should be preserved in return value."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        async def failing_hook(event):
            raise ValueError("Specific error message")

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result.get("had_errors") is True


class TestPathResolution:
    """Test marker path resolution."""

    @pytest.mark.asyncio
    async def test_respects_cybersecsuite_home_env_var(self, tmp_path, monkeypatch):
        """Should respect CYBERSECSUITE_HOME env var for marker path."""
        custom_home = tmp_path / "custom_css_home"
        custom_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(custom_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(custom_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        await registry.execute_on_first_setup(event, context)

        # Check that marker was created in custom location
        marker_path = custom_home / ".initialized"
        assert marker_path.exists()

    @pytest.mark.asyncio
    async def test_defaults_to_home_cybersecsuite_initialized(self, tmp_path, monkeypatch):
        """Should default to ~/.cybersecsuite/.initialized."""
        # Clear CYBERSECSUITE_HOME and use default
        monkeypatch.delenv("CYBERSECSUITE_HOME", raising=False)

        # Mock get_app_home to return a test directory
        mock_app_home = tmp_path / ".cybersecsuite"
        mock_app_home.mkdir()

        with patch("src.registries.hooks.get_app_home", return_value=mock_app_home):
            registry = HookRegistry()
            context = HookContext(
                correlation_id="test-corr",
                session_id="test-sess",
                timestamp=time.time(),
            )
            event: dict = {
                "project_root": "/test",
                "app_home": str(mock_app_home),
                "hostname": "test-host",
                "triggered_by": "user",
                "hook_event_name": "OnFirstSetup",
            }

            result = await registry.execute_on_first_setup(event, context)

            # Marker should be in the mocked app_home
            assert result.get("initialized") is True

    @pytest.mark.asyncio
    async def test_marker_parent_directory_created(self, tmp_path, monkeypatch):
        """Should create parent directory if it doesn't exist."""
        app_home = tmp_path / "nested" / "app" / "home" / ".cybersecsuite"
        # Don't create the directory

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        with patch("src.registries.hooks.get_app_home", return_value=app_home):
            registry = HookRegistry()
            context = HookContext(
                correlation_id="test-corr",
                session_id="test-sess",
                timestamp=time.time(),
            )
            event: dict = {
                "project_root": "/test",
                "app_home": str(app_home),
                "hostname": "test-host",
                "triggered_by": "user",
                "hook_event_name": "OnFirstSetup",
            }

            result = await registry.execute_on_first_setup(event, context)

            # Parent directory should have been created
            assert result.get("initialized") is True


class TestReturnValues:
    """Test return value formats."""

    @pytest.mark.asyncio
    async def test_skip_return_format(self, tmp_path, monkeypatch):
        """Skip return should have exact format."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()
        marker_path = app_home / ".initialized"
        marker_path.touch()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result == {
            "skipped": True,
            "reason": "already_initialized",
            "marker_path": str(marker_path),
        }

    @pytest.mark.asyncio
    async def test_success_return_format(self, tmp_path, monkeypatch):
        """Success return should have 'initialized': True."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result.get("initialized") is True

    @pytest.mark.asyncio
    async def test_partial_failure_return_format(self, tmp_path, monkeypatch):
        """Partial failure return should have 'initialized': False and 'had_errors': True."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        async def failing_hook(event):
            raise Exception("Hook failed")

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        assert result.get("initialized") is False
        assert result.get("had_errors") is True

    @pytest.mark.asyncio
    async def test_hook_outputs_preserved(self, tmp_path, monkeypatch):
        """Hook outputs should be preserved in return dict."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        async def hook_with_output(event):
            return {"custom_field": "custom_value", "setup_status": "ready"}

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[hook_with_output])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result = await registry.execute_on_first_setup(event, context)

        # Hook outputs should be preserved
        assert result.get("custom_field") == "custom_value"
        assert result.get("setup_status") == "ready"


class TestCleanup:
    """Test cleanup and persistence behavior."""

    @pytest.mark.asyncio
    async def test_marker_persistent_across_calls(self, tmp_path, monkeypatch):
        """Marker should persist across multiple calls."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        # First call
        result1 = await registry.execute_on_first_setup(event, context)
        assert result1.get("initialized") is True

        # Marker should still exist
        marker_path = app_home / ".initialized"
        assert marker_path.exists()

        # Second call should skip
        result2 = await registry.execute_on_first_setup(event, context)
        assert result2.get("skipped") is True

    @pytest.mark.asyncio
    async def test_tmp_file_cleaned_up_on_error(self, tmp_path, monkeypatch):
        """Temporary files should be cleaned up on error."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        async def failing_hook(event):
            raise Exception("Setup failed")

        registry = HookRegistry()
        registry._hooks = {"OnFirstSetup": [MagicMock(hooks=[failing_hook])]}

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        await registry.execute_on_first_setup(event, context)

        # Marker should be deleted
        marker_path = app_home / ".initialized"
        assert not marker_path.exists()

    @pytest.mark.asyncio
    async def test_marker_survives_app_restart_simulation(self, tmp_path, monkeypatch):
        """Marker should survive application restart (simulated by new registry)."""
        app_home = tmp_path / ".cybersecsuite"
        app_home.mkdir()

        monkeypatch.setenv("CYBERSECSUITE_HOME", str(app_home))

        # First "run"
        registry1 = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        event: dict = {
            "project_root": "/test",
            "app_home": str(app_home),
            "hostname": "test-host",
            "triggered_by": "user",
            "hook_event_name": "OnFirstSetup",
        }

        result1 = await registry1.execute_on_first_setup(event, context)
        assert result1.get("initialized") is True

        # Simulate restart with new registry instance
        registry2 = HookRegistry()
        result2 = await registry2.execute_on_first_setup(event, context)

        # Should skip because marker persisted
        assert result2.get("skipped") is True
