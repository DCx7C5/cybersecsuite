"""TeamMember — in-process worker within Orchestrator.

Executes tasks delegated by TeamLeader within the same process.
"""

from typing import Any, Optional


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
    
    async def execute(self, task_data: dict[str, Any]) -> Any:
        """Execute task.
        
        Args:
            task_data: Task payload
            
        Returns:
            Task result
        """
        if self._is_paused:
            raise RuntimeError(f"Member {self.member_id} is paused")
        
        if not self._is_available:
            raise RuntimeError(f"Member {self.member_id} is unavailable")
        
        # Placeholder: actual execution logic
        return {
            "member_id": self.member_id,
            "task": task_data,
            "status": "completed",
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
