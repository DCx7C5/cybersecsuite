"""Tests for hooks.config: YAML-based hook configuration."""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from hooks.config import (
    HookConfig,
    HookEventConfig,
    HookHandlerConfig,
    PerformanceConfig,
)

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class TestHookHandlerConfig:
    """Test HookHandlerConfig dataclass."""

    def test_handler_config_defaults(self):
        """Handler should have sensible defaults."""
        handler = HookHandlerConfig(name="test_handler")
        assert handler.name == "test_handler"
        assert handler.enabled is True
        assert handler.pattern is None
        assert handler.extra == {}

    def test_handler_config_with_pattern(self):
        """Handler should support regex patterns."""
        handler = HookHandlerConfig(
            name="write_guard",
            enabled=True,
            pattern="Write|Edit|Bash",
        )
        assert handler.pattern == "Write|Edit|Bash"

    def test_handler_config_from_dict(self):
        """Handler should load from dict."""
        data = {
            "name": "audit",
            "enabled": True,
            "pattern": ".*",
            "extra": {"level": "debug"},
        }
        handler = HookHandlerConfig.from_dict(data)
        assert handler.name == "audit"
        assert handler.enabled is True
        assert handler.pattern == ".*"
        assert handler.extra == {"level": "debug"}

    def test_handler_config_from_dict_minimal(self):
        """Handler should have defaults when loading minimal dict."""
        handler = HookHandlerConfig.from_dict({"name": "test"})
        assert handler.name == "test"
        assert handler.enabled is True
        assert handler.pattern is None
        assert handler.extra == {}

    def test_handler_config_disabled(self):
        """Handler should support being disabled."""
        handler = HookHandlerConfig(
            name="optional_handler",
            enabled=False,
        )
        assert handler.enabled is False


class TestHookEventConfig:
    """Test HookEventConfig dataclass."""

    def test_event_config_defaults(self):
        """Event should have sensible defaults."""
        event = HookEventConfig()
        assert event.enabled is True
        assert event.handlers == []

    def test_event_config_with_handlers(self):
        """Event should support multiple handlers."""
        handlers = [
            HookHandlerConfig(name="audit"),
            HookHandlerConfig(name="write_guard"),
        ]
        event = HookEventConfig(enabled=True, handlers=handlers)
        assert len(event.handlers) == 2
        assert event.handlers[0].name == "audit"

    def test_event_config_from_dict(self):
        """Event should load from dict."""
        data = {
            "enabled": True,
            "handlers": [
                {"name": "audit", "enabled": True},
                {"name": "write_guard", "enabled": True, "pattern": "Write|Edit"},
            ],
        }
        event = HookEventConfig.from_dict(data)
        assert event.enabled is True
        assert len(event.handlers) == 2
        assert event.handlers[0].name == "audit"
        assert event.handlers[1].pattern == "Write|Edit"

    def test_event_config_from_dict_empty_handlers(self):
        """Event should handle missing handlers."""
        event = HookEventConfig.from_dict({"enabled": False})
        assert event.enabled is False
        assert event.handlers == []

    def test_event_config_disabled(self):
        """Event should support being disabled."""
        event = HookEventConfig(enabled=False)
        assert event.enabled is False


class TestPerformanceConfig:
    """Test PerformanceConfig dataclass."""

    def test_performance_config_defaults(self):
        """Performance config should have sensible defaults."""
        perf = PerformanceConfig()
        assert perf.budget_no_op_ms == 2.0
        assert perf.budget_validated_ms == 10.0
        assert perf.slow_hook_threshold_ms == 10.0

    def test_performance_config_custom_budgets(self):
        """Performance config should support custom budgets."""
        perf = PerformanceConfig(
            budget_no_op_ms=1.0,
            budget_validated_ms=5.0,
            slow_hook_threshold_ms=15.0,
        )
        assert perf.budget_no_op_ms == 1.0
        assert perf.budget_validated_ms == 5.0
        assert perf.slow_hook_threshold_ms == 15.0

    def test_performance_config_from_dict(self):
        """Performance config should load from dict."""
        data = {
            "budget_no_op_ms": 1.5,
            "budget_validated_ms": 8.0,
            "slow_hook_threshold_ms": 12.0,
        }
        perf = PerformanceConfig.from_dict(data)
        assert perf.budget_no_op_ms == 1.5
        assert perf.budget_validated_ms == 8.0
        assert perf.slow_hook_threshold_ms == 12.0

    def test_performance_config_from_dict_partial(self):
        """Performance config should use defaults for missing values."""
        perf = PerformanceConfig.from_dict({"budget_no_op_ms": 1.0})
        assert perf.budget_no_op_ms == 1.0
        assert perf.budget_validated_ms == 10.0  # default
        assert perf.slow_hook_threshold_ms == 10.0  # default


