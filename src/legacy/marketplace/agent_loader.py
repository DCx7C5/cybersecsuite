"""Marketplace-aware agent loader — respects enabled toggle.

Wraps core.google_a2a.agent_loader to filter out disabled agents.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.a2a.models import AgentCard

log = logging.getLogger(__name__)


async def get_enabled_agents(base_path: Optional[Path] = None) -> dict[str, AgentCard]:
    """Load agents that are enabled in the marketplace.
    
    Filters out agents with status='disabled' and agents not installed.
    
    Args:
        base_path: Optional path to agents directory (defaults to ~/.claude/agents)
        
    Returns:
        Dictionary of agent_id → AgentCard (enabled only)
    """
    try:
        from core.marketplace.toggle import get_enabled_agents as query_enabled_agents
        
        # Query enabled agents from marketplace DB
        enabled_agents_db = await query_enabled_agents()
        enabled_agent_ids = {a.name for a in enabled_agents_db} if enabled_agents_db else set()
        
        # Load from filesystem (existing loader)
        from core.a2a.agent_loader import load_agents_from_directory
        
        if base_path is None:
            base_path = Path.home() / ".claude" / "agents"
        
        all_agents = await load_agents_from_directory(base_path)
        
        # Filter to only enabled agents
        enabled = {
            agent_id: card
            for agent_id, card in all_agents.items()
            if not enabled_agent_ids or card.name in enabled_agent_ids
        }
        
        log.info(f"Loaded {len(enabled)}/{len(all_agents)} enabled agents")
        return enabled
        
    except Exception as e:
        log.warning(f"Failed to load enabled agents: {e}")
        return {}


async def filter_enabled_agents(agents: dict[str, AgentCard]) -> dict[str, AgentCard]:
    """Filter a dictionary of agents to only enabled ones.
    
    Checks marketplace database for enabled status.
    
    Args:
        agents: Dictionary of agent_id → AgentCard
        
    Returns:
        Filtered dictionary with only enabled agents
    """
    try:
        from core.marketplace.toggle import get_enabled_agents as query_enabled_agents
        
        # Query enabled agents from marketplace DB
        enabled_agents_db = await query_enabled_agents()
        enabled_agent_ids = {a.name for a in enabled_agents_db} if enabled_agents_db else set()
        
        # Filter agents
        filtered = {
            agent_id: card
            for agent_id, card in agents.items()
            if not enabled_agent_ids or card.name in enabled_agent_ids
        }
        
        log.debug(f"Filtered {len(filtered)}/{len(agents)} agents to enabled")
        return filtered
        
    except Exception as e:
        log.warning(f"Failed to filter agents by enabled status: {e}; returning all")
        return agents
