"""YAML-based declarative configuration for the hook system.

This module provides:
- HookConfig: Main configuration dataclass supporting YAML loading
- HookHandlerConfig: Per-handler configuration
- HookEventConfig: Per-event configuration
- PerformanceConfig: Performance budgets and thresholds

Design:
    - Dataclass-based configuration (no Pydantic, minimal dependencies)
    - YAML loading via from_yaml() and from_dict()
    - Sensible defaults (all hooks enabled by default)
    - Event-level enable/disable
    - Handler-level enable/disable with optional pattern matching
    - Performance budgets for monitoring

Integration:
    - HookRegistry accepts optional HookConfig at init
    - Config filters enabled/disabled hooks at execution time
    - Performance budgets applied to HookInstrument
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# ── YAML Event Mapping ─────────────────────────────────────────────────

_YAML_EVENT_MAP = {
    "PreToolUse": "pre_tool_use",
    "PostToolUse": "post_tool_use",
    "PostToolUseFailure": "post_tool_use_failure",
    "UserPromptSubmit": "user_prompt_submit",
    "Stop": "stop",
    "AgentStart": "agent_start",
    "AgentStop": "agent_stop",
    "OrchestratorStart": "orchestrator_start",
    "OrchestratorStop": "orchestrator_stop",
    "PreCompact": "pre_compact",
    "PostCompact": "post_compact",
    "Notification": "notification",
    "PermissionRequest": "permission_request",
    "PreStreaming": "pre_streaming",
    "StreamingToken": "streaming_token",
    "PostStreaming": "post_streaming",
    "PreMessage": "pre_message",
    "PostMessage": "post_message",
    "PreRetry": "pre_retry",
    "OnRecovery": "on_recovery",
    "OnError": "on_error",
    "OnFirstSetup": "first_setup",
    "PlanStart": "plan_start",
    "PlanStop": "plan_stop",
    "PlanComplete": "plan_complete",
    "PlanPhaseStart": "plan_phase_start",
    "PlanPhaseStop": "plan_phase_stop",
    "PlanPhaseComplete": "plan_phase_complete",
    "PlanTaskStart": "plan_task_start",
    "PlanTaskStop": "plan_task_stop",
    "PlanTaskComplete": "plan_task_complete",
    "PlanTodoStart": "plan_todo_start",
    "PlanTodoStop": "plan_todo_stop",
    "PlanTodoComplete": "plan_todo_complete",
}





# ── Handler Configuration ──────────────────────────────────────────────────

@dataclass
class HookHandlerConfig:
    """Configuration for a single hook handler.
    
    Attributes:
        name: Handler/hook function name (e.g., "write_guard", "audit")
        enabled: Whether this handler is enabled (default True)
        pattern: Optional regex pattern to match hook names (for filtering)
        extra: Additional handler-specific configuration (key-value pairs)
    """
    name: str
    enabled: bool = True
    pattern: Optional[str] = None
    extra: dict = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "HookHandlerConfig":
        """Create HookHandlerConfig from dict (parsed YAML).
        
        Args:
            data: Dict with keys: name, enabled, pattern, extra
        
        Returns:
            HookHandlerConfig instance
        """
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            pattern=data.get("pattern"),
            extra=data.get("extra", {}),
        )


# ── Event Configuration ────────────────────────────────────────────────────

@dataclass
class HookEventConfig:
    """Configuration for a hook event type.
    
    Attributes:
        enabled: Whether this event type is enabled (default True)
        handlers: List of HookHandlerConfig for this event
    """
    enabled: bool = True
    handlers: list[HookHandlerConfig] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "HookEventConfig":
        """Create HookEventConfig from dict (parsed YAML).
        
        Args:
            data: Dict with keys: enabled, handlers
        
        Returns:
            HookEventConfig instance
        """
        handlers = []
        for handler_data in data.get("handlers", []):
            if isinstance(handler_data, dict):
                handlers.append(HookHandlerConfig.from_dict(handler_data))
        
        return cls(
            enabled=data.get("enabled", True),
            handlers=handlers,
        )


# ── Performance Configuration ──────────────────────────────────────────────

@dataclass
class PerformanceConfig:
    """Performance budgets and thresholds for hooks.
    
    Attributes:
        budget_no_op_ms: Maximum time for no-op hooks (default 2.0 ms)
        budget_validated_ms: Maximum time for validated hooks (default 10.0 ms)
        slow_hook_threshold_ms: Threshold for logging slow hooks (default 10.0 ms)
    """
    budget_no_op_ms: float = 2.0
    budget_validated_ms: float = 10.0
    slow_hook_threshold_ms: float = 10.0
    
    @classmethod
    def from_dict(cls, data: dict) -> "PerformanceConfig":
        """Create PerformanceConfig from dict (parsed YAML).
        
        Args:
            data: Dict with performance budget keys
        
        Returns:
            PerformanceConfig instance
        """
        return cls(
            budget_no_op_ms=data.get("budget_no_op_ms", 2.0),
            budget_validated_ms=data.get("budget_validated_ms", 10.0),
            slow_hook_threshold_ms=data.get("slow_hook_threshold_ms", 10.0),
        )


# ── Main Hook Configuration ────────────────────────────────────────────────

@dataclass
class HookConfig:
    """Main hook configuration from YAML.
    
    Attributes:
        version: Configuration version (default "1.0")
        hooks: Dict mapping event type to HookEventConfig
        performance: PerformanceConfig with budgets and thresholds
    """
    version: str = "1.0"
    hooks: dict[str, HookEventConfig] = field(default_factory=dict)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    @classmethod
    def from_yaml(cls, path: Path) -> "HookConfig":
        """Load configuration from YAML file.
        
        Args:
            path: Path to hooks.yaml configuration file
        
        Returns:
            HookConfig instance
        
        Raises:
            FileNotFoundError: If path does not exist
            yaml.YAMLError: If YAML parsing fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Hook config file not found: {path}")
        
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict) -> "HookConfig":
        """Load configuration from dict (parsed YAML).
        
        Args:
            data: Dict with keys: version, hooks, performance
        
        Returns:
            HookConfig instance
        """
        # Parse hooks section
        hooks_dict = {}
        for event_type, event_data in data.get("hooks", {}).items():
            if isinstance(event_data, dict):
                hooks_dict[event_type] = HookEventConfig.from_dict(event_data)
        
        # Parse performance section
        perf_data = data.get("performance", {})
        performance = PerformanceConfig.from_dict(perf_data) if isinstance(perf_data, dict) else PerformanceConfig()
        
        return cls(
            version=data.get("version", "1.0"),
            hooks=hooks_dict,
            performance=performance,
        )
    
    def is_event_enabled(self, event_type: str) -> bool:
        """Check if an event type is enabled.
        
        Args:
            event_type: Event type name (e.g., "PreToolUse")
        
        Returns:
            True if event is enabled, False otherwise
            (default True if event not found in config)
        """
        # Map PascalCase event type to snake_case YAML key
        yaml_key = _YAML_EVENT_MAP.get(event_type, event_type.lower())
        
        if yaml_key not in self.hooks:
            # Default: enable events not explicitly configured
            return True
        
        return self.hooks[yaml_key].enabled
    
    def get_handlers_for_event(self, event_type: str) -> list[HookHandlerConfig]:
        """Get all enabled handlers for an event type.
        
        Args:
            event_type: Event type name (e.g., "PreToolUse")
        
        Returns:
            List of enabled HookHandlerConfig instances
        """
        # Map PascalCase event type to snake_case YAML key
        yaml_key = _YAML_EVENT_MAP.get(event_type, event_type.lower())
        
        if yaml_key not in self.hooks:
            return []
        
        event_config = self.hooks[yaml_key]
        if not event_config.enabled:
            return []
        
        return [h for h in event_config.handlers if h.enabled]
    
    def to_dict(self) -> dict:
        """Convert configuration to dict (for serialization).
        
        Returns:
            Dict representation of configuration
        """
        return {
            "version": self.version,
            "hooks": {
                event_type: {
                    "enabled": config.enabled,
                    "handlers": [
                        {
                            "name": h.name,
                            "enabled": h.enabled,
                            "pattern": h.pattern,
                            "extra": h.extra,
                        }
                        for h in config.handlers
                    ],
                }
                for event_type, config in self.hooks.items()
            },
            "performance": {
                "budget_no_op_ms": self.performance.budget_no_op_ms,
                "budget_validated_ms": self.performance.budget_validated_ms,
                "slow_hook_threshold_ms": self.performance.slow_hook_threshold_ms,
            },
        }
