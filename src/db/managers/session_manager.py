"""
Worker Session Manager — t367.

Implements session state save/restore:
- Save worker context, execution history, bookmarks to DB
- Restore on restart with integrity verification
- BLAKE2b hashing for integrity checks
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from tortoise.transactions import in_transaction

from db.models.worker import WorkerSession, WorkerState
from db.models.scope import ProjectScope, SessionScope as DBSession

logger = logging.getLogger(__name__)


class SessionStateError(Exception):
    """Session state management error."""
    pass


class IntegrityCheckError(SessionStateError):
    """Integrity verification failed."""
    pass


class SessionNotFoundError(SessionStateError):
    """Session not found."""
    pass


class WorkerSessionManager:
    """
    Manage worker session state save/restore (t367).
    
    Persists and restores:
    - Worker context data
    - Execution history
    - Bookmarks
    - Integrity verification via BLAKE2b hashing
    """
    
    def __init__(
        self,
        worker_id: str,
        project_id: int,
        session_id: Optional[str] = None
    ) -> None:
        """
        Initialize session manager.
        
        Args:
            worker_id: Unique worker identifier
            project_id: Project scope ID
            session_id: Optional session scope ID
        """
        self.worker_id = worker_id
        self.project_id = project_id
        self.session_id = session_id
    
    async def __aenter__(self) -> WorkerSessionManager:
        """
        Enter async context manager.
        
        Returns:
            Self for use in async with statement (t367)
        """
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context manager with optional cleanup.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred (t367)
        """
        # Optional cleanup can be added here if needed
        pass
    
    async def save_session(
        self,
        context_data: dict[str, Any],
        execution_history: list[dict[str, Any]],
        bookmarks: dict[str, Any]
    ) -> WorkerSession:
        """
        Save worker session state to database (t367).
        
        Persists context, history, and bookmarks with BLAKE2b integrity hashing.
        
        Args:
            context_data: Worker context variables and state
            execution_history: List of execution steps
            bookmarks: Execution bookmarks for resume capability
            
        Returns:
            Updated/created WorkerSession
            
        Raises:
            SessionStateError: If save fails
        """
        try:
            project = await ProjectScope.get_or_none(id=self.project_id)
            if not project:
                raise SessionStateError(f"Project {self.project_id} not found")
            
            session_obj = None
            if self.session_id:
                session_obj = await DBSession.get_or_none(
                    session_id=self.session_id
                )
            
            async with in_transaction():
                # Get or create worker session
                worker_session, created = await WorkerSession.get_or_create(
                    worker_id=self.worker_id,
                    defaults={
                        "project": project,
                        "session": session_obj,
                        "current_state": WorkerState.RUNNING,
                    }
                )
                
                # Update with new state
                worker_session.update_context(context_data)
                worker_session.update_execution_history(execution_history)
                worker_session.update_bookmarks(bookmarks)
                
                # Update metrics
                worker_session.steps_executed = len(execution_history)
                
                await worker_session.save()
            
            logger.info(
                f"Saved worker session {self.worker_id}: "
                f"{len(execution_history)} steps, "
                f"{len(bookmarks)} bookmarks"
            )
            
            return worker_session
        
        except Exception as e:
            raise SessionStateError(
                f"Failed to save session for {self.worker_id}: {str(e)}"
            ) from e
    
    async def restore_session(
        self,
        verify_integrity: bool = True
    ) -> WorkerSession:
        """
        Restore worker session state from database (t367).
        
        Restores context, history, and bookmarks with optional integrity verification.
        
        Args:
            verify_integrity: Whether to verify BLAKE2b hashes (t367)
            
        Returns:
            Restored WorkerSession
            
        Raises:
            SessionNotFoundError: If no session exists
            IntegrityCheckError: If integrity check fails
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                raise SessionNotFoundError(
                    f"No saved session for worker {self.worker_id}"
                )
            
            # Verify integrity if requested
            if verify_integrity:
                is_valid, failures = await worker_session.verify_integrity()
                if not is_valid:
                    error_msg = "Integrity check failed:\n" + "\n".join(failures)
                    raise IntegrityCheckError(error_msg)
            
            logger.info(
                f"Restored worker session {self.worker_id}: "
                f"{worker_session.steps_executed} steps, "
                f"state={worker_session.current_state}"
            )
            
            return worker_session
        
        except SessionNotFoundError:
            raise
        except IntegrityCheckError:
            raise
        except Exception as e:
            raise SessionStateError(
                f"Failed to restore session for {self.worker_id}: {str(e)}"
            ) from e
    
    async def clear_session(self) -> None:
        """
        Clear saved session data (cleanup).
        
        Useful for starting fresh or cleaning up old sessions.
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if worker_session:
                await worker_session.delete()
                logger.info(f"Cleared session for worker {self.worker_id}")
        
        except Exception as e:
            logger.error(f"Error clearing session for {self.worker_id}: {str(e)}")


