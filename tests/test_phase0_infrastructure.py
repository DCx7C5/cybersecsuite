"""Tests for Phase 0 Backend Infrastructure components."""
import pytest
import asyncio
from datetime import datetime, timedelta

from ai_proxy.health import (
    detect_gpu,
    check_ollama_health,
    check_lmstudio_health,
    GPUProvider,
)
from ai_proxy.error_handler import (
    CyberSecError,
    ValidationError,
    AuthenticationError,
    TimeoutError as CSTimeoutError,
    ErrorCode,
    ErrorSeverity,
    retry_with_backoff,
    RetryConfig,
)
from ai_proxy.context_awareness import (
    WorkerContextAwareness,
    ArchitectureContext,
    ScopeContext,
    PatternContext,
    APIContext,
)


# ── GPU Detection Tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_detect_gpu_returns_valid_gpu_info():
    """Test GPU detection returns valid GPUInfo."""
    gpu_info = await detect_gpu()
    assert gpu_info is not None
    assert gpu_info.provider in [GPUProvider.NVIDIA, GPUProvider.AMD, GPUProvider.APPLE, GPUProvider.INTEL, GPUProvider.NONE]
    assert isinstance(gpu_info.available, bool)
    assert gpu_info.count >= 0
    assert gpu_info.memory_gb >= 0


@pytest.mark.asyncio
async def test_detect_gpu_detected_at_timestamp():
    """Test GPU detection sets detected_at timestamp."""
    gpu_info = await detect_gpu()
    assert gpu_info.detected_at > 0
    assert gpu_info.detected_at <= datetime.utcnow().timestamp() + 1


# ── Ollama Health Check Tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_ollama_health_timeout():
    """Test Ollama health check with timeout."""
    # Try an unreachable host
    health = await check_ollama_health(
        base_url="http://192.0.2.1:11434",
        timeout_seconds=1.0,
    )
    assert health.healthy is False
    assert health.base_url == "http://192.0.2.1:11434"
    assert health.error != ""


@pytest.mark.asyncio
async def test_check_ollama_health_returns_valid_structure():
    """Test Ollama health check returns valid structure."""
    health = await check_ollama_health()
    assert hasattr(health, "healthy")
    assert hasattr(health, "base_url")
    assert hasattr(health, "response_time_ms")
    assert hasattr(health, "models")
    assert hasattr(health, "gpu_info")
    assert health.response_time_ms >= 0


@pytest.mark.asyncio
async def test_ollama_health_to_dict():
    """Test OllamaHealth conversion to dict."""
    health = await check_ollama_health()
    health_dict = health.to_dict()
    assert "healthy" in health_dict
    assert "base_url" in health_dict
    assert "response_time_ms" in health_dict
    assert "models" in health_dict
    assert "gpu_info" in health_dict


# ── LM Studio Health Check Tests ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_lmstudio_health_returns_valid_structure():
    """Test LM Studio health check returns valid structure."""
    health = await check_lmstudio_health()
    assert "healthy" in health
    assert "base_url" in health
    assert "response_time_ms" in health
    assert "models" in health
    assert "error" in health


@pytest.mark.asyncio
async def test_check_lmstudio_health_timeout():
    """Test LM Studio health check with timeout."""
    health = await check_lmstudio_health(
        base_url="http://192.0.2.1:1234",
        timeout_seconds=1.0,
    )
    assert health["healthy"] is False
    assert health["error"] != ""


# ── Error Handling Tests ─────────────────────────────────────────────────────

def test_validation_error_structure():
    """Test ValidationError has correct structure."""
    error = ValidationError("Invalid input", details={"field": "name"})
    assert error.code == ErrorCode.VALIDATION_ERROR
    assert error.severity == ErrorSeverity.WARNING
    assert error.status_code == 422
    assert error.details["field"] == "name"


def test_authentication_error_structure():
    """Test AuthenticationError has correct structure."""
    error = AuthenticationError("Invalid token")
    assert error.code == ErrorCode.AUTHENTICATION_ERROR
    assert error.status_code == 401


def test_timeout_error_structure():
    """Test TimeoutError has correct structure."""
    error = CSTimeoutError("Query operation", 5.0)
    assert error.code == ErrorCode.TIMEOUT_ERROR
    assert error.status_code == 504
    assert error.details["timeout_seconds"] == 5.0


def test_cybersec_error_to_dict():
    """Test CyberSecError conversion to dict."""
    error = CyberSecError(
        "Test error",
        code=ErrorCode.INTERNAL_ERROR,
        severity=ErrorSeverity.CRITICAL,
    )
    error_dict = error.to_dict()
    assert "message" in error_dict
    assert "code" in error_dict
    assert "severity" in error_dict
    assert "status_code" in error_dict
    assert error_dict["code"] == ErrorCode.INTERNAL_ERROR.value


def test_cybersec_error_to_response():
    """Test CyberSecError conversion to response."""
    error = ValidationError("Invalid field")
    response = error.to_response()
    assert response.status_code == 422
    # Response should be a JSONResponse


