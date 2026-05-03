"""TeamMember — in-process worker within Orchestrator.

Executes tasks delegated by TeamLeader within the same process.
"""

from typing import Any, Optional
import time


class TeamMember:
    """In-process team member executor.
    
    Responsibilities:
    - Execute tasks from TeamLeader
    - Report availability/status
    - Handle pause/resume
    - Clean shutdown
    """
    
    def __init__(self, member_id: str):
        """Initialize TeamMember.
        
        Args:
            member_id: Unique member identifier within team
        """
        self.member_id = member_id
        self._is_available = True
        self._is_paused = False
    
    def is_available(self) -> bool:
        """Check if member can accept work."""
        return self._is_available and not self._is_paused
    
    async def execute(self, task: Any) -> dict[str, Any]:
        """Execute task (B12).
        
        Args:
            task: Task object (modules.tasks.Task)
            
        Returns:
            dict with "status", "result", and "error" keys
        """
        if self._is_paused:
            raise RuntimeError(f"Member {self.member_id} is paused")
        
        if not self._is_available:
            raise RuntimeError(f"Member {self.member_id} is unavailable")
        
        # Task must have scope with query
        if not hasattr(task, 'scope') or not hasattr(task.scope, 'query'):
            raise ValueError(f"Invalid task object: missing scope.query")
        
        start_time = time.time()
        query = task.scope.query
        
        try:
            # Placeholder: execute the query (actual logic in Phase 2)
            # For now, return a mock result
            result_text = f"Executed: {query.prompt[:100]}..."
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "completed",
                "member_id": self.member_id,
                "task_id": task.id,
                "result": result_text,
                "execution_time_ms": execution_time_ms,
            }
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return {
                "status": "failed",
                "member_id": self.member_id,
                "task_id": task.id,
                "error": str(e),
                "execution_time_ms": execution_time_ms,
            }
    
    async def pause(self) -> None:
        """Pause member."""
        self._is_paused = True
    
    async def resume(self) -> None:
        """Resume member."""
        self._is_paused = False
    
    async def shutdown(self) -> None:
        """Shutdown member."""
        self._is_available = False
        self._is_paused = False

