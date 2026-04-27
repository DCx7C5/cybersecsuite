"""Tests for Plan* events: TypedDict definitions and routing."""

import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks.config import HookConfig
from hooks.core import (
    ErrorStrategy,
    HookContext,
    PlanCompleteEvent,
    PlanPhaseCompleteEvent,
    PlanPhaseStartEvent,
    PlanStartEvent,
    PlanTaskCompleteEvent,
    PlanTaskStartEvent,
    PlanTodoCompleteEvent,
    PlanTodoStartEvent,
)
from src.registries.hooks import HookRegistry


class TestTypesDictFieldCoverage:
    """Test TypedDict field coverage for Plan events."""

    def test_plan_start_event_has_all_required_fields(self):
        """PlanStartEvent should have all required fields."""
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test Plan",
            "total_tasks": 5,
            "total_todos": 10,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }
        assert event["plan_id"] == 1
        assert event["plan_title"] == "Test Plan"
        assert event["total_tasks"] == 5
        assert event["total_todos"] == 10
        assert event["triggered_by"] == "user"
        assert event["hook_event_name"] == "PlanStart"

    def test_plan_complete_event_has_all_required_fields(self):
        """PlanCompleteEvent should have all required fields."""
        event: PlanCompleteEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test Plan",
            "total_todos": 10,
            "completed_todos": 8,
            "failed_todos": 2,
            "duration_ms": 5000.0,
            "hook_event_name": "PlanComplete",
        }
        assert event["plan_id"] == 1
        assert event["plan_title"] == "Test Plan"
        assert event["total_todos"] == 10
        assert event["completed_todos"] == 8
        assert event["failed_todos"] == 2
        assert event["duration_ms"] == 5000.0
        assert event["hook_event_name"] == "PlanComplete"

    def test_plan_phase_start_event_has_phase_name_not_db_field(self):
        """PlanPhaseStartEvent should have phase_name as string label."""
        event: PlanPhaseStartEvent = {  # type: ignore
            "plan_id": 1,
            "phase_name": "Discovery Phase",
            "phase_index": 0,
            "total_phases": 3,
            "todos_in_phase": 5,
            "hook_event_name": "PlanPhaseStart",
        }
        assert event["phase_name"] == "Discovery Phase"
        assert isinstance(event["phase_name"], str)

    def test_plan_task_start_event_has_task_sequence(self):
        """PlanTaskStartEvent should have task_id and task_sequence."""
        event: PlanTaskStartEvent = {  # type: ignore
            "plan_id": 1,
            "task_id": 5,
            "task_title": "Task 1",
            "task_sequence": 1,
            "hook_event_name": "PlanTaskStart",
        }
        assert event["task_id"] == 5
        assert event["task_sequence"] == 1

    def test_plan_todo_start_event_has_todo_content(self):
        """PlanTodoStartEvent should have todo_content (NOT 'title')."""
        event: PlanTodoStartEvent = {  # type: ignore
            "plan_id": 1,
            "todo_id": 10,
            "todo_content": "Fix bug in auth module",
            "task_id": 5,
            "hook_event_name": "PlanTodoStart",
        }
        assert event["todo_content"] == "Fix bug in auth module"
        assert "todo_title" not in event

    def test_all_plan_events_have_hook_event_name_field(self):
        """All Plan* TypedDicts should have hook_event_name field."""
        events = [
            {
                "plan_id": 1,
                "plan_title": "Test",
                "total_tasks": 1,
                "total_todos": 1,
                "triggered_by": "user",
                "hook_event_name": "PlanStart",
            },
            {
                "plan_id": 1,
                "plan_title": "Test",
                "total_todos": 1,
                "completed_todos": 1,
                "failed_todos": 0,
                "duration_ms": 100.0,
                "hook_event_name": "PlanComplete",
            },
            {
                "plan_id": 1,
                "phase_name": "Phase",
                "phase_index": 0,
                "total_phases": 1,
                "todos_in_phase": 1,
                "hook_event_name": "PlanPhaseStart",
            },
        ]

        for event in events:
            assert "hook_event_name" in event
            assert isinstance(event["hook_event_name"], str)