class TestHookConfig:
    """Test HookConfig main configuration class."""

    def test_hook_config_defaults(self):
        """Hook config should have sensible defaults."""
        config = HookConfig()
        assert config.version == "1.0"
        assert config.hooks == {}
        assert isinstance(config.performance, PerformanceConfig)

    def test_hook_config_from_dict_empty(self):
        """Hook config should handle empty dict."""
        config = HookConfig.from_dict({})
        assert config.version == "1.0"
        assert config.hooks == {}

    def test_hook_config_from_dict_with_hooks(self):
        """Hook config should load hooks from dict."""
        data = {
            "version": "1.0",
            "hooks": {
                "pre_tool_use": {
                    "enabled": True,
                    "handlers": [
                        {"name": "write_guard", "enabled": True},
                        {"name": "audit", "enabled": True},
                    ],
                },
                "post_tool_use": {
                    "enabled": True,
                    "handlers": [
                        {"name": "audit", "enabled": True},
                    ],
                },
            },
        }
        config = HookConfig.from_dict(data)
        assert config.version == "1.0"
        assert len(config.hooks) == 2
        assert "pre_tool_use" in config.hooks
        assert "post_tool_use" in config.hooks
        assert len(config.hooks["pre_tool_use"].handlers) == 2

    def test_hook_config_is_event_enabled(self):
        """Hook config should check if event is enabled."""
        data = {
            "hooks": {
                "pre_tool_use": {"enabled": True},
                "post_tool_use": {"enabled": False},
            },
        }
        config = HookConfig.from_dict(data)
        assert config.is_event_enabled("pre_tool_use") is True
        assert config.is_event_enabled("post_tool_use") is False
        # Event not in config defaults to enabled
        assert config.is_event_enabled("unknown_event") is True

    def test_hook_config_get_handlers_for_event(self):
        """Hook config should return handlers for enabled event."""
        data = {
            "hooks": {
                "pre_tool_use": {
                    "enabled": True,
                    "handlers": [
                        {"name": "write_guard", "enabled": True},
                        {"name": "audit", "enabled": False},
                        {"name": "optional", "enabled": True},
                    ],
                },
            },
        }
        config = HookConfig.from_dict(data)
        handlers = config.get_handlers_for_event("pre_tool_use")
        assert len(handlers) == 2
        assert handlers[0].name == "write_guard"
        assert handlers[1].name == "optional"

    def test_hook_config_get_handlers_event_disabled(self):
        """Hook config should return empty list if event disabled."""
        data = {
            "hooks": {
                "pre_tool_use": {
                    "enabled": False,
                    "handlers": [
                        {"name": "write_guard", "enabled": True},
                    ],
                },
            },
        }
        config = HookConfig.from_dict(data)
        handlers = config.get_handlers_for_event("pre_tool_use")
        assert handlers == []

    def test_hook_config_get_handlers_event_not_found(self):
        """Hook config should return empty list for unknown event."""
        config = HookConfig()
        handlers = config.get_handlers_for_event("unknown_event")
        assert handlers == []

    def test_hook_config_with_performance(self):
        """Hook config should include performance config."""
        data = {
            "performance": {
                "budget_no_op_ms": 1.0,
                "budget_validated_ms": 5.0,
                "slow_hook_threshold_ms": 15.0,
            },
        }
        config = HookConfig.from_dict(data)
        assert config.performance.budget_no_op_ms == 1.0
        assert config.performance.budget_validated_ms == 5.0
        assert config.performance.slow_hook_threshold_ms == 15.0

    def test_hook_config_to_dict(self):
        """Hook config should serialize back to dict."""
        data = {
            "version": "1.0",
            "hooks": {
                "pre_tool_use": {
                    "enabled": True,
                    "handlers": [
                        {"name": "audit", "enabled": True, "pattern": None, "extra": {}},
                    ],
                },
            },
            "performance": {
                "budget_no_op_ms": 2.0,
                "budget_validated_ms": 10.0,
                "slow_hook_threshold_ms": 10.0,
            },
        }
        config = HookConfig.from_dict(data)
        serialized = config.to_dict()
        assert serialized["version"] == "1.0"
        assert "pre_tool_use" in serialized["hooks"]
        assert serialized["performance"]["budget_no_op_ms"] == 2.0

    def test_hook_config_roundtrip(self):
        """Hook config should support dict roundtrip."""
        data = {
            "version": "1.0",
            "hooks": {
                "pre_tool_use": {
                    "enabled": True,
                    "handlers": [
                        {"name": "write_guard", "enabled": True, "pattern": "Write|Edit"},
                    ],
                },
            },
        }
        config1 = HookConfig.from_dict(data)
        serialized = config1.to_dict()
        config2 = HookConfig.from_dict(serialized)
        
        assert config2.version == config1.version
        assert len(config2.hooks) == len(config1.hooks)
        assert config2.is_event_enabled("pre_tool_use") == config1.is_event_enabled("pre_tool_use")