# ── Retry Logic Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_retry_with_backoff_succeeds():
    """Test retry succeeds on first attempt."""
    async def success_func():
        return "success"

    result = await retry_with_backoff(success_func)
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_with_backoff_recovers_from_temporary_failure():
    """Test retry recovers from temporary failures."""
    attempt_count = 0

    async def failing_then_succeeds():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise ValueError("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=3, initial_delay_seconds=0.01, max_delay_seconds=0.1)
    result = await retry_with_backoff(failing_then_succeeds, config=config)
    assert result == "success"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_with_backoff_exhausts_retries():
    """Test retry exhausts all retries and raises."""
    async def always_fails():
        raise ValueError("Always fails")

    config = RetryConfig(max_retries=2, initial_delay_seconds=0.01)
    with pytest.raises(ValueError):
        await retry_with_backoff(always_fails, config=config)


# ── Context Awareness Tests ──────────────────────────────────────────────────

def test_architecture_context_initialization():
    """Test ArchitectureContext initialization."""
    ctx = ArchitectureContext()
    assert ctx.current_layer is None
    assert ctx.current_component is None
    assert ctx.accessed_layers == []
    assert ctx.accessed_components == []


def test_architecture_context_to_dict():
    """Test ArchitectureContext serialization."""
    ctx = ArchitectureContext()
    ctx.current_layer = "Layer 3"
    ctx.current_component = "ai_proxy"
    data = ctx.to_dict()
    assert data["current_layer"] == "Layer 3"
    assert data["current_component"] == "ai_proxy"


def test_architecture_context_from_dict():
    """Test ArchitectureContext deserialization."""
    data = {
        "current_layer": "Layer 3",
        "current_component": "ai_proxy",
        "current_module": "routing",
        "accessed_layers": ["Layer 1", "Layer 2"],
        "accessed_components": ["a2a", "ai_proxy"],
    }
    ctx = ArchitectureContext.from_dict(data)
    assert ctx.current_layer == "Layer 3"
    assert ctx.current_component == "ai_proxy"
    assert ctx.current_module == "routing"


def test_scope_context_initialization():
    """Test ScopeContext initialization."""
    ctx = ScopeContext()
    assert ctx.session_id is None
    assert ctx.project_id is None
    assert ctx.scope_level == "session"


def test_pattern_context_add_pattern():
    """Test PatternContext pattern tracking."""
    ctx = PatternContext()
    ctx.add_pattern("pattern_1")
    ctx.add_pattern("pattern_1")
    ctx.add_pattern("pattern_2")
    assert len(ctx.recent_patterns) == 2
    assert ctx.pattern_count["pattern_1"] == 2
    assert ctx.pattern_count["pattern_2"] == 1


def test_pattern_context_hot_patterns():
    """Test PatternContext identifies hot patterns."""
    ctx = PatternContext()
    for _ in range(5):
        ctx.add_pattern("hot_pattern")
    for _ in range(2):
        ctx.add_pattern("cold_pattern")
    
    hot = ctx.get_hot_patterns(1)
    assert hot[0] == "hot_pattern"


def test_api_context_record_endpoint_call():
    """Test APIContext endpoint call recording."""
    ctx = APIContext()
    ctx.record_endpoint_call("/api/test", 50.5)
    ctx.record_endpoint_call("/api/test", 45.2)
    
    assert len(ctx.recent_endpoints) == 1
    assert ctx.endpoint_count["/api/test"] == 2
    avg_latency = ctx.get_avg_latency("/api/test")
    assert 45 < avg_latency < 51


def test_api_context_error_tracking():
    """Test APIContext error tracking."""
    ctx = APIContext()
    ctx.record_endpoint_call("/api/test", 50.0, error="Connection timeout")
    ctx.record_endpoint_call("/api/test", 45.0, error="Connection timeout")
    
    assert len(ctx.recent_errors) == 2
    assert ctx.recent_errors[0]["error"] == "Connection timeout"


def test_worker_context_awareness_initialization():
    """Test WorkerContextAwareness initialization."""
    awareness = WorkerContextAwareness("worker_1", 123)
    assert awareness.worker_id == "worker_1"
    assert awareness.session_id == 123
    assert isinstance(awareness.architecture, ArchitectureContext)
    assert isinstance(awareness.scope, ScopeContext)
    assert isinstance(awareness.pattern, PatternContext)
    assert isinstance(awareness.api, APIContext)


def test_worker_context_awareness_get_summary():
    """Test WorkerContextAwareness summary generation."""
    awareness = WorkerContextAwareness("worker_1", 123)
    awareness.architecture.current_layer = "Layer 3"
    awareness.scope.scope_level = "session"
    
    summary = awareness.get_context_summary()
    assert summary["worker_id"] == "worker_1"
    assert summary["session_id"] == 123
    assert summary["architecture"]["current_layer"] == "Layer 3"
    assert summary["scope"]["scope_level"] == "session"


# ── Integration Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check_with_gpu_detection():
    """Integration test: health check includes GPU detection."""
    health = await check_ollama_health()
    assert health.gpu_info is not None
    assert health.gpu_info.provider in [e.value for e in GPUProvider]


@pytest.mark.asyncio
async def test_error_and_retry_integration():
    """Integration test: error handling with retry logic."""
    attempt_count = 0

    async def api_call_with_retry():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise ValidationError("Invalid request")
        return {"status": "ok"}

    config = RetryConfig(max_retries=3, initial_delay_seconds=0.01)
    result = await retry_with_backoff(api_call_with_retry, config=config)
    assert result["status"] == "ok"
    assert attempt_count == 2