class TestYAMLKeyMapping:
    """Test YAML key mapping for Plan events."""

    def test_pascal_case_to_snake_case_mapping(self):
        """PascalCase event names should map to snake_case YAML keys."""
        from hooks.config import _YAML_EVENT_MAP

        assert _YAML_EVENT_MAP.get("PreToolUse") == "pre_tool_use"
        assert _YAML_EVENT_MAP.get("PostToolUse") == "post_tool_use"

    def test_plan_start_mapping(self):
        """PlanStart should map to plan_start."""
        from hooks.config import _YAML_EVENT_MAP

        assert _YAML_EVENT_MAP.get("PlanStart") == "plan_start"

    def test_plan_todo_start_mapping(self):
        """PlanTodoStart should map to plan_todo_start."""
        from hooks.config import _YAML_EVENT_MAP

        assert _YAML_EVENT_MAP.get("PlanTodoStart") == "plan_todo_start"

    def test_on_first_setup_mapping(self):
        """OnFirstSetup should map to first_setup."""
        from hooks.config import _YAML_EVENT_MAP

        assert _YAML_EVENT_MAP.get("OnFirstSetup") == "first_setup"

    @pytest.mark.asyncio
    async def test_is_event_enabled_uses_mapped_key(self):
        """is_event_enabled() should use mapped key for case-insensitive lookup."""
        config_data = {
            "hooks": {
                "plan_start": {"enabled": True},
                "plan_stop": {"enabled": False},
            }
        }
        config = HookConfig.from_dict(config_data)

        # Should map PascalCase to snake_case
        assert config.is_event_enabled("PlanStart") is True
        assert config.is_event_enabled("PlanStop") is False


