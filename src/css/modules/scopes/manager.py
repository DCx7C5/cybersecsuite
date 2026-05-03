"""Scope management and resolution."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .context import ScopeContext
from .enums import ScopeLevel, ScopeRestriction
from .exceptions import ScopeValidationError, ScopeResolutionError

logger = logging.getLogger(__name__)


class ScopeManager:
    """Manages scope hierarchy, resolution, and access control."""
    
    # Scope hierarchy: lower levels inherit from higher
    HIERARCHY = [
        ScopeLevel.GLOBAL,
        ScopeLevel.APP,
        ScopeLevel.PROJECT,
        ScopeLevel.RUNTIME,
        ScopeLevel.SESSION,
    ]
    
    def __init__(self, root_scope: ScopeContext = None):
        """Initialize scope manager."""
        self.root_scope = root_scope or ScopeContext(ScopeLevel.GLOBAL)
        self._scopes: Dict[str, ScopeContext] = {}
        self._restrictions: Dict[str, ScopeRestriction] = {}
    
    def create_scope(self, context: ScopeContext) -> str:
        """Create a new scope from context."""
        try:
            scope_id = self._generate_scope_id(context)
            self._scopes[scope_id] = context
            logger.info(f"Created scope: {scope_id}")
            return scope_id
        except Exception as e:
            logger.error(f"Failed to create scope: {e}")
            raise ScopeValidationError(str(e), scope_level=context.scope_level.value)
    
    def get_scope(self, scope_id: str) -> Optional[ScopeContext]:
        """Get scope by ID."""
        return self._scopes.get(scope_id)
    
    def resolve_scope_path(self, scope_id: str) -> List[ScopeContext]:
        """Resolve scope path from root to target scope (inheritance chain)."""
        try:
            target = self._scopes.get(scope_id)
            if not target:
                raise ScopeResolutionError(scope_id)
            
            path = [self.root_scope]
            
            # Build inheritance chain based on scope level
            current_level = self.HIERARCHY.index(target.scope_level)
            for level_idx in range(1, current_level + 1):
                # Find scope at this level with matching context
                matching = self._find_scope_at_level(self.HIERARCHY[level_idx], target)
                if matching:
                    path.append(matching)
            
            return path
        except Exception as e:
            logger.error(f"Scope resolution failed: {e}")
            raise ScopeResolutionError(scope_id)
    
    def can_access(self, scope_id: str, user_role: str = None) -> bool:
        """Check if scope access is allowed."""
        try:
            if scope_id not in self._scopes:
                return False
            
            restriction = self._restrictions.get(scope_id, ScopeRestriction.NONE)
            
            if restriction == ScopeRestriction.DENY:
                return False
            elif restriction == ScopeRestriction.REQUIRE_ROLE:
                return user_role is not None
            elif restriction == ScopeRestriction.REQUIRE_AUTH:
                return True  # Already authenticated if we get here
            
            return True
        except Exception as e:
            logger.warning(f"Access check failed: {e}")
            return False
    
    def set_restriction(self, scope_id: str, restriction: ScopeRestriction) -> None:
        """Set access restriction on a scope."""
        self._restrictions[scope_id] = restriction
        logger.debug(f"Set restriction on {scope_id}: {restriction.value}")
    
    def delete_scope(self, scope_id: str) -> bool:
        """Delete a scope."""
        if scope_id in self._scopes:
            del self._scopes[scope_id]
            self._restrictions.pop(scope_id, None)
            logger.info(f"Deleted scope: {scope_id}")
            return True
        return False
    
    def list_scopes(self, level: ScopeLevel = None) -> List[str]:
        """List all scope IDs, optionally filtered by level."""
        if level is None:
            return list(self._scopes.keys())
        
        return [
            scope_id for scope_id, ctx in self._scopes.items()
            if ctx.scope_level == level
        ]
    
    def _generate_scope_id(self, context: ScopeContext) -> str:
        """Generate unique scope ID from context."""
        parts = [context.scope_level.value]
        
        if context.project_id:
            parts.append(f"p{context.project_id}")
        if context.runtime_id:
            parts.append(f"r{context.runtime_id}")
        if context.session_id:
            parts.append(f"s{context.session_id}")
        
        timestamp = datetime.utcnow().isoformat().replace(":", "").replace(".", "")
        parts.append(timestamp)
        
        return ":".join(parts)
    
    def _find_scope_at_level(self, level: ScopeLevel, target: ScopeContext) -> Optional[ScopeContext]:
        """Find scope at given level that matches target context."""
        for scope in self._scopes.values():
            if scope.scope_level != level:
                continue
            
            # Match based on level
            if level == ScopeLevel.PROJECT and scope.project_id == target.project_id:
                return scope
            elif level == ScopeLevel.RUNTIME and scope.runtime_id == target.runtime_id:
                return scope
            elif level == ScopeLevel.SESSION and scope.session_id == target.session_id:
                return scope
        
        return None
