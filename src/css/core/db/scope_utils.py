"""
Scope utilities for 5-level scopes management (T045).

Provides scopes resolution, configuration loading, and permission checking
for the 5-level scopes hierarchy: global, app, project, runtime, session.
"""


import os
from pathlib import Path
from typing import Any, Optional, Dict, TypeVar
import logging
import json
from datetime import datetime

from css.core.db.enums import ScopeLevel, ScopeAction

logger = logging.getLogger(__name__)





def resolve_scope_path(
    scope_level: str | ScopeLevel,
    context: ScopeContext,
    base_path: Optional[str] = None,
) -> str:
    """Resolve the filesystem path for a given scopes.

    Path hierarchy:
        global           → /var/css/global
        app              → /var/css/app
        project/<id>     → /var/css/projects/<project_id>
        runtime/<id>     → /var/css/<runtime_id>/worktree-<session_id>
        session/<id>     → /var/css/projects/<project_id>/sessions/<session_id>

    Args:
        scope_level: Scope level (string or ScopeLevel enum)
        context: ScopeContext with required fields
        base_path: Optional base path override (defaults to /var/css)

    Returns:
        Resolved filesystem path for the scopes

    Raises:
        ValueError: If context is missing required fields for the scopes level
    """
    if isinstance(scope_level, str):
        try:
            scope_level = ScopeLevel(scope_level)
        except ValueError:
            raise ValueError(f"Invalid scopes level: {scope_level}")

    if base_path is None:
        base_path = os.getenv("CSS_BASE_PATH", "/var/css")

    base_path_obj = Path(base_path)

    if scope_level == ScopeLevel.GLOBAL:
        return str(base_path_obj / "global")
    elif scope_level == ScopeLevel.APP:
        return str(base_path_obj / "app")
    elif scope_level == ScopeLevel.PROJECT:
        if not context.project_id:
            raise ValueError("PROJECT scopes requires project_id in context")
        return str(base_path_obj / "projects" / str(context.project_id))
    elif scope_level == ScopeLevel.RUNTIME:
        if not context.runtime_id or not context.session_id:
            raise ValueError("RUNTIME scopes requires runtime_id and session_id in context")
        return str(base_path_obj / context.runtime_id / f"worktree-{context.session_id}")
    elif scope_level == ScopeLevel.SESSION:
        if not context.project_id or not context.session_id:
            raise ValueError("SESSION scopes requires project_id and session_id in context")
        return str(
            base_path_obj / "projects" / str(context.project_id) / "sessions" /
            context.session_id
        )
    else:
        raise ValueError(f"Unknown scopes level: {scope_level}")


def load_scope_config(
    scope_level: str | ScopeLevel,
    context: ScopeContext,
    config_file: str = "scope_config.json",
) -> Dict[str, Any]:
    """Load scopes configuration from filesystem.

    Looks for a config file at the resolved scopes path. If not found,
    returns defaults and logs a warning.

    Configuration structure:
    {
        "scope_level": "session",
        "access_controls": {
            "users": ["user1", "user2"],
            "groups": ["analysts"],
            "roles": ["admin", "analyst"]
        },
        "permissions": {
            "findings": ["read", "create", "update"],
            "iocs": ["read", "create"],
            "artifacts": ["read"]
        },
        "retention": {
            "days": 30,
            "archive_after": 90
        },
        "tags": ["tag1", "tag2"]
    }

    Args:
        scope_level: Scope level
        context: ScopeContext with required fields
        config_file: Config filename (default: scope_config.json)

    Returns:
        Configuration dictionary (empty dict if not found)
    """
    if isinstance(scope_level, str):
        try:
            scope_level = ScopeLevel(scope_level)
        except ValueError:
            raise ValueError(f"Invalid scopes level: {scope_level}")

    try:
        scope_path = resolve_scope_path(scope_level, context)
        config_path = Path(scope_path) / config_file

        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
                logger.debug(f"Loaded scopes config from {config_path}")
                return config
        else:
            logger.warning(f"Scope config not found at {config_path}, using defaults")
            return _get_default_scope_config(scope_level, context)
    except Exception as exc:
        logger.error(f"Error loading scopes config: {exc}")
        return _get_default_scope_config(scope_level, context)


