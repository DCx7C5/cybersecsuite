"""Toggle marketplace item enabled/disabled status.

Updates the database status field and triggers loader refresh.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


async def set_item_enabled(item_id: str, enabled: bool) -> dict[str, Any]:
    """Toggle an item's enabled/disabled status in the database.
    
    Args:
        item_id: Kebab-case item ID
        enabled: True to enable, False to disable
        
    Returns:
        {
            "success": bool,
            "item_id": str,
            "old_status": str,
            "new_status": str,
            "error": str or None,
        }
    """
    try:
        # Try to find and update the item in any marketplace table
        new_status = "available" if enabled else "disabled"
        old_status = None
        updated = False
        
        # Try each marketplace model
        from core.db.models.marketplace import (
            MarketplaceMCP,
            Skill,
            Agent,
            Plugin,
            Workflow,
            MarketplaceAsset,
        )
        
        # Try to find by name (since item_id might be a kebab-case name)
        for model_class in [MarketplaceMCP, Skill, Agent, Plugin, Workflow, MarketplaceAsset]:
            try:
                # Query by name or by a name_normalized field if available
                item = await model_class.get_or_none(name=item_id)
                if not item:
                    # Try kebab-case to title case conversion
                    title_case = " ".join(w.capitalize() for w in item_id.split("-"))
                    item = await model_class.get_or_none(name=title_case)
                
                if item:
                    old_status = item.status
                    item.status = new_status
                    await item.save()
                    updated = True
                    log.info(f"Toggled {model_class.__name__} {item_id}: {old_status} → {new_status}")
                    break
            except Exception as e:
                log.debug(f"Could not toggle {model_class.__name__}: {e}")
                continue
        
        if not updated:
            return {
                "success": False,
                "item_id": item_id,
                "old_status": None,
                "new_status": None,
                "error": f"Item not found: {item_id}",
            }
        
        return {
            "success": True,
            "item_id": item_id,
            "old_status": old_status,
            "new_status": new_status,
        }
        
    except Exception as e:
        log.exception(f"Failed to toggle item {item_id}: {e}")
        return {
            "success": False,
            "item_id": item_id,
            "old_status": None,
            "new_status": None,
            "error": str(e),
        }


async def get_enabled_agents() -> list[Any]:
    """Get all enabled agents from marketplace.
    
    Returns list of agents with status != 'disabled'.
    """
    try:
        from core.db.models.marketplace import Agent
        agents = await Agent.filter(status__not_exact="disabled")
        return agents
    except Exception as e:
        log.warning(f"Could not query enabled agents: {e}")
        return []


async def get_enabled_skills() -> list[Any]:
    """Get all enabled skills from marketplace.
    
    Returns list of skills with status != 'disabled'.
    """
    try:
        from core.db.models.marketplace import Skill
        skills = await Skill.filter(status__not_exact="disabled")
        return skills
    except Exception as e:
        log.warning(f"Could not query enabled skills: {e}")
        return []


async def get_enabled_mcps() -> list[Any]:
    """Get all enabled MCPs from marketplace.
    
    Returns list of MCPs with status != 'disabled'.
    """
    try:
        from core.db.models.marketplace import MarketplaceMCP
        mcps = await MarketplaceMCP.filter(status__not_exact="disabled")
        return mcps
    except Exception as e:
        log.warning(f"Could not query enabled MCPs: {e}")
        return []
