"""Team lifecycle state machine."""

class TeamLifecycle:
    """Manage team status transitions."""
    
    @staticmethod
    def can_activate(current_status: str) -> bool:
        return current_status == "pending"
    
    @staticmethod
    def can_pause(current_status: str) -> bool:
        return current_status == "active"
    
    @staticmethod
    def can_resume(current_status: str) -> bool:
        return current_status == "paused"
    
    @staticmethod
    def can_complete(current_status: str) -> bool:
        return current_status in ("active", "paused")
