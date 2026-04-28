"""
Tests for t368: Worker-Scope Integration.

Tests scope binding, permission checks, and audit trails.
"""
import pytest
from datetime import datetime

from db.models.worker import (
    WorkerStateTransition,
    WorkerSession,
    WorkerAuditLog,
    WorkerState,
)
from db.models.scope import ProjectScope
from db.managers.worker_manager import WorkerStateMachine


@pytest.mark.asyncio
class TestWorkerScopeBinding:
    """Test scope binding for workers (t368)."""
    
    async def test_worker_transition_binds_to_project_scope(
        self,
        test_project
    ) -> None:
        """Test that state transitions bind to project scope."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-1",
            project_id=test_project.id,
        )
        
        transition = await sm.transition(
            to_state=WorkerState.RUNNING,
            reason="Start"
        )
        
        assert transition.project_id == test_project.id
        assert transition.session is None  # No session scope
    
    async def test_worker_transition_binds_to_session_scope(
        self,
        test_project,
        test_session
    ) -> None:
        """Test that state transitions bind to session scope."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-2",
            project_id=test_project.id,
            session_id=test_session.session_id,
        )
        
        transition = await sm.transition(
            to_state=WorkerState.RUNNING,
            reason="Start"
        )
        
        assert transition.project_id == test_project.id
        assert transition.session_id == test_session.id
    
    async def test_worker_session_inherits_scope_from_project(
        self,
        test_project
    ) -> None:
        """Test that worker sessions inherit project scope."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-3",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        session = await WorkerSession.get(worker_id="worker-scope-3")
        assert session.project_id == test_project.id
    
    async def test_worker_session_inherits_scope_from_session(
        self,
        test_project,
        test_session
    ) -> None:
        """Test that worker sessions inherit session scope."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-4",
            project_id=test_project.id,
            session_id=test_session.session_id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        session = await WorkerSession.get(worker_id="worker-scope-4")
        assert session.project_id == test_project.id
        assert session.session_id == test_session.id
    
    async def test_scope_level_set_correctly_for_project(
        self,
        test_project
    ) -> None:
        """Test that scope_level is set to 'project' when no session."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-5",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        # Check audit log
        audit_log = await WorkerAuditLog.get(worker_id="worker-scope-5")
        assert audit_log.scope_level == "project"
    
    async def test_scope_level_set_correctly_for_session(
        self,
        test_project,
        test_session
    ) -> None:
        """Test that scope_level is set to 'session' when session provided."""
        sm = WorkerStateMachine(
            worker_id="worker-scope-6",
            project_id=test_project.id,
            session_id=test_session.session_id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        # Check audit log
        audit_log = await WorkerAuditLog.get(worker_id="worker-scope-6")
        assert audit_log.scope_level == "session"


@pytest.mark.asyncio
class TestScopeBasedFiltering:
    """Test scope-based filtering (t368)."""
    
    async def test_filter_transitions_by_project_scope(
        self,
        test_project
    ) -> None:
        """Test filtering transitions by project scope."""
        sm = WorkerStateMachine(
            worker_id="worker-filter-1",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        # Query transitions for this project
        transitions = await WorkerStateTransition.filter(
            project_id=test_project.id
        ).all()
        
        assert any(t.worker_id == "worker-filter-1" for t in transitions)
    
    async def test_filter_transitions_by_state_and_scope(
        self,
        test_project
    ) -> None:
        """Test filtering transitions by state within scope."""
        # Create multiple workers in different states
        for i in range(3):
            sm = WorkerStateMachine(f"worker-filter-{i}", test_project.id)
            if i < 2:
                await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
            else:
                await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
                await sm.transition(to_state=WorkerState.PAUSED, reason="Pause")
        
        # Filter running workers in project scope
        running_in_project = await WorkerStateTransition.filter(
            project_id=test_project.id,
            to_state=WorkerState.RUNNING
        ).all()
        
        assert len(running_in_project) >= 3  # At least 3 running transitions
    
    async def test_filter_audit_logs_by_scope(
        self,
        test_project
    ) -> None:
        """Test filtering audit logs by scope."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-1",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        # Filter audit logs for project
        audit_logs = await WorkerAuditLog.filter(
            project_id=test_project.id,
            scope_level="project"
        ).all()
        
        assert any(log.worker_id == "worker-audit-1" for log in audit_logs)
    
    async def test_filter_audit_logs_by_state_action(
        self,
        test_project
    ) -> None:
        """Test filtering audit logs by action."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-2",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        await sm.transition(to_state=WorkerState.PAUSED, reason="Pause")
        
        # Filter state_transition actions
        state_transitions = await WorkerAuditLog.filter(
            worker_id="worker-audit-2",
            action="state_transition"
        ).all()
        
        assert len(state_transitions) >= 2


@pytest.mark.asyncio
class TestPermissionChecks:
    """Test permission checks in audit trail (t368)."""
    
    async def test_successful_transition_records_permission_pass(
        self,
        test_project
    ) -> None:
        """Test that successful transition records permission pass."""
        sm = WorkerStateMachine(
            worker_id="worker-perm-1",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        audit_log = await WorkerAuditLog.get(worker_id="worker-perm-1")
        assert audit_log.permission_check_passed is True
        assert audit_log.permission_required == "worker_state_transition"
    
    async def test_audit_log_records_permission_type(
        self,
        test_project
    ) -> None:
        """Test that audit log records what permission was required."""
        sm = WorkerStateMachine(
            worker_id="worker-perm-2",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        audit_log = await WorkerAuditLog.get(worker_id="worker-perm-2")
        assert audit_log.permission_required in [
            "worker_state_transition",
            "worker_pause",
            "worker_resume",
        ]
    
    async def test_audit_log_records_action_status(
        self,
        test_project
    ) -> None:
        """Test that audit log records action status."""
        sm = WorkerStateMachine(
            worker_id="worker-perm-3",
            project_id=test_project.id,
        )
        
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        
        audit_log = await WorkerAuditLog.get(worker_id="worker-perm-3")
        assert audit_log.status in ["success", "failure", "denied"]


@pytest.mark.asyncio
class TestAuditTrail:
    """Test comprehensive audit trail (t368)."""
    
    async def test_audit_log_records_all_transitions(
        self,
        test_project
    ) -> None:
        """Test that audit log records all state transitions."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-trail-1",
            project_id=test_project.id,
        )
        
        states = [
            WorkerState.RUNNING,
            WorkerState.PAUSED,
            WorkerState.RUNNING,
            WorkerState.COMPLETED,
        ]
        
        for state in states:
            await sm.transition(to_state=state, reason=f"Transition to {state}")
        
        # Get audit logs
        audit_logs = await WorkerAuditLog.filter(
            worker_id="worker-audit-trail-1"
        ).order_by("occurred_at").all()
        
        assert len(audit_logs) == len(states)
        
        # Verify all actions are state_transition
        assert all(log.action == "state_transition" for log in audit_logs)
    
    async def test_audit_log_includes_transition_details(
        self,
        test_project
    ) -> None:
        """Test that audit log includes detailed transition info."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-trail-2",
            project_id=test_project.id,
        )
        
        reason = "Manual intervention required"
        metadata = {"risk_score": 0.85}
        
        await sm.transition(
            to_state=WorkerState.RUNNING,
            reason=reason,
            metadata=metadata
        )
        
        audit_log = await WorkerAuditLog.get(worker_id="worker-audit-trail-2")
        
        assert audit_log.details["reason"] == reason
        assert audit_log.details["metadata"]["risk_score"] == 0.85
    
    async def test_audit_log_timestamp_reflects_action_time(
        self,
        test_project
    ) -> None:
        """Test that audit log timestamp is recorded correctly."""
        from datetime import timezone
        
        sm = WorkerStateMachine(
            worker_id="worker-audit-trail-3",
            project_id=test_project.id,
        )
        
        before_time = datetime.now(timezone.utc)
        await sm.transition(to_state=WorkerState.RUNNING, reason="Start")
        after_time = datetime.now(timezone.utc)
        
        audit_log = await WorkerAuditLog.get(worker_id="worker-audit-trail-3")
        
        # Convert to UTC-aware if needed
        log_time = audit_log.occurred_at
        if log_time.tzinfo is None:
            log_time = log_time.replace(tzinfo=timezone.utc)
        
        assert before_time <= log_time <= after_time
    
    async def test_audit_trail_retrievable_per_worker(
        self,
        test_project
    ) -> None:
        """Test that audit trail is retrievable for specific worker."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-trail-4",
            project_id=test_project.id,
        )
        
        # Make several transitions
        for i in range(3):
            if i == 0:
                await sm.transition(to_state=WorkerState.RUNNING)
            else:
                await sm.transition(
                    to_state=WorkerState.PAUSED if i % 2 == 1 else WorkerState.RUNNING
                )
        
        # Retrieve audit trail through state machine
        audit_trail = await sm.get_audit_trail()
        
        assert len(audit_trail) >= 3
        assert all(log.worker_id == "worker-audit-trail-4" for log in audit_trail)
    
    async def test_audit_logs_maintain_order(
        self,
        test_project
    ) -> None:
        """Test that audit logs maintain temporal order."""
        sm = WorkerStateMachine(
            worker_id="worker-audit-trail-5",
            project_id=test_project.id,
        )
        
        # Make transitions
        await sm.transition(to_state=WorkerState.RUNNING)
        await sm.transition(to_state=WorkerState.PAUSED)
        await sm.transition(to_state=WorkerState.RUNNING)
        
        audit_logs = await WorkerAuditLog.filter(
            worker_id="worker-audit-trail-5"
        ).order_by("-occurred_at").all()
        
        # Verify descending order (most recent first)
        for i in range(len(audit_logs) - 1):
            assert audit_logs[i].occurred_at >= audit_logs[i+1].occurred_at


