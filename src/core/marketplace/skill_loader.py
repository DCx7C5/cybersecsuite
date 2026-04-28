"""Marketplace-aware skill loader — respects enabled toggle.

Wraps skill discovery to filter out disabled skills.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.marketplace.models import MarketplaceItem

log = logging.getLogger(__name__)


async def get_enabled_skills() -> list[MarketplaceItem]:
    """Get all enabled skills from the marketplace.
    
    Filters out skills with status='disabled'.
    
    Returns:
        List of enabled MarketplaceItem (kind='skill')
    """
    try:
        from core.marketplace.toggle import get_enabled_skills as query_enabled_skills
        
        # Query enabled skills from marketplace DB
        enabled_skills = await query_enabled_skills()
        
        log.info(f"Loaded {len(enabled_skills)} enabled skills")
        return enabled_skills
        
    except Exception as e:
        log.warning(f"Failed to load enabled skills: {e}")
        return []


async def filter_enabled_skills(skills: list[Any]) -> list[Any]:
    """Filter a list of skills to only enabled ones.
    
    Checks marketplace database for enabled status.
    
    Args:
        skills: List of skill objects (with name attribute)
        
    Returns:
        Filtered list with only enabled skills
    """
    try:
        from core.marketplace.toggle import get_enabled_skills as query_enabled_skills
        
        # Query enabled skills from marketplace DB
        enabled_skills_db = await query_enabled_skills()
        enabled_skill_names = {s.name for s in enabled_skills_db} if enabled_skills_db else set()
        
        # Filter skills
        if enabled_skill_names:
            filtered = [
                skill
                for skill in skills
                if getattr(skill, "name", skill.get("name", None) if isinstance(skill, dict) else None) in enabled_skill_names
            ]
        else:
            filtered = skills
        
        log.debug(f"Filtered {len(filtered)}/{len(skills)} skills to enabled")
        return filtered
        
    except Exception as e:
        log.warning(f"Failed to filter skills by enabled status: {e}; returning all")
        return skills


async def get_enabled_mcps() -> list[Any]:
    """Get all enabled MCPs from the marketplace.
    
    Filters out MCPs with status='disabled'.
    
    Returns:
        List of enabled MarketplaceMCP objects
    """
    try:
        from core.marketplace.toggle import get_enabled_mcps as query_enabled_mcps
        
        # Query enabled MCPs from marketplace DB
        enabled_mcps = await query_enabled_mcps()
        
        log.info(f"Loaded {len(enabled_mcps)} enabled MCPs")
        return enabled_mcps
        
    except Exception as e:
        log.warning(f"Failed to load enabled MCPs: {e}")
        return []
