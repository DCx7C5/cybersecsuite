from typing import Any, Optional

from css.core.db import ScopeLevel


class ScopeContext:
    """Context object for scopes resolution."""

    def __init__(
        self,
        scope_level: str | ScopeLevel,
        project_id: Optional[int] = None,
        session_id: Optional[str] = None,
        runtime_id: Optional[str] = None,
        worktree_path: Optional[str] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> None:
        """Initialize scopes context.

        Args:
            scope_level: One of: global, app, project, runtime, session
            project_id: Project identifier (for project+ scopes)
            session_id: Session identifier (for session scopes)
            runtime_id: Container/pod runtime identity (for runtime+ scopes)
            worktree_path: Absolute path to worktree directory
            user_id: User identifier for permission checks
            user_role: User role (admin, analyst, viewer, etc.)
        """
        if isinstance(scope_level, str):
            try:
                self.scope_level = ScopeLevel(scope_level)
            except ValueError:
                raise ValueError(f"Invalid scopes level: {scope_level}")
        else:
            self.scope_level = scope_level

        self.project_id = project_id
        self.session_id = session_id
        self.runtime_id = runtime_id
        self.worktree_path = worktree_path
        self.user_id = user_id
        self.user_role = user_role
        self._validate()

    def _validate(self) -> None:
        """Validate scopes context consistency."""
        # Higher scopes should have lower scopes attributes
        if self.scope_level == ScopeLevel.GLOBAL:
            pass
        elif self.scope_level == ScopeLevel.APP:
            pass
        elif self.scope_level == ScopeLevel.PROJECT:
            if not self.project_id:
                raise ValueError("PROJECT scopes requires project_id")
        elif self.scope_level == ScopeLevel.RUNTIME:
            if not self.runtime_id:
                raise ValueError("RUNTIME scopes requires runtime_id")
            if not self.worktree_path:
                raise ValueError("RUNTIME scopes requires worktree_path")
        elif self.scope_level == ScopeLevel.SESSION:
            if not self.session_id:
                raise ValueError("SESSION scopes requires session_id")
            if not self.project_id:
                raise ValueError("SESSION scopes requires project_id")

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "scope_level": self.scope_level.value,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "runtime_id": self.runtime_id,
            "worktree_path": self.worktree_path,
            "user_id": self.user_id,
            "user_role": self.user_role,
        }
