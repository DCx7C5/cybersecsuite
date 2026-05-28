"""Permission checker — gate tool access via ScopeContext / PermissionGrant rules."""


from typing import Protocol, runtime_checkable

from css.core.logger import getLogger
from .enums import PathOp
from .types import ScopeContext
from .exceptions import PermissionDenied

logger = getLogger(__name__)


@runtime_checkable
class PermissionPolicyContract(Protocol):
    """Runtime contract for policy objects consumed by PermissionChecker."""

    def has_tool_permission(self, tool_id: str) -> bool:
        ...

    def has_permission(self, permission: PathOp) -> bool:
        ...


class PermissionChecker:
    """Stateless helper that enforces permission rules for tool access.

    All methods are synchronous and take a ``ScopeContext`` as their source of
    truth.  The checker never mutates state — it only reads.

    Usage::

        checker = PermissionChecker()
        checker.require_tool(scope, "openai:code_interpreter")   # raises on deny
        ok = checker.can_tool(scope, "anthropic:computer_use")   # returns bool
    """

    def can_tool(self, scope: ScopeContext, tool_id: str) -> bool:
        """Return True when *tool_id* is allowed in *scope*, False otherwise."""
        policy_for_scope = getattr(scope.role, "policy_for_scope", None)
        if callable(policy_for_scope):
            policy = policy_for_scope(scope.scope_level)
        else:
            # Role has no policy_for_scope — fall back to checking the policy
            # attached directly to the ScopeContext (PermissionPolicy may be in
            # scope.role.policies dict keyed by scope_level).
            policy = getattr(scope.role, "policies", {}).get(scope.scope_level)

        if policy is None:
            logger.debug("No policy for %s at %s — deny", tool_id, scope.scope_level)
            return False
        if not isinstance(policy, PermissionPolicyContract):
            logger.debug("Policy object for %s does not satisfy checker contract", scope.scope_level)
            return False

        allowed = policy.has_tool_permission(tool_id)
        logger.debug("can_tool(%s, %s) → %s", tool_id, scope.scope_level, allowed)
        return allowed

    def require_tool(self, scope: ScopeContext, tool_id: str) -> None:
        """Raise :exc:`PermissionDenied` if *tool_id* is not allowed in *scope*.

        Args:
            scope: Current operation scope context.
            tool_id: Tool identifier in ``provider:name`` format.

        Raises:
            PermissionDenied: When the role/scope lacks permission for the tool.
        """
        if not self.can_tool(scope, tool_id):
            raise PermissionDenied(
                f"Tool '{tool_id}' not permitted for role "
                f"'{scope.role.role_id}' at scope '{scope.scope_level}'"
            )

    def can_path(self, scope: ScopeContext, permission: PathOp) -> bool:
        """Return True when *permission* is granted in *scope*, False otherwise."""
        policy_for_scope = getattr(scope.role, "policy_for_scope", None)
        if callable(policy_for_scope):
            policy = policy_for_scope(scope.scope_level)
        else:
            policy = getattr(scope.role, "policies", {}).get(scope.scope_level)

        if policy is None or not isinstance(policy, PermissionPolicyContract):
            return False
        return policy.has_permission(permission)

    def require_path(self, scope: ScopeContext, permission: PathOp) -> None:
        """Raise :exc:`PermissionDenied` if *permission* is not granted in *scope*.

        Args:
            scope: Current operation scope context.
            permission: Path-level permission enum value.

        Raises:
            PermissionDenied: When the role/scope lacks the path permission.
        """
        if not self.can_path(scope, permission):
            raise PermissionDenied(
                f"Permission '{permission}' not granted for role "
                f"'{scope.role.role_id}' at scope '{scope.scope_level}'"
            )


# Module-level singleton — imported by tools executor and agent executor.
permission_checker = PermissionChecker()