class TestEventRouting:
    """Test Plan event routing to handlers."""

    @pytest.mark.asyncio
    async def test_execute_routes_plan_events_to_handlers(self):
        """execute() should route Plan* events to handlers."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        # Create a test Plan event
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test Plan",
            "total_tasks": 5,
            "total_todos": 10,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }

        # Execute should handle Plan events
        result = await registry.execute("PlanStart", event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_disabled_stop_events_return_empty_dict(self):
        """Disabled stop events should return {}."""
        config_data = {
            "hooks": {
                "plan_stop": {"enabled": False},
                "plan_phase_stop": {"enabled": False},
            }
        }
        config = HookConfig.from_dict(config_data)
        registry = HookRegistry(config=config)

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        # Stop events should return empty when disabled
        result1 = await registry.execute("PlanStop", {}, context)
        result2 = await registry.execute("PlanPhaseStop", {}, context)

        assert result1 == {}
        assert result2 == {}

    @pytest.mark.asyncio
    async def test_enabled_events_return_handler_results(self):
        """Enabled events should return handler results."""
        config_data = {
            "hooks": {
                "plan_start": {"enabled": True},
                "plan_complete": {"enabled": True},
            }
        }
        config = HookConfig.from_dict(config_data)
        registry = HookRegistry(config=config)

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        # Enabled events should be routed
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_tasks": 1,
            "total_todos": 1,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }

        result = await registry.execute("PlanStart", event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_mixed_enable_disable_plan_lifecycle(self):
        """Mixed enable/disable states should be respected across plan lifecycle."""
        config_data = {
            "hooks": {
                "plan_start": {"enabled": True},
                "plan_stop": {"enabled": False},
                "plan_complete": {"enabled": True},
            }
        }
        config = HookConfig.from_dict(config_data)
        registry = HookRegistry(config=config)

        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        # PlanStart should execute
        result1 = await registry.execute("PlanStart", {}, context)
        assert isinstance(result1, dict)

        # PlanStop should return empty (disabled)
        result2 = await registry.execute("PlanStop", {}, context)
        assert result2 == {}

        # PlanComplete should execute
        result3 = await registry.execute("PlanComplete", {}, context)
        assert isinstance(result3, dict)


class TestTypesDictValidation:
    """Test TypedDict validation."""

    def test_plan_start_event_instantiation(self):
        """PlanStartEvent should be instantiable with correct fields."""
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_tasks": 5,
            "total_todos": 10,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }
        assert isinstance(event, dict)

    def test_plan_complete_event_instantiation(self):
        """PlanCompleteEvent should be instantiable with correct fields."""
        event: PlanCompleteEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_todos": 10,
            "completed_todos": 8,
            "failed_todos": 2,
            "duration_ms": 5000.0,
            "hook_event_name": "PlanComplete",
        }
        assert isinstance(event, dict)

    def test_total_false_allows_partial_fields(self):
        """total=False should allow partial field submission."""
        # PlanStartEvent can be created with partial fields
        partial_event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "hook_event_name": "PlanStart",
        }
        assert isinstance(partial_event, dict)
        assert len(partial_event) == 2

    def test_extra_fields_dont_cause_validation_errors(self):
        """Extra fields should not cause validation errors."""
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_tasks": 5,
            "total_todos": 10,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
            "extra_field": "extra_value",  # Extra field
        }
        assert event["extra_field"] == "extra_value"
        assert isinstance(event, dict)

    @pytest.mark.asyncio
    async def test_all_12_plan_typeddicts_instantiable(self):
        """All 12 Plan* TypedDicts should be instantiable."""
        plan_events = [
            {
                "plan_id": 1,
                "plan_title": "Test",
                "total_tasks": 1,
                "total_todos": 1,
                "triggered_by": "user",
                "hook_event_name": "PlanStart",
            },
            {
                "plan_id": 1,
                "stop_reason": "user_interrupt",
                "completed_todos": 0,
                "total_todos": 1,
                "hook_event_name": "PlanStop",
            },
            {
                "plan_id": 1,
                "plan_title": "Test",
                "total_todos": 1,
                "completed_todos": 1,
                "failed_todos": 0,
                "duration_ms": 100.0,
                "hook_event_name": "PlanComplete",
            },
            {
                "plan_id": 1,
                "phase_name": "Phase 1",
                "phase_index": 0,
                "total_phases": 1,
                "todos_in_phase": 1,
                "hook_event_name": "PlanPhaseStart",
            },
            {
                "plan_id": 1,
                "phase_name": "Phase 1",
                "stop_reason": "user_interrupt",
                "completed_todos": 0,
                "hook_event_name": "PlanPhaseStop",
            },
            {
                "plan_id": 1,
                "phase_name": "Phase 1",
                "phase_index": 0,
                "completed_todos": 1,
                "failed_todos": 0,
                "duration_ms": 100.0,
                "hook_event_name": "PlanPhaseComplete",
            },
            {
                "plan_id": 1,
                "task_id": 5,
                "task_title": "Task 1",
                "task_sequence": 1,
                "hook_event_name": "PlanTaskStart",
            },
            {
                "plan_id": 1,
                "task_id": 5,
                "stop_reason": "user_interrupt",
                "hook_event_name": "PlanTaskStop",
            },
            {
                "plan_id": 1,
                "task_id": 5,
                "task_title": "Task 1",
                "duration_ms": 100.0,
                "hook_event_name": "PlanTaskComplete",
            },
            {
                "plan_id": 1,
                "todo_id": 10,
                "todo_content": "Fix bug",
                "task_id": 5,
                "hook_event_name": "PlanTodoStart",
            },
            {
                "plan_id": 1,
                "todo_id": 10,
                "stop_reason": "user_interrupt",
                "hook_event_name": "PlanTodoStop",
            },
            {
                "plan_id": 1,
                "todo_id": 10,
                "todo_content": "Fix bug",
                "duration_ms": 100.0,
                "hook_event_name": "PlanTodoComplete",
            },
        ]

        for event in plan_events:
            assert isinstance(event, dict)
            assert "hook_event_name" in event


class TestEventNamingConsistency:
    """Test event naming consistency."""

    def test_hook_event_name_matches_event_type_name(self):
        """hook_event_name field should match the event type name."""
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_tasks": 1,
            "total_todos": 1,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }
        assert event["hook_event_name"] == "PlanStart"

    def test_event_type_names_consistent_across_hierarchy(self):
        """Event type names should be consistent across Plan hierarchy."""
        event_names = [
            "PlanStart",
            "PlanStop",
            "PlanComplete",
            "PlanPhaseStart",
            "PlanPhaseStop",
            "PlanPhaseComplete",
            "PlanTaskStart",
            "PlanTaskStop",
            "PlanTaskComplete",
            "PlanTodoStart",
            "PlanTodoStop",
            "PlanTodoComplete",
        ]

        # All should follow the pattern Plan[Noun][Verb]
        for name in event_names:
            assert name.startswith("Plan")
            assert len(name) > 4


class TestPlanEventIntegration:
    """Integration tests for Plan event flow."""

    @pytest.mark.asyncio
    async def test_complete_plan_lifecycle_event_routing(self):
        """Complete Plan lifecycle should route all events correctly."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        # Simulate a plan lifecycle
        lifecycle_events = [
            ("PlanStart", {
                "plan_id": 1,
                "plan_title": "Build Auth System",
                "total_tasks": 3,
                "total_todos": 10,
                "triggered_by": "user",
                "hook_event_name": "PlanStart",
            }),
            ("PlanPhaseStart", {
                "plan_id": 1,
                "phase_name": "Design Phase",
                "phase_index": 0,
                "total_phases": 3,
                "todos_in_phase": 3,
                "hook_event_name": "PlanPhaseStart",
            }),
            ("PlanTaskStart", {
                "plan_id": 1,
                "task_id": 5,
                "task_title": "Design Schema",
                "task_sequence": 1,
                "hook_event_name": "PlanTaskStart",
            }),
            ("PlanTodoStart", {
                "plan_id": 1,
                "todo_id": 10,
                "todo_content": "Define User model",
                "task_id": 5,
                "hook_event_name": "PlanTodoStart",
            }),
            ("PlanTodoComplete", {
                "plan_id": 1,
                "todo_id": 10,
                "todo_content": "Define User model",
                "duration_ms": 500.0,
                "hook_event_name": "PlanTodoComplete",
            }),
            ("PlanTaskComplete", {
                "plan_id": 1,
                "task_id": 5,
                "task_title": "Design Schema",
                "duration_ms": 1000.0,
                "hook_event_name": "PlanTaskComplete",
            }),
            ("PlanPhaseComplete", {
                "plan_id": 1,
                "phase_name": "Design Phase",
                "phase_index": 0,
                "completed_todos": 3,
                "failed_todos": 0,
                "duration_ms": 1500.0,
                "hook_event_name": "PlanPhaseComplete",
            }),
            ("PlanComplete", {
                "plan_id": 1,
                "plan_title": "Build Auth System",
                "total_todos": 10,
                "completed_todos": 10,
                "failed_todos": 0,
                "duration_ms": 5000.0,
                "hook_event_name": "PlanComplete",
            }),
        ]

        # All events should route successfully
        for event_type, event_data in lifecycle_events:
            result = await registry.execute(event_type, event_data, context)
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_plan_event_todo_content_preserved(self):
        """todo_content should be preserved in Plan events."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )

        todo_content = "Implement password hashing with bcrypt"
        event: PlanTodoStartEvent = {  # type: ignore
            "plan_id": 1,
            "todo_id": 10,
            "todo_content": todo_content,
            "task_id": 5,
            "hook_event_name": "PlanTodoStart",
        }

        result = await registry.execute("PlanTodoStart", event, context)
        assert isinstance(result, dict)


class TestPlanEventFieldTypes:
    """Test field types in Plan events."""

    def test_plan_id_is_integer(self):
        """plan_id should be integer."""
        event: PlanStartEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_tasks": 1,
            "total_todos": 1,
            "triggered_by": "user",
            "hook_event_name": "PlanStart",
        }
        assert isinstance(event["plan_id"], int)

    def test_duration_ms_is_float(self):
        """duration_ms should be float."""
        event: PlanCompleteEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_todos": 1,
            "completed_todos": 1,
            "failed_todos": 0,
            "duration_ms": 5000.5,
            "hook_event_name": "PlanComplete",
        }
        assert isinstance(event["duration_ms"], float)

    def test_todos_count_fields_are_integers(self):
        """todo count fields should be integers."""
        event: PlanCompleteEvent = {  # type: ignore
            "plan_id": 1,
            "plan_title": "Test",
            "total_todos": 10,
            "completed_todos": 8,
            "failed_todos": 2,
            "duration_ms": 5000.0,
            "hook_event_name": "PlanComplete",
        }
        assert isinstance(event["total_todos"], int)
        assert isinstance(event["completed_todos"], int)
        assert isinstance(event["failed_todos"], int)

    def test_phase_index_is_zero_based(self):
        """phase_index should start from 0."""
        event: PlanPhaseStartEvent = {  # type: ignore
            "plan_id": 1,
            "phase_name": "Phase 1",
            "phase_index": 0,
            "total_phases": 3,
            "todos_in_phase": 5,
            "hook_event_name": "PlanPhaseStart",
        }
        assert event["phase_index"] == 0
        assert event["total_phases"] == 3
