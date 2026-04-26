"""
Worker State Machine Manager — t366.

Implements state machine logic:
- State transitions: queued → running → paused → complete/failed
- Transition validation
- Query/filter by state
- Event logging and audit trail
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from db.models.worker import (
    WorkerState,
    WorkerStateTransition,
    WorkerSession,
    WorkerAuditLog,
)
from db.models.scope import Project, Session

logger = logging.getLogger(__name__)


class WorkerStateMachineError(Exception):
    """Worker state machine operation error."""
    pass


class InvalidStateTransitionError(WorkerStateMachineError):
    """Invalid state transition attempted."""
    pass


class WorkerNotFoundError(WorkerStateMachineError):
    """Worker not found."""
    pass


class WorkerStateMachine:
    """
    State machine manager for worker lifecycle (t366).
    
    Handles state transitions with validation, audit logging, and queries.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        WorkerState.QUEUED: [WorkerState.RUNNING, WorkerState.FAILED],
        WorkerState.RUNNING: [WorkerState.PAUSED, WorkerState.COMPLETED, WorkerState.FAILED],
        WorkerState.PAUSED: [WorkerState.RUNNING, WorkerState.FAILED, WorkerState.COMPLETED],
        WorkerState.COMPLETED: [],  # Terminal state
        WorkerState.FAILED: [WorkerState.QUEUED],  # Allow retry (failed → queued)
    }
    
    def __init__(
        self,
        worker_id: str,
        project_id: int,
        session_id: Optional[str] = None,
        worker_type: str = "generic"
    ) -> None:
        """
        Initialize state machine for a worker.
        
        Args:
            worker_id: Unique worker identifier
            project_id: Project scope ID
            session_id: Optional session scope ID
            worker_type: Type of worker
        """
        self.worker_id = worker_id
        self.project_id = project_id
        self.session_id = session_id
        self.worker_type = worker_type
        self._cached_session: Optional[Session] = None
    
    async def _get_session_obj(self) -> Optional[Session]:
        """
        Get Session object with caching to eliminate N+1 queries (t366).
        
        Returns:
            Session object if session_id is set, None otherwise
        """
        if not self.session_id:
            return None
        
        # Return cached session if available
        if self._cached_session is not None:
            return self._cached_session
        
        # Fetch and cache session
        self._cached_session = await Session.get_or_none(
            session_id=self.session_id
        )
        return self._cached_session
    
    async def transition(
        self,
        to_state: WorkerState,
        reason: str = "",
        metadata: Optional[dict[str, Any]] = None
    ) -> WorkerStateTransition:
        """
        Transition worker to new state with validation.
        
        Args:
            to_state: Target state
            reason: Reason for transition
            metadata: Additional context
            
        Returns:
            Created WorkerStateTransition record
            
        Raises:
            InvalidStateTransitionError: If transition not allowed
            WorkerNotFoundError: If worker session not found
        """
        metadata = metadata or {}
        
        # Get current state
        try:
            session = await WorkerSession.get(worker_id=self.worker_id)
            from_state = session.current_state
        except DoesNotExist:
            from_state = WorkerState.QUEUED
        
        # Validate transition
        if from_state not in self.VALID_TRANSITIONS:
            raise InvalidStateTransitionError(
                f"Unknown source state: {from_state}"
            )
        
        if to_state not in self.VALID_TRANSITIONS[from_state]:
            raise InvalidStateTransitionError(
                f"Invalid transition: {from_state} → {to_state}. "
                f"Allowed: {self.VALID_TRANSITIONS[from_state]}"
            )
        
        project = await Project.get_or_none(id=self.project_id)
        if not project:
            raise WorkerNotFoundError(f"Project {self.project_id} not found")
        
        async with in_transaction():
            # Get cached session object once to eliminate N+1 queries
            session_obj = await self._get_session_obj()
            
            # Create transition record
            transition = await WorkerStateTransition.create(
                worker_id=self.worker_id,
                worker_type=self.worker_type,
                project=project,
                session=session_obj,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
                metadata=metadata,
            )
            
            # Update session current state
            if from_state == WorkerState.QUEUED and to_state == WorkerState.RUNNING:
                # First transition - create session if doesn't exist
                session, created = await WorkerSession.get_or_create(
                    worker_id=self.worker_id,
                    defaults={
                        "worker_type": self.worker_type,
                        "project": project,
                        "session": session_obj,
                        "current_state": to_state,
                    }
                )
                if not created:
                    session.current_state = to_state
                    await session.save()
            else:
                # Update existing session
                session = await WorkerSession.get_or_none(worker_id=self.worker_id)
                if session:
                    session.current_state = to_state
                    await session.save()
                else:
                    await WorkerSession.create(
                        worker_id=self.worker_id,
                        worker_type=self.worker_type,
                        project=project,
                        session=session_obj,
                        current_state=to_state,
                    )
            
            # Log audit trail
            await WorkerAuditLog.create(
                worker_id=self.worker_id,
                project=project,
                session=session_obj,
                scope_level="session" if self.session_id else "project",
                action="state_transition",
                status="success",
                permission_check_passed=True,
                permission_required="worker_state_transition",
                details={
                    "from_state": str(from_state),
                    "to_state": str(to_state),
                    "reason": reason,
                    "metadata": metadata,
                },
            )
        
        logger.info(
            f"Worker {self.worker_id} transitioned: {from_state} → {to_state} "
            f"(reason: {reason})"
        )
        
        return transition
    
    async def get_current_state(self) -> WorkerState:
        """
        Get current worker state.
        
        Returns:
            Current WorkerState
        """
        session = await WorkerSession.get_or_none(worker_id=self.worker_id)
        if session:
            return session.current_state
        return WorkerState.QUEUED
    
    async def get_transition_history(
        self,
        limit: int = 100
    ) -> list[WorkerStateTransition]:
        """
        Get transition history for worker (t366 - query).
        
        Args:
            limit: Max records to return
            
        Returns:
            List of transitions ordered by timestamp desc
        """
        return await WorkerStateTransition.filter(
            worker_id=self.worker_id
        ).order_by(
            "-transitioned_at"
        ).limit(limit)
    
    async def get_audit_trail(
        self,
        limit: int = 100
    ) -> list[WorkerAuditLog]:
        """
        Get audit trail for worker (t368).
        
        Args:
            limit: Max records to return
            
        Returns:
            List of audit logs ordered by timestamp desc
        """
        return await WorkerAuditLog.filter(
            worker_id=self.worker_id
        ).order_by(
            "-occurred_at"
        ).limit(limit)


