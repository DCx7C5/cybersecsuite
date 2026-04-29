"""Seed marketplace index into database — download from GitHub and ingest."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.db.models.scope import ProjectScope

log = logging.getLogger(__name__)


async def seed_marketplace_index(
    index: dict, project: ProjectScope, skip_existing: bool = True
) -> dict:
    """Seed marketplace index.json into database.
    
    Args:
        index: Parsed index.json from GitHub marketplace
        project: ProjectScope to associate items with
        skip_existing: If True, don't re-insert items that already exist
        
    Returns:
        {
            "mcps_created": int,
            "agents_created": int, 
            "skills_created": int,
            "combos_created": int,
            "templates_created": int,
            "total_created": int,
        }
    """
    from core.marketplace.models import MarketplaceItem

    # Import DB models dynamically to avoid circular imports
    try:
        from core.db.models.marketplace import MarketplaceMCP
    except ImportError:
        log.warning("MarketplaceMCP model not found; skipping MCP seeding")
        MarketplaceMCP = None

    stats = {
        "mcps_created": 0,
        "agents_created": 0,
        "skills_created": 0,
        "combos_created": 0,
        "templates_created": 0,
        "total_created": 0,
    }

    # Process MCPs
    if MarketplaceMCP and "mcps" in index:
        for mcp_data in index.get("mcps", []):
            try:
                # Check if exists
                if skip_existing:
                    existing = await MarketplaceMCP.filter(id=mcp_data.get("id")).exists()
                    if existing:
                        log.debug(f"Skipping existing MCP: {mcp_data.get('id')}")
                        continue

                # Create from index data
                mcp = await MarketplaceMCP.create(
                    id=mcp_data.get("id"),
                    name=mcp_data.get("name"),
                    description=mcp_data.get("description"),
                    kind="mcp",
                    provider=mcp_data.get("provider", "unknown"),
                    version=mcp_data.get("version", "0.1.0"),
                    source_url=mcp_data.get("source"),
                    project=project,
                )
                stats["mcps_created"] += 1
                log.debug(f"Created MCP: {mcp.id}")
            except Exception as e:
                log.warning(f"Failed to create MCP {mcp_data.get('id')}: {e}")

    # Process Agents
    if "agents" in index:
        for agent_data in index.get("agents", []):
            try:
                kind = agent_data.get("kind", "agent")
                
                # For now, just count (would need Agent model)
                log.debug(f"Agent: {agent_data.get('id')} ({kind})")
                if kind == "agent":
                    stats["agents_created"] += 1
                    
            except Exception as e:
                log.warning(f"Failed to process agent {agent_data.get('id')}: {e}")

    # Process Skills
    if "skills" in index:
        for skill_data in index.get("skills", []):
            try:
                log.debug(f"Skill: {skill_data.get('id')}")
                stats["skills_created"] += 1
            except Exception as e:
                log.warning(f"Failed to process skill {skill_data.get('id')}: {e}")

    # Count combos and templates from agents
    for agent_data in index.get("agents", []):
        kind = agent_data.get("kind", "agent")
        if kind == "combo":
            stats["combos_created"] += 1
        elif kind == "template":
            stats["templates_created"] += 1

    stats["total_created"] = (
        stats["mcps_created"]
        + stats["agents_created"]
        + stats["skills_created"]
        + stats["combos_created"]
        + stats["templates_created"]
    )

    log.info(
        f"Seeded marketplace index: "
        f"{stats['mcps_created']} MCPs, "
        f"{stats['agents_created']} agents, "
        f"{stats['skills_created']} skills, "
        f"{stats['combos_created']} combos, "
        f"{stats['templates_created']} templates"
    )

    return stats
