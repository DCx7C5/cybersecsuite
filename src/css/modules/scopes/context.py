from typing import Any, Optional

from css.core.db import ScopeLevel


class ScopeContext:
    """Context object for scopes resolution (2-level model: GLOBAL + SESSION only)."""

    def __init__(
        self,
        scope_level: str | ScopeLevel,
        session_id: Optional[str] = None,
        worktree_path: Optional[str] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> None:
        """Initialize scopes context (simplified for 2-level model).

        Args:
            scope_level: One of: global, session (only these two supported now)
            session_id: Session identifier (required for session scope, optional for global)
            worktree_path: Absolute path to worktree directory
            user_id: User identifier for permission checks
            user_role: User role (admin, analyst, viewer, etc.)
        """
        if isinstance(scope_level, str):
            try:
                self.scope_level = ScopeLevel(scope_level)
            except ValueError:
                raise ValueError(f"Invalid scopes level: {scope_level}. Must be 'global' or 'session'.")
        else:
            self.scope_level = scope_level

        self.session_id = session_id
        self.worktree_path = worktree_path
        self.user_id = user_id
        self.user_role = user_role
        self._validate()

    def _validate(self) -> None:
        """Validate scopes context consistency (2-level model)."""
        if self.scope_level == ScopeLevel.GLOBAL:
            # GLOBAL scope: no requirements
            pass
        elif self.scope_level == ScopeLevel.SESSION:
            # SESSION scope: session_id is required
            if not self.session_id:
                raise ValueError("SESSION scope requires session_id")
        else:
            raise ValueError(f"Unexpected scope level: {self.scope_level}. Only GLOBAL and SESSION are supported.")

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "scope_level": self.scope_level.value,
            "session_id": self.session_id,
            "worktree_path": self.worktree_path,
            "user_id": self.user_id,
            "user_role": self.user_role,
        }