def _get_default_scope_config(
    scope_level: ScopeLevel,
    context: ScopeContext,
) -> Dict[str, Any]:
    """Get default configuration for a scopes level."""
    base_config = {
        "scope_level": scope_level.value,
        "access_controls": {
            "users": [context.user_id] if context.user_id else [],
            "groups": [],
            "roles": [context.user_role] if context.user_role else [],
        },
        "permissions": {
            "findings": [],
            "iocs": [],
            "artifacts": [],
        },
        "retention": {
            "days": 30,
            "archive_after": 90,
        },
        "tags": [],
        "created_at": datetime.utcnow().isoformat(),
    }

    # Set default permissions based on scopes level
    if scope_level in (ScopeLevel.GLOBAL, ScopeLevel.APP):
        base_config["permissions"] = {
            "findings": ["read", "create", "update", "delete"],
            "iocs": ["read", "create", "update", "delete"],
            "artifacts": ["read", "create", "update", "delete"],
        }
    elif scope_level == ScopeLevel.PROJECT:
        base_config["permissions"] = {
            "findings": ["read", "create", "update"],
            "iocs": ["read", "create", "update"],
            "artifacts": ["read", "create"],
        }
    elif scope_level in (ScopeLevel.RUNTIME, ScopeLevel.SESSION):
        base_config["permissions"] = {
            "findings": ["read", "create"],
            "iocs": ["read", "create"],
            "artifacts": ["read"],
        }

    return base_config


def check_scope_permission(
    user_id: str,
    scope: ScopeContext,
    action: str | ScopeAction,
    resource: str,
) -> bool:
    """Check if user has permission for an action on a resource within a scopes.

    Permission hierarchy:
        - Global scopes users can access all scopes
        - App scopes users can access app and lower scopes
        - Project scopes users can access their project and lower scopes
        - Runtime/Session scopes users can access only their scopes

    Args:
        user_id: User identifier
        scope: ScopeContext for the target resource
        action: Action to perform (read, create, update, delete, execute, export)
        resource: Resource type (findings, iocs, artifacts, etc.)

    Returns:
        True if user has permission, False otherwise
    """
    if isinstance(action, str):
        try:
            action = ScopeAction(action)
        except ValueError:
            logger.warning(f"Invalid action: {action}")
            return False

    # Load scopes configuration
    try:
        config = load_scope_config(scope.scope_level, scope)
    except Exception as exc:
        logger.error(f"Error loading scopes config for permission check: {exc}")
        return False

    # Check user access controls
    access_controls = config.get("access_controls", {})

    # Check if user is in allowed users list
    allowed_users = access_controls.get("users", [])
    if allowed_users and user_id not in allowed_users:
        # Allow if list is empty (no restriction)
        if allowed_users:
            logger.debug(f"User {user_id} not in allowed_users list for {scope.scope_level} scopes")
            return False

    # Check if user role is in allowed roles
    if scope.user_role:
        allowed_roles = access_controls.get("roles", [])
        if allowed_roles and scope.user_role not in allowed_roles:
            msg = (
                f"User role {scope.user_role} not in allowed_roles for "
                f"{scope.scope_level} scopes"
            )
            logger.debug(msg)
            return False

    # Check if action is permitted for resource
    permissions = config.get("permissions", {})
    resource_actions = permissions.get(resource, [])

    if action.value not in resource_actions:
        msg = (
            f"Action {action.value} not permitted for {resource} in "
            f"{scope.scope_level} scopes"
        )
        logger.debug(msg)
        return False

    msg = (
        f"Permission granted: {user_id} can {action.value} {resource} in "
        f"{scope.scope_level} scopes"
    )
    logger.debug(msg)
    return True