class TestHookConfigYAML:
    """Test YAML loading functionality."""

    def test_hook_config_from_yaml_file(self):
        """Hook config should load from YAML file."""
        yaml_content = """
version: "1.0"
hooks:
  pre_tool_use:
    enabled: true
    handlers:
      - name: write_guard
        enabled: true
      - name: audit
        enabled: true
performance:
  budget_no_op_ms: 2.0
  budget_validated_ms: 10.0
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            config = HookConfig.from_yaml(temp_path)
            assert config.version == "1.0"
            assert "pre_tool_use" in config.hooks
            assert config.is_event_enabled("pre_tool_use") is True
        finally:
            temp_path.unlink()

    def test_hook_config_from_yaml_not_found(self):
        """Hook config should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            HookConfig.from_yaml(Path("/nonexistent/path/hooks.yaml"))

    def test_hook_config_from_yaml_complex(self):
        """Hook config should load complex YAML structures."""
        yaml_content = """
version: "1.0"
hooks:
  pre_tool_use:
    enabled: true
    handlers:
      - name: write_guard
        enabled: true
        pattern: "Write|Edit|Bash"
        extra:
          validation_level: strict
      - name: audit
        enabled: true
        pattern: ".*"
  post_tool_use:
    enabled: true
    handlers:
      - name: audit
        enabled: true
  streaming:
    enabled: false
performance:
  budget_no_op_ms: 1.0
  budget_validated_ms: 8.0
  slow_hook_threshold_ms: 15.0
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            config = HookConfig.from_yaml(temp_path)
            assert config.version == "1.0"
            assert config.is_event_enabled("pre_tool_use") is True
            assert config.is_event_enabled("streaming") is False
            assert len(config.get_handlers_for_event("pre_tool_use")) == 2
            assert config.performance.budget_no_op_ms == 1.0
            
            # Check handler extras
            handlers = config.get_handlers_for_event("pre_tool_use")
            write_guard = [h for h in handlers if h.name == "write_guard"][0]
            assert write_guard.extra.get("validation_level") == "strict"
        finally:
            temp_path.unlink()

    def test_hook_config_from_yaml_empty_file(self):
        """Hook config should handle empty YAML file."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            temp_path = Path(f.name)
        
        try:
            config = HookConfig.from_yaml(temp_path)
            assert config.version == "1.0"
            assert config.hooks == {}
        finally:
            temp_path.unlink()


class TestHookConfigIntegration:
    """Integration tests with defaults file."""

    def test_default_hooks_yaml_exists(self):
        """Default hooks.yaml should exist and be loadable."""
        hooks_yaml_path = Path(__file__).resolve().parent.parent.parent / "src" / "hooks" / "hooks.yaml"
        assert hooks_yaml_path.exists(), f"Default hooks.yaml not found at {hooks_yaml_path}"
        
        # Should be loadable
        config = HookConfig.from_yaml(hooks_yaml_path)
        assert config.version == "1.0"
        assert len(config.hooks) > 0

    def test_default_hooks_yaml_events_enabled(self):
        """Default hooks.yaml should have key events enabled."""
        hooks_yaml_path = Path(__file__).resolve().parent.parent.parent / "src" / "hooks" / "hooks.yaml"
        config = HookConfig.from_yaml(hooks_yaml_path)
        
        # Key events should be enabled
        assert config.is_event_enabled("pre_tool_use") is True
        assert config.is_event_enabled("post_tool_use") is True
        assert config.is_event_enabled("streaming_token") is True

    def test_default_hooks_yaml_handlers(self):
        """Default hooks.yaml should have handlers for each event."""
        hooks_yaml_path = Path(__file__).resolve().parent.parent.parent / "src" / "hooks" / "hooks.yaml"
        config = HookConfig.from_yaml(hooks_yaml_path)
        
        # Each enabled event should have at least one handler
        for event_type, event_config in config.hooks.items():
            if event_config.enabled:
                handlers = config.get_handlers_for_event(event_type)
                assert len(handlers) > 0, f"Event {event_type} has no enabled handlers"

    def test_default_hooks_yaml_performance_budgets(self):
        """Default hooks.yaml should have reasonable performance budgets."""
        hooks_yaml_path = Path(__file__).resolve().parent.parent.parent / "src" / "hooks" / "hooks.yaml"
        config = HookConfig.from_yaml(hooks_yaml_path)
        
        # Budgets should be positive
        assert config.performance.budget_no_op_ms > 0
        assert config.performance.budget_validated_ms > 0
        assert config.performance.slow_hook_threshold_ms > 0
        
        # no_op budget should be < validated budget
        assert config.performance.budget_no_op_ms < config.performance.budget_validated_ms
