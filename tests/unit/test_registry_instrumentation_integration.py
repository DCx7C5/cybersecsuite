"""Integration tests for HookRegistry with instrumentation.

Tests verify:
- Registry integration with HookInstrument
- Zero behavioral changes when instrumentation enabled
- Metrics collected during registry execution
- Performance validation through registry
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks.core import ErrorStrategy, HookContext
from hooks.instrumentation import HookInstrument
from hooks.registry import HookRegistry, reset_registry


class TestRegistryWithInstrumentation:
    """Test HookRegistry integration with instrumentation."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry after each test."""
        yield
        reset_registry()
    
    def test_registry_initialization_with_instrumentation(self):
        """Registry should accept instrumentation parameter."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        
        assert registry.get_instrumentation() is instrument
    
    def test_registry_initialization_without_instrumentation(self):
        """Registry should work without instrumentation."""
        registry = HookRegistry()
        assert registry.get_instrumentation() is None
    
    @pytest.mark.asyncio
    async def test_instrumented_registry_integration(self):
        """Instrumented registry should collect metrics."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        # Execute a hook through registry
        with patch("hooks.sdk_hooks.build_python_hooks") as mock_build:
            async def test_hook(event):
                return {"result": "ok"}
            
            from claude_agent_sdk import HookMatcher
            mock_build.return_value = {
                "PreToolUse": [HookMatcher(matcher=".*", hooks=[test_hook])]
            }
            
            registry2 = HookRegistry(instrumentation=instrument)
            
            # Execute hook
            output = await registry2.execute("PreToolUse", {"tool": "Bash"}, context)
            
            # Verify metrics collected
            assert len(instrument.metrics) > 0
            assert instrument.metrics[0].hook_name == "test_hook"
            assert instrument.metrics[0].event_type == "PreToolUse"
            assert instrument.metrics[0].success is True
    
    @pytest.mark.asyncio
    async def test_registry_without_instrumentation_unchanged_behavior(self):
        """Registry without instrumentation should work as before."""
        registry = HookRegistry()  # No instrumentation
        
        context = HookContext(
            correlation_id="test",
            session_id="test",
            timestamp=time.time(),
        )
        
        # Should execute without errors
        output = await registry.execute("PreToolUse", {"tool": "Bash"}, context)
        assert isinstance(output, dict)
    
    @pytest.mark.asyncio
    async def test_instrumentation_error_handling_integration(self):
        """Registry should instrument failed hooks correctly."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        
        context = HookContext(
            correlation_id="test",
            session_id="test",
            timestamp=time.time(),
        )
        
        with patch("hooks.sdk_hooks.build_python_hooks") as mock_build:
            async def failing_hook(event):
                raise ValueError("Test error")
            
            from claude_agent_sdk import HookMatcher
            mock_build.return_value = {
                "PostToolUse": [HookMatcher(matcher=".*", hooks=[failing_hook])]
            }
            
            registry2 = HookRegistry(
                error_strategy=ErrorStrategy.PRESERVE_EXISTING,
                instrumentation=instrument,
            )
            
            # Should not raise despite hook failure
            output = await registry2.execute("PostToolUse", {"tool": "Bash"}, context)
            
            # Metrics should show failure
            assert len(instrument.metrics) > 0
            assert instrument.metrics[0].success is False
            assert "Test error" in instrument.metrics[0].error_message


class TestRegistryInstrumentationPerformance:
    """Test performance characteristics of instrumented registry."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()
    
    @pytest.mark.asyncio
    async def test_no_op_hook_performance_budget(self):
        """No-op hooks should execute in <2ms."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        
        context = HookContext(
            correlation_id="perf-test",
            session_id="test",
            timestamp=time.time(),
        )
        
        with patch("hooks.sdk_hooks.build_python_hooks") as mock_build:
            async def no_op_hook(event):
                return {}
            
            from claude_agent_sdk import HookMatcher
            mock_build.return_value = {
                "PreToolUse": [HookMatcher(matcher=".*", hooks=[no_op_hook])]
            }
            
            registry2 = HookRegistry(instrumentation=instrument)
            
            # Execute multiple times
            for _ in range(5):
                await registry2.execute("PreToolUse", {"tool": "Bash"}, context)
            
            # Check performance
            report = instrument.generate_report()
            assert report["summary"]["total_calls"] == 5
            
            # Average should be < 2ms
            no_op_avg = report["per_hook"]["no_op_hook"]["avg_ms"]
            assert no_op_avg < 2.0


class TestInstrumentationMetricsAccuracy:
    """Test that instrumentation metrics are accurate."""
    
    def test_metrics_preserved_across_calls(self):
        """Metrics should accumulate across multiple registry calls."""
        instrument = HookInstrument()
        
        # Simulate multiple calls
        instrument.metrics.append(
            __import__("hooks.instrumentation", fromlist=["HookMetrics"]).HookMetrics(
                "hook1", "PreToolUse", 5.0, True
            )
        )
        instrument.metrics.append(
            __import__("hooks.instrumentation", fromlist=["HookMetrics"]).HookMetrics(
                "hook2", "PostToolUse", 8.0, True
            )
        )
        
        report = instrument.generate_report()
        assert report["summary"]["total_calls"] == 2
