"""
Manager classes for Tortoise ORM models.

Pattern: Manager classes are co-located with their models in core/db/models/
but re-exported here for clean namespace and architectural clarity.

This follows the Tortoise ORM pattern where each model can define custom
manager methods without requiring separate manager files. Managers handle:
- Custom queries and filtering logic
- Cache invalidation
- Event hooks
- Business rule validation
"""

# Re-export managers from their co-located model files
from css.core.db.models.events import DomainEventRecordManager
from css.core.db.models.llm_models import LLMModelManager
from css.core.db.models.marketplace import (
    MarketplaceItemManager,
    MarketplaceMetaManager,
)
from css.core.db.models.menu import MenuItemManager
from css.core.db.models.orchestrator import OrchestratorInstanceManager
from css.core.db.models.permissions import (
    PermissionGrantManager,
    RolePermissionCacheManager,
    ScopeSessionManager,
)
from css.core.db.models.scope import (
    AppScopeManager,
    ProjectScopeManager,
    SessionScopeManager,
)
from css.core.db.models.team import TeamManager
from css.core.db.models.user import UserManager

__all__ = [
    "TeamManager",
    "UserManager",
    "OrchestratorInstanceManager",
    "PermissionGrantManager",
    "ScopeSessionManager",
    "RolePermissionCacheManager",
    "DomainEventRecordManager",
    "AppScopeManager",
    "ProjectScopeManager",
    "SessionScopeManager",
    "MenuItemManager",
    "MarketplaceMetaManager",
    "MarketplaceItemManager",
    "LLMModelManager",
]
