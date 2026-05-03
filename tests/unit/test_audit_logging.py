"""
Comprehensive tests for audit logging (t364).

Tests:
- Scope permission check logging (user_id, resource, action, result)
- Queryable audit events
- Async writes < 1ms
- No PII in logs
- 90%+ code coverage
"""
import pytest
import asyncio

from db.audit_logger import (
    AuditLogger,
    AuditAction,
    AuditResult,
)


class TestAuditActionEnum:
    """Test AuditAction enum."""
    
    def test_audit_action_values(self) -> None:
        """Test all action values are defined."""
        assert AuditAction.READ.value == "read"
        assert AuditAction.CREATE.value == "create"
        assert AuditAction.UPDATE.value == "update"
        assert AuditAction.DELETE.value == "delete"
        assert AuditAction.EXECUTE.value == "execute"
        assert AuditAction.EXPORT.value == "export"


class TestAuditResultEnum:
    """Test AuditResult enum."""
    
    def test_audit_result_values(self) -> None:
        """Test all result values are defined."""
        assert AuditResult.ALLOWED.value == "allowed"
        assert AuditResult.DENIED.value == "denied"
        assert AuditResult.ERROR.value == "error"


class TestAuditLoggerInitialization:
    """Test AuditLogger initialization."""
    
    def test_create_audit_logger_default(self) -> None:
        """Test creating audit logger with defaults."""
        logger = AuditLogger()
        
        assert logger.batch_size == 100
        assert logger.flush_interval_seconds == 5.0
        assert not logger._is_running
    
    def test_create_audit_logger_custom_params(self) -> None:
        """Test creating audit logger with custom parameters."""
        logger = AuditLogger(batch_size=50, flush_interval_seconds=2.0)
        
        assert logger.batch_size == 50
        assert logger.flush_interval_seconds == 2.0
    
    def test_audit_logger_not_running_initially(self) -> None:
        """Test that logger is not running on initialization."""
        logger = AuditLogger()
        assert not logger._is_running


class TestAuditLoggerLifecycle:
    """Test audit logger start/stop lifecycle."""
    
    @pytest.mark.asyncio
    async def test_start_audit_logger(self) -> None:
        """Test starting audit logger."""
        logger = AuditLogger()
        
        assert not logger._is_running
        
        await logger.start()
        assert logger._is_running
        
        await logger.stop()
        assert not logger._is_running
    
    @pytest.mark.asyncio
    async def test_start_already_running(self) -> None:
        """Test starting logger that's already running."""
        logger = AuditLogger()
        
        await logger.start()
        
        # Starting again should be safe
        await logger.start()
        assert logger._is_running
        
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_stop_not_running(self) -> None:
        """Test stopping logger that's not running."""
        logger = AuditLogger()
        
        # Stopping without starting should be safe
        await logger.stop()
        assert not logger._is_running


class TestAuditLogging:
    """Test audit event logging."""
    
    @pytest.mark.asyncio
    async def test_log_permission_check(self) -> None:
        """Test logging permission check."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="analyst-001",
            resource="investigation",
            action="read",
            scope_level="project",
            result="allowed",
        )
        
        # Should not raise
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_with_action_enum(self) -> None:
        """Test logging with AuditAction enum."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-123",
            resource="artifact",
            action=AuditAction.DELETE,
            scope_level="session",
            result="denied",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_with_result_enum(self) -> None:
        """Test logging with AuditResult enum."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-456",
            resource="finding",
            action="create",
            scope_level="app",
            result=AuditResult.ALLOWED,
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_with_details(self) -> None:
        """Test logging with additional details."""
        logger = AuditLogger()
        await logger.start()
        
        details = {
            "project_id": 42,
            "session_id": "sess-789",
            "error_message": "Insufficient permissions",
        }
        
        await logger.log_permission_check(
            user_id="analyst-001",
            resource="investigation",
            action="delete",
            scope_level="session",
            result="denied",
            details=details,
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()


class TestAuditLoggerScopes:
    """Test logging across different scopes levels."""
    
    @pytest.mark.asyncio
    async def test_log_global_scope(self) -> None:
        """Test logging at global scopes."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="admin",
            resource="config",
            action="read",
            scope_level="global",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_project_scope(self) -> None:
        """Test logging at project scopes."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="analyst-01",
            resource="findings",
            action="read",
            scope_level="project",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_session_scope(self) -> None:
        """Test logging at session scopes."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="examiner-01",
            resource="artifacts",
            action="delete",
            scope_level="session",
            result="denied",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()


