"""Custom Tortoise Managers for Ring 2 ORM models.

Each manager encapsulates common query patterns so endpoint and registry code
can call manager methods instead of repeating inline ``.filter()`` calls.

Usage::

    from css.core.db.models.managers import TeamManager

    teams = await TeamManager.active_teams()
    teams = await TeamManager.by_session(session_id=123)
"""

from css.core.db.models.marketplace import MarketplaceItem
from css.core.db.models.scope import ProjectScope
from css.core.db.models.team import Team

from .enums import TeamStatus


class TeamManager:
    """Query helpers for ``Team``."""

    @staticmethod
    async def active_teams():
        return await Team.filter(status=TeamStatus.ACTIVE).all()

    @staticmethod
    async def by_session(session_id: int):
        return await Team.filter(session_id=session_id).all()


class ToolModelManager:
    """Query helpers for ``HybridToolDefinition``."""

    @staticmethod
    async def by_provider(provider: str):
        from css.modules.tools.models import HybridToolDefinition
        return await HybridToolDefinition.filter(fallback_provider=provider).all()

    @staticmethod
    async def enabled():
        from css.modules.tools.models import HybridToolDefinition
        return await HybridToolDefinition.filter(enabled=True).all()


class MarketplaceItemManager:
    """Query helpers for ``MarketplaceItem``."""

    @staticmethod
    async def installed():
        return await MarketplaceItem.filter(installed_at__not_isnull=True).all()

    @staticmethod
    async def by_kind(kind):
        return await MarketplaceItem.filter(kind=kind).all()


class ScopeManager:
    """Query helpers for ``ProjectScope`` and ``SessionScope``."""

    @staticmethod
    async def active():
        return await ProjectScope.filter(is_active=True).all()

    @staticmethod
    async def by_project(project_id: int):
        return await ProjectScope.filter(project_id=project_id).all()