def check_scope_hierarchy(
    source_scope: ScopeContext,
    target_scope: ScopeContext,
) -> bool:
    """Check if target scopes is within source scopes hierarchy.

    Hierarchy (inclusive):
        GLOBAL > APP > PROJECT > RUNTIME > SESSION

    Args:
        source_scope: Higher scopes
        target_scope: Potentially lower scopes

    Returns:
        True if target_scope is within source_scope, False otherwise
    """
    scope_hierarchy = [
        ScopeLevel.GLOBAL,
        ScopeLevel.APP,
        ScopeLevel.PROJECT,
        ScopeLevel.RUNTIME,
        ScopeLevel.SESSION,
    ]

    source_idx = scope_hierarchy.index(source_scope.scope_level)
    target_idx = scope_hierarchy.index(target_scope.scope_level)

    if source_idx > target_idx:
        return False

    if source_scope.scope_level == ScopeLevel.GLOBAL:
        return True
    elif source_scope.scope_level == ScopeLevel.APP:
        return True
    elif source_scope.scope_level == ScopeLevel.PROJECT:
        return source_scope.project_id == target_scope.project_id
    elif source_scope.scope_level == ScopeLevel.RUNTIME:
        return (
            source_scope.runtime_id == target_scope.runtime_id
            and source_scope.session_id == target_scope.session_id
        )
    elif source_scope.scope_level == ScopeLevel.SESSION:
        return (
            source_scope.session_id == target_scope.session_id
            and source_scope.project_id == target_scope.project_id
        )

    return False


def validate_scope_fields(
    project_id: Optional[int] = None,
    session_id: Optional[str] = None,
    runtime_id: Optional[str] = None,
    worktree_path: Optional[str] = None,
    scope_level: str | ScopeLevel = "session",
) -> tuple[bool, Optional[str]]:
    """Validate scopes fields for model save operations.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if isinstance(scope_level, str):
        try:
            scope_level = ScopeLevel(scope_level)
        except ValueError:
            return False, f"Invalid scope_level: {scope_level}"

    # Validate based on scopes level
    if scope_level == ScopeLevel.GLOBAL:
        pass
    elif scope_level == ScopeLevel.APP:
        pass
    elif scope_level == ScopeLevel.PROJECT:
        if not project_id:
            return False, "PROJECT scopes requires project_id"
    elif scope_level == ScopeLevel.RUNTIME:
        if not runtime_id:
            return False, "RUNTIME scopes requires runtime_id"
        if not worktree_path:
            return False, "RUNTIME scopes requires worktree_path"
    elif scope_level == ScopeLevel.SESSION:
        if not session_id:
            return False, "SESSION scopes requires session_id"
        if not project_id:
            return False, "SESSION scopes requires project_id"

    return True, None


T = TypeVar("T")


def get_scoped_queryset(
    model_class: type[T],
    scope: ScopeContext,
) -> Any:
    """Build a queryset filtered by scopes.

    This is a helper for building filtered queries at different scopes levels.
    Should be used with async ORM queries like: await get_scoped_queryset(...).filter(...)

    Args:
        model_class: The scoped model class
        scope: ScopeContext with filtering parameters

    Returns:
        Filtered queryset (should be used with await)
    """
    queryset = model_class

    if scope.scope_level in (ScopeLevel.RUNTIME, ScopeLevel.SESSION):
        if scope.session_id:
            queryset = queryset.filter(session_id=scope.session_id)
    elif scope.scope_level in (ScopeLevel.PROJECT, ScopeLevel.APP):
        if scope.project_id:
            queryset = queryset.filter(project_id=scope.project_id)
    elif scope.scope_level == ScopeLevel.GLOBAL:
        pass

    if scope.runtime_id:
        queryset = queryset.filter(runtime_id=scope.runtime_id)

    return queryset