@pytest.mark.asyncio
class TestScopeIsolation:
    """Test scope isolation between projects."""
    
    async def test_workers_isolated_between_projects(
        self,
        test_project
    ) -> None:
        """Test that workers are isolated between project scopes."""
        # Create second project
        project2 = await ProjectScope.create(
            name="test-project-2",
            description="Test project 2"
        )
        
        # Create workers in each project
        sm1 = WorkerStateMachine("worker-iso-1", test_project.id)
        sm2 = WorkerStateMachine("worker-iso-2", project2.id)
        
        await sm1.transition(to_state=WorkerState.RUNNING)
        await sm2.transition(to_state=WorkerState.RUNNING)
        
        # Verify transitions are isolated
        transitions1 = await WorkerStateTransition.filter(
            project_id=test_project.id,
            worker_id="worker-iso-1"
        ).all()
        
        transitions2 = await WorkerStateTransition.filter(
            project_id=project2.id,
            worker_id="worker-iso-2"
        ).all()
        
        # Cross-project queries should be empty
        cross_query = await WorkerStateTransition.filter(
            project_id=test_project.id,
            worker_id="worker-iso-2"
        ).all()
        
        assert len(transitions1) >= 1
        assert len(transitions2) >= 1
        assert len(cross_query) == 0
    
    async def test_audit_logs_isolated_between_projects(
        self,
        test_project
    ) -> None:
        """Test that audit logs are isolated between projects."""
        project2 = await ProjectScope.create(
            name="test-project-3",
            description="Test project 3"
        )
        
        sm1 = WorkerStateMachine("worker-iso-3", test_project.id)
        sm2 = WorkerStateMachine("worker-iso-4", project2.id)
        
        await sm1.transition(to_state=WorkerState.RUNNING)
        await sm2.transition(to_state=WorkerState.RUNNING)
        
        # Audit logs for project 1
        logs1 = await WorkerAuditLog.filter(
            project_id=test_project.id
        ).all()
        
        # Audit logs for project 2
        logs2 = await WorkerAuditLog.filter(
            project_id=project2.id
        ).all()
        
        # Should not cross-pollinate
        assert all(log.project_id == test_project.id for log in logs1)
        assert all(log.project_id == project2.id for log in logs2)