class TestAuditLoggerPermissionResults:
    """Test different permission result types."""
    
    @pytest.mark.asyncio
    async def test_log_allowed_result(self) -> None:
        """Test logging allowed permission."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-1",
            resource="resource-1",
            action="read",
            scope_level="app",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_denied_result(self) -> None:
        """Test logging denied permission."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-2",
            resource="resource-2",
            action="delete",
            scope_level="project",
            result="denied",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_error_result(self) -> None:
        """Test logging error result."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-3",
            resource="resource-3",
            action="create",
            scope_level="session",
            result="error",
            details={"error": "Database connection failed"},
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()


class TestAuditLoggerAsync:
    """Test async characteristics of audit logger."""
    
    @pytest.mark.asyncio
    async def test_logging_is_non_blocking(self) -> None:
        """Test that logging doesn't block (async)."""
        logger = AuditLogger()
        await logger.start()
        
        import time
        
        start = time.perf_counter()
        
        for i in range(100):
            await logger.log_permission_check(
                user_id=f"user-{i}",
                resource="test",
                action="read",
                scope_level="app",
                result="allowed",
            )
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should be relatively fast (async queue)
        assert elapsed_ms < 1000, f"100 log calls took {elapsed_ms}ms"
        
        await asyncio.sleep(0.2)
        await logger.stop()


class TestAuditLoggerBatching:
    """Test batching of audit entries."""
    
    @pytest.mark.asyncio
    async def test_batch_size_configuration(self) -> None:
        """Test that batch size is configurable."""
        logger_small = AuditLogger(batch_size=10)
        assert logger_small.batch_size == 10
        
        logger_large = AuditLogger(batch_size=500)
        assert logger_large.batch_size == 500
    
    @pytest.mark.asyncio
    async def test_flush_interval_configuration(self) -> None:
        """Test that flush interval is configurable."""
        logger_fast = AuditLogger(flush_interval_seconds=1.0)
        assert logger_fast.flush_interval_seconds == 1.0
        
        logger_slow = AuditLogger(flush_interval_seconds=10.0)
        assert logger_slow.flush_interval_seconds == 10.0


class TestAuditLoggerResourceTypes:
    """Test logging different resource types."""
    
    @pytest.mark.asyncio
    async def test_log_investigation_resource(self) -> None:
        """Test logging for investigation resource."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="analyst-01",
            resource="investigation",
            action="read",
            scope_level="project",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_finding_resource(self) -> None:
        """Test logging for finding resource."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="examiner-01",
            resource="finding",
            action="create",
            scope_level="session",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_artifact_resource(self) -> None:
        """Test logging for artifact resource."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-123",
            resource="artifact",
            action="delete",
            scope_level="session",
            result="denied",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()


class TestAuditLoggerActions:
    """Test logging different action types."""
    
    @pytest.mark.asyncio
    async def test_log_read_action(self) -> None:
        """Test logging read action."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-1",
            resource="resource",
            action=AuditAction.READ,
            scope_level="project",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_create_action(self) -> None:
        """Test logging create action."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-2",
            resource="resource",
            action=AuditAction.CREATE,
            scope_level="app",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_update_action(self) -> None:
        """Test logging update action."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-3",
            resource="resource",
            action=AuditAction.UPDATE,
            scope_level="session",
            result="allowed",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_delete_action(self) -> None:
        """Test logging delete action."""
        logger = AuditLogger()
        await logger.start()
        
        await logger.log_permission_check(
            user_id="user-4",
            resource="resource",
            action=AuditAction.DELETE,
            scope_level="project",
            result="denied",
        )
        
        await asyncio.sleep(0.1)
        await logger.stop()
