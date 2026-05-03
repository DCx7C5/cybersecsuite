"""TeamLeader — in-process orchestrator coordinator.

Manages a Team and delegates work to TeamMember(s) within the same process.
Holds persistent FK to Team model.
"""

from typing import Any, Optional
import asyncio
import uuid
from datetime import datetime

from css.core.db.models import Team as TeamModel
from css.core.types import Query
from css.modules.tasks import Task, TaskScope, TaskLifecycle, TaskStatus


class TeamLeader:
    """In-process coordinator for a Team + Orchestrator.
    
    Responsibilities:
    - Hold FK reference to Team (persistent)
    - Coordinate task distribution to TeamMember(s)
    - Manage task lifecycle (queue, execute, complete, fail, retry)
    - Aggregate results with timeout + exception handling
    """
    
    def __init__(self, team_id: int, orchestrator_id: str):
        """Initialize TeamLeader for a specific Team.
        
        Args:
            team_id: FK to Team model (persistent)
            orchestrator_id: Unique orchestrator identifier
        """
        self.team_id = team_id
        self.orchestrator_id = orchestrator_id
        self.team_model: Optional[TeamModel] = None
        self._members: dict[str, "TeamMember"] = {}
    
    async def initialize(self) -> None:
        """Load Team model and validate."""
        from tortoise.exceptions import DoesNotExist
        try:
            self.team_model = await TeamModel.get(id=self.team_id)
        except DoesNotExist:
            raise ValueError(f"Team {self.team_id} not found")
    
    def add_member(self, member_id: str, member: "TeamMember") -> None:
        """Register a TeamMember."""
        self._members[member_id] = member
    
    async def delegate(self, query: Query) -> dict[str, Any]:
        """Delegate query to best available TeamMember with retry loop (B7).
        
        Implements exponential backoff for retries up to max_retries.
        
        Args:
            query: Query object from QueryExecutor
            
        Returns:
            dict with status, result, error, execution_time_ms
        """
        if not self._members:
            raise RuntimeError(f"No team members available for team {self.team_id}")
        
        # Create Task from Query (B4)
        task = self._create_task_from_query(query)
        
        # Retry loop with exponential backoff (B7)
        while True:
            try:
                result = await self._execute_task_once(task)
                
                # Success path
                if result.get("status") == "completed":
                    return result
                
                # Failed path - check if we can retry
                if task.can_retry():
                    # Reset task to queued for retry (B7)
                    await TaskLifecycle.retry_task(task)
                    
                    # Exponential backoff: 2^retry_count seconds (capped at 30s)
                    backoff_seconds = min(2 ** task.retry_count, 30)
                    await asyncio.sleep(backoff_seconds)
                    
                    # Continue loop to retry
                    continue
                else:
                    # Max retries exceeded
                    return result
            
            except Exception as e:
                # Unexpected error - fail without retry
                error_msg = f"TeamLeader error: {str(e)}"
                try:
                    await TaskLifecycle.fail_task(task, error_msg)
                except Exception:
                    pass
                
                return {
                    "status": "failed",
                    "task_id": task.id,
                    "error": error_msg,
                    "execution_time_ms": 0,
                }
    
    async def _execute_task_once(self, task: Task) -> dict[str, Any]:
        """Execute task once without retry (helper for B7).
        
        Args:
            task: Task to execute
            
        Returns:
            dict with status, result, error, execution_time_ms
        """
        try:
            # Transition to queued (TaskLifecycle)
            await TaskLifecycle.queue_task(task)
            
            # Find available member
            member = self._find_available_member()
            if member is None:
                raise RuntimeError(f"No available members for team {self.team_id}")
            
            # Transition to executing with member assignment
            await TaskLifecycle.execute_task(task, member.member_id)
            
            # Execute with timeout enforcement (B6)
            timeout_seconds = task.scope.timeout_seconds
            try:
                result = await asyncio.wait_for(
                    member.execute(task),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                error_msg = f"Task timeout after {timeout_seconds}s"
                await TaskLifecycle.fail_task(task, error_msg)
                return {
                    "status": "failed",
                    "task_id": task.id,
                    "error": error_msg,
                    "execution_time_ms": int(timeout_seconds * 1000),
                }
            
            # Handle success (B4)
            if result.get("status") == "completed":
                await TaskLifecycle.complete_task(task, result.get("result"))
                return {
                    "status": "completed",
                    "task_id": task.id,
                    "result": result.get("result"),
                    "execution_time_ms": result.get("execution_time_ms", 0),
                }
            else:
                # Handle member-side failure (B8)
                error_msg = result.get("error", "Unknown error")
                await TaskLifecycle.fail_task(task, error_msg)
                return {
                    "status": "failed",
                    "task_id": task.id,
                    "error": error_msg,
                    "execution_time_ms": result.get("execution_time_ms", 0),
                }
        
        except Exception as e:
            # Exception handling (B8): update state and return error
            error_msg = f"Execution error: {str(e)}"
            try:
                await TaskLifecycle.fail_task(task, error_msg)
            except Exception:
                pass
            
            return {
                "status": "failed",
                "task_id": task.id,
                "error": error_msg,
                "execution_time_ms": 0,
            }
    
    def _create_task_from_query(self, query: Query) -> Task:
        """Convert Query to Task with TeamLeader context (B4)."""
        task_id = str(uuid.uuid4())
        scope = TaskScope(
            id=task_id,
            team_id=self.team_id,
            orchestrator_id=self.orchestrator_id,
            query=query,
            priority=query.metadata.get("priority", "normal"),
            timeout_seconds=query.metadata.get("timeout_seconds", 300),
            max_retries=query.metadata.get("max_retries", 3),
        )
        return Task(id=task_id, scope=scope)
    
    def _find_available_member(self) -> Optional["TeamMember"]:
        """Find first available member (round-robin)."""
        for member in self._members.values():
            if member.is_available():
                return member
        return None
    
    async def pause_team(self) -> None:
        """Pause all team members."""
        for member in self._members.values():
            await member.pause()
    
    async def resume_team(self) -> None:
        """Resume all team members."""
        for member in self._members.values():
            await member.resume()
    
    async def shutdown(self) -> None:
        """Shutdown all team members."""
        for member in self._members.values():
            await member.shutdown()