class ExecutionHistoryManager:
    """
    Manage execution history within a session.
    
    Provides convenient methods to append steps and query history.
    """
    
    def __init__(
        self,
        worker_id: str
    ) -> None:
        """Initialize history manager."""
        self.worker_id = worker_id
    
    async def __aenter__(self) -> ExecutionHistoryManager:
        """
        Enter async context manager.
        
        Returns:
            Self for use in async with statement (t367)
        """
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context manager with optional cleanup.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred (t367)
        """
        # Optional cleanup can be added here if needed
        pass
    
    async def append_step(
        self,
        action: str,
        status: str = "success",
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Append execution step to history.
        
        Args:
            action: Action name (e.g., "fetch_intel", "analyze_findings")
            status: Step status (success, failure, skipped)
            result: Step result data
            error: Error message if failed
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                logger.warning(
                    f"No session for worker {self.worker_id}, "
                    f"creating new session"
                )
                return
            
            step = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "status": status,
                "result": result or {},
                "error": error,
            }
            
            history = worker_session.execution_history or []
            history.append(step)
            
            worker_session.update_execution_history(history)
            worker_session.steps_executed = len(history)
            
            await worker_session.save()
        
        except Exception as e:
            logger.error(
                f"Error appending step for {self.worker_id}: {str(e)}"
            )
    
    async def get_history(
        self,
        limit: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Get execution history.
        
        Args:
            limit: Max steps to return
            
        Returns:
            List of execution steps
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                return []
            
            history = worker_session.execution_history or []
            
            if limit:
                history = history[-limit:]
            
            return history
        
        except Exception as e:
            logger.error(f"Error retrieving history for {self.worker_id}: {str(e)}")
            return []
    
    async def clear_history(self) -> None:
        """Clear execution history."""
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if worker_session:
                worker_session.update_execution_history([])
                await worker_session.save()
        
        except Exception as e:
            logger.error(f"Error clearing history for {self.worker_id}: {str(e)}")


class BookmarkManager:
    """
    Manage execution bookmarks for resumable execution.
    
    Bookmarks enable pausing and resuming at specific points.
    """
    
    def __init__(
        self,
        worker_id: str
    ) -> None:
        """Initialize bookmark manager."""
        self.worker_id = worker_id
    
    async def __aenter__(self) -> BookmarkManager:
        """
        Enter async context manager.
        
        Returns:
            Self for use in async with statement (t367)
        """
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context manager with optional cleanup.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred (t367)
        """
        # Optional cleanup can be added here if needed
        pass
    
    async def set_bookmark(
        self,
        bookmark_name: str,
        line: Optional[int] = None,
        position: Optional[int] = None,
        state: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Set named bookmark for later resumption.
        
        Args:
            bookmark_name: Name of bookmark
            line: Line number for code-based bookmarks
            position: Position/offset for stream-based bookmarks
            state: State snapshot at bookmark
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                logger.warning(
                    f"No session for worker {self.worker_id}, "
                    f"cannot set bookmark"
                )
                return
            
            bookmarks = worker_session.bookmarks or {}
            
            bookmarks[bookmark_name] = {
                "timestamp": datetime.utcnow().isoformat(),
                "line": line,
                "position": position,
                "state": state or {},
            }
            
            worker_session.update_bookmarks(bookmarks)
            await worker_session.save()
            
            logger.debug(f"Set bookmark '{bookmark_name}' for {self.worker_id}")
        
        except Exception as e:
            logger.error(
                f"Error setting bookmark '{bookmark_name}' for {self.worker_id}: "
                f"{str(e)}"
            )
    
    async def get_bookmark(
        self,
        bookmark_name: str
    ) -> Optional[dict[str, Any]]:
        """
        Get named bookmark.
        
        Args:
            bookmark_name: Name of bookmark
            
        Returns:
            Bookmark data or None
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                return None
            
            bookmarks = worker_session.bookmarks or {}
            return bookmarks.get(bookmark_name)
        
        except Exception as e:
            logger.error(
                f"Error retrieving bookmark '{bookmark_name}' for {self.worker_id}: "
                f"{str(e)}"
            )
            return None
    
    async def delete_bookmark(
        self,
        bookmark_name: str
    ) -> None:
        """
        Delete named bookmark.
        
        Args:
            bookmark_name: Name of bookmark to delete
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                return
            
            bookmarks = worker_session.bookmarks or {}
            bookmarks.pop(bookmark_name, None)
            
            worker_session.update_bookmarks(bookmarks)
            await worker_session.save()
            
            logger.debug(f"Deleted bookmark '{bookmark_name}' for {self.worker_id}")
        
        except Exception as e:
            logger.error(
                f"Error deleting bookmark '{bookmark_name}' for {self.worker_id}: "
                f"{str(e)}"
            )
    
    async def list_bookmarks(self) -> list[str]:
        """
        List all bookmark names.
        
        Returns:
            List of bookmark names
        """
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if not worker_session:
                return []
            
            bookmarks = worker_session.bookmarks or {}
            return list(bookmarks.keys())
        
        except Exception as e:
            logger.error(f"Error listing bookmarks for {self.worker_id}: {str(e)}")
            return []
    
    async def clear_bookmarks(self) -> None:
        """Clear all bookmarks."""
        try:
            worker_session = await WorkerSession.get_or_none(
                worker_id=self.worker_id
            )
            
            if worker_session:
                worker_session.update_bookmarks({})
                await worker_session.save()
        
        except Exception as e:
            logger.error(f"Error clearing bookmarks for {self.worker_id}: {str(e)}")
