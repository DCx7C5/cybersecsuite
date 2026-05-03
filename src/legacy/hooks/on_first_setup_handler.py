"""OnFirstSetupEvent handler — refresh marketplace index on first setup."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hooks.events import OnFirstSetupEvent

log = logging.getLogger(__name__)


async def handle_on_first_setup_event(event: OnFirstSetupEvent) -> dict:
    """Handle OnFirstSetupEvent: download and seed marketplace index.
    
    Args:
        event: OnFirstSetupEvent with project_root, app_home, hostname, etc.
        
    Returns:
        {
            "status": "success" | "failed",
            "seed_result": dict (from seed_marketplace_index) or None,
            "error": str or None,
        }
    """
    from core.hooks.bootstrap_status import BootstrapStatus
    from core.hooks.sha512_checker import check_index_update
    from core.marketplace import seed_marketplace_index
    import json

    try:
        log.info(f"OnFirstSetupEvent: Bootstrap started (triggered by {event.get('triggered_by')})")
        
        # Get or create project scope for seeding
        try:
            from core.db.models.scope import ProjectScope
            # Use app_home as project identifier
            event.get("app_home", str(Path.home() / ".cybersecsuite"))
            project = await ProjectScope.get_or_create(
                name="default",
                defaults={"description": "Default project scope for marketplace items"}
            )
            project = project[0] if isinstance(project, tuple) else project
        except Exception as e:
            log.warning(f"Could not get/create ProjectScope: {e}; continuing without DB seeding")
            project = None
        
        # Check for marketplace index updates
        status = BootstrapStatus()
        status.advance_phase("checking_sha512")
        
        has_update, index_data = await check_index_update()
        
        if not has_update:
            log.info("Marketplace index is current; skipping update")
            return {
                "status": "success",
                "seed_result": None,
                "error": None,
            }
        
        # Parse index
        try:
            index = json.loads(index_data)
        except Exception as e:
            error_msg = f"Failed to parse index.json: {e}"
            log.error(error_msg)
            status.mark_failed(error_msg)
            return {
                "status": "failed",
                "seed_result": None,
                "error": error_msg,
            }
        
        # Seed into database (if project scope available)
        seed_result = None
        if project:
            status.advance_phase("seeding_db")
            try:
                seed_result = await seed_marketplace_index(index, project)
                log.info(f"Marketplace index seeded: {seed_result}")
            except Exception as e:
                error_msg = f"Failed to seed marketplace index: {e}"
                log.error(error_msg)
                status.mark_failed(error_msg)
                return {
                    "status": "failed",
                    "seed_result": seed_result,
                    "error": error_msg,
                }
        else:
            log.warning("Skipping database seeding (ProjectScope unavailable)")
        
        # Mark as complete
        status.mark_complete()
        log.info("OnFirstSetupEvent: Bootstrap completed successfully")
        
        return {
            "status": "success",
            "seed_result": seed_result,
            "error": None,
        }
        
    except Exception as e:
        error_msg = f"OnFirstSetupEvent handler failed: {e}"
        log.exception(error_msg)
        try:
            status.mark_failed(error_msg)
        except Exception:
            pass
        return {
            "status": "failed",
            "seed_result": None,
            "error": error_msg,
        }