class WorkerStateQueryEngine:
    """
    Query and filter workers by state (t366).
    """
    
    @staticmethod
    async def get_workers_by_state(
        to_state: WorkerState,
        project_id: Optional[int] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> list[WorkerSession]:
        """
        Query workers by current state (t366 - filter).
        
        Args:
            to_state: Filter by this state
            project_id: Optional project filter
            session_id: Optional session filter
            limit: Max results
            
        Returns:
            List of worker sessions in requested state
        """
        query = WorkerSession.filter(current_state=to_state)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        if session_id:
            query = query.filter(session__session_id=session_id)
        
        return await query.limit(limit)
    
    @staticmethod
    async def get_workers_by_multiple_states(
        states: list[WorkerState],
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> list[WorkerSession]:
        """
        Query workers in any of multiple states.
        
        Args:
            states: Filter by any of these states
            project_id: Optional project filter
            limit: Max results
            
        Returns:
            List of worker sessions
        """
        query = WorkerSession.filter(current_state__in=states)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        return await query.limit(limit)
    
    @staticmethod
    async def count_workers_by_state(
        to_state: WorkerState,
        project_id: Optional[int] = None
    ) -> int:
        """
        Count workers in a given state.
        
        Args:
            to_state: State to count
            project_id: Optional project filter
            
        Returns:
            Count of workers in state
        """
        query = WorkerSession.filter(current_state=to_state)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        return await query.count()
    
    @staticmethod
    async def get_state_distribution(
        project_id: Optional[int] = None
    ) -> dict[str, int]:
        """
        Get distribution of workers across states.
        
        Args:
            project_id: Optional project filter
            
        Returns:
            Dictionary mapping state name to count
        """
        distribution = {}
        
        for state in WorkerState:
            count = await WorkerStateQueryEngine.count_workers_by_state(
                state,
                project_id=project_id
            )
            distribution[str(state)] = count
        
        return distribution
    
    @staticmethod
    async def get_stale_workers(
        inactivity_seconds: int = 3600,
        project_id: Optional[int] = None
    ) -> list[WorkerSession]:
        """
        Get workers inactive for threshold time (cleanup).
        
        Args:
            inactivity_seconds: Inactivity threshold
            project_id: Optional project filter
            
        Returns:
            List of stale worker sessions
        """
        from datetime import timedelta
        
        threshold = datetime.utcnow() - timedelta(seconds=inactivity_seconds)
        
        query = WorkerSession.filter(last_activity_at__lt=threshold)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        return await query
