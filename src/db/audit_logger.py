"""
Async audit logger for scope permission checks.

Logs all scope-related permission checks to audit_log table:
- User ID, resource, action (read/write/delete), scope_level, result, timestamp
- Queryable by user, resource, action, date range
- No PII logged (IDs only, no usernames)
- Async writes with minimal latency (< 1ms)
"""


import logging
import asyncio
from datetime import datetime
from typing import Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Audit log action types."""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    EXPORT = "export"


class AuditResult(str, Enum):
    """Audit log result types."""
    ALLOWED = "allowed"
    DENIED = "denied"
    ERROR = "error"


class AuditLogger:
    """Async audit logger for scope permission checks.

    Implements:
    - Non-blocking async writes (< 1ms per entry)
    - Batch inserts for efficiency
    - No PII (IDs only, no usernames)
    - Queryable filtering (user_id, resource, action, date range)
    """

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval_seconds: float = 5.0,
    ) -> None:
        """Initialize audit logger.

        Args:
            batch_size: Number of entries to batch before flush
            flush_interval_seconds: Max time between flushes (background task)
        """
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._background_task: Optional[asyncio.Task[None]] = None
        self._is_running = False

    async def start(self) -> None:
        """Start background flush task."""
        if self._is_running:
            logger.warning("AuditLogger already running")
            return
        self._is_running = True
        self._background_task = asyncio.create_task(self._flush_loop())
        logger.info("AuditLogger started")

    async def stop(self) -> None:
        """Stop background flush task and flush remaining entries."""
        if not self._is_running:
            logger.warning("AuditLogger not running")
            return
        self._is_running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        # Final flush of remaining entries
        await self._flush()
        logger.info("AuditLogger stopped")

    async def log_permission_check(
        self,
        user_id: str,
        resource: str,
        action: str | AuditAction,
        scope_level: str,
        result: str | AuditResult,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a permission check (non-blocking).

        Args:
            user_id: User ID (no PII)
            resource: Resource type (Finding, IOC, etc.)
            action: Action attempted (read, write, delete, etc.)
            scope_level: Scope at which check occurred
            result: Result (allowed, denied, error)
            details: Optional details (project_id, session_id, error_message, etc.)
        """
        if isinstance(action, AuditAction):
            action = action.value
        if isinstance(result, AuditResult):
            result = result.value

        entry = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "scope_level": scope_level,
            "result": result,
            "timestamp": datetime.utcnow(),
            "details": details or {},
        }

        # Queue asynchronously (never blocks)
        try:
            self._queue.put_nowait(entry)
        except asyncio.QueueFull:
            logger.error("Audit queue full, dropping entry")

    async def log_scope_access(
        self,
        user_id: str,
        resource_id: str | int,
        resource_type: str,
        action: str | AuditAction,
        scope_level: str,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Log a resource access attempt.

        Args:
            user_id: User attempting access
            resource_id: Resource being accessed
            resource_type: Type of resource
            action: Action attempted
            scope_level: Scope context
            success: Whether access was granted
            error_message: Error message if access denied
        """
        result = AuditResult.ALLOWED if success else AuditResult.DENIED
        details = {
            "resource_id": str(resource_id),
            "resource_type": resource_type,
        }
        if error_message:
            details["error_message"] = error_message

        await self.log_permission_check(
            user_id=user_id,
            resource=resource_type,
            action=action,
            scope_level=scope_level,
            result=result,
            details=details,
        )

    async def _flush(self) -> None:
        """Flush all queued entries to database."""
        entries: list[dict[str, Any]] = []

        # Collect all queued entries without blocking
        while not self._queue.empty() and len(entries) < self.batch_size:
            try:
                entry = self._queue.get_nowait()
                entries.append(entry)
            except asyncio.QueueEmpty:
                break

        if not entries:
            return

        try:
            # Import here to avoid circular dependencies
            from db.models.core import AuditLog

            # Create audit log entries
            audit_logs = [
                AuditLog(
                    user_id=entry["user_id"],
                    resource=entry["resource"],
                    action=entry["action"],
                    scope_level=entry["scope_level"],
                    result=entry["result"],
                    details=entry["details"],
                    timestamp=entry["timestamp"],
                )
                for entry in entries
            ]

            # Bulk insert (async)
            await AuditLog.bulk_create(audit_logs)
            logger.debug(f"Flushed {len(entries)} audit log entries")
        except Exception as exc:
            logger.error(f"Error flushing audit logs: {exc}")
            # Re-queue entries on failure
            for entry in entries:
                try:
                    self._queue.put_nowait(entry)
                except asyncio.QueueFull:
                    logger.error("Cannot re-queue failed entries, queue full")
                    break

    async def _flush_loop(self) -> None:
        """Background task to periodically flush entries."""
        while self._is_running:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                if self._is_running:
                    await self._flush()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Error in flush loop: {exc}")

    async def query_by_user(
        self,
        user_id: str,
        days: int = 7,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs by user ID (last N days).

        Args:
            user_id: User to query
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of audit log entries
        """
        try:
            from db.models.core import AuditLog
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            logs = await AuditLog.filter(
                user_id=user_id,
                timestamp__gte=cutoff_date,
            ).limit(limit).order_by("-timestamp")

            return [
                {
                    "user_id": log.user_id,
                    "resource": log.resource,
                    "action": log.action,
                    "scope_level": log.scope_level,
                    "result": log.result,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details,
                }
                for log in logs
            ]
        except Exception as exc:
            logger.error(f"Error querying audit logs by user: {exc}")
            return []

    async def query_by_resource(
        self,
        resource_type: str,
        days: int = 7,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs by resource type.

        Args:
            resource_type: Resource type to query
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of audit log entries
        """
        try:
            from db.models.core import AuditLog
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            logs = await AuditLog.filter(
                resource=resource_type,
                timestamp__gte=cutoff_date,
            ).limit(limit).order_by("-timestamp")

            return [
                {
                    "user_id": log.user_id,
                    "resource": log.resource,
                    "action": log.action,
                    "scope_level": log.scope_level,
                    "result": log.result,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details,
                }
                for log in logs
            ]
        except Exception as exc:
            logger.error(f"Error querying audit logs by resource: {exc}")
            return []

    async def query_by_action(
        self,
        action: str | AuditAction,
        days: int = 7,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs by action type.

        Args:
            action: Action to query
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of audit log entries
        """
        if isinstance(action, AuditAction):
            action = action.value

        try:
            from db.models.core import AuditLog
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            logs = await AuditLog.filter(
                action=action,
                timestamp__gte=cutoff_date,
            ).limit(limit).order_by("-timestamp")

            return [
                {
                    "user_id": log.user_id,
                    "resource": log.resource,
                    "action": log.action,
                    "scope_level": log.scope_level,
                    "result": log.result,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details,
                }
                for log in logs
            ]
        except Exception as exc:
            logger.error(f"Error querying audit logs by action: {exc}")
            return []

    async def query_by_result(
        self,
        result: str | AuditResult,
        days: int = 7,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs by result (allowed/denied).

        Args:
            result: Result to query
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of audit log entries
        """
        if isinstance(result, AuditResult):
            result = result.value

        try:
            from db.models.core import AuditLog
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            logs = await AuditLog.filter(
                result=result,
                timestamp__gte=cutoff_date,
            ).limit(limit).order_by("-timestamp")

            return [
                {
                    "user_id": log.user_id,
                    "resource": log.resource,
                    "action": log.action,
                    "scope_level": log.scope_level,
                    "result": log.result,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details,
                }
                for log in logs
            ]
        except Exception as exc:
            logger.error(f"Error querying audit logs by result: {exc}")
            return []

    async def query_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum results

        Returns:
            List of audit log entries
        """
        try:
            from db.models.core import AuditLog

            logs = await AuditLog.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date,
            ).limit(limit).order_by("-timestamp")

            return [
                {
                    "user_id": log.user_id,
                    "resource": log.resource,
                    "action": log.action,
                    "scope_level": log.scope_level,
                    "result": log.result,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details,
                }
                for log in logs
            ]
        except Exception as exc:
            logger.error(f"Error querying audit logs by date range: {exc}")
            return []


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance.

    Returns:
        Global AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


async def init_audit_logger() -> AuditLogger:
    """Initialize and start global audit logger.

    Returns:
        Started AuditLogger instance
    """
    logger_instance = get_audit_logger()
    await logger_instance.start()
    return logger_instance


async def shutdown_audit_logger() -> None:
    """Shutdown global audit logger."""
    if _audit_logger:
        await _audit_logger.stop()
