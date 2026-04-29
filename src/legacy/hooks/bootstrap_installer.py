"""Bootstrap installer — downloads and installs core marketplace items on first setup."""

from __future__ import annotations

import logging
from typing import Optional

from hooks.bootstrap_status import BootstrapStatus
from hooks.sha512_checker import get_core_items

log = logging.getLogger(__name__)


async def bootstrap_install_core_items(
    index: dict,
    status: BootstrapStatus,
    max_retries: int = 3,
) -> dict:
    """Download and install core marketplace items during bootstrap.
    
    Returns:
        Summary: {"total": int, "installed": int, "failed": int, "failed_items": dict}
    """
    from marketplace.installer import PackageInstaller
    
    core_items = get_core_items(index)
    installer = PackageInstaller()
    
    total = len(core_items)
    installed = 0
    
    log.info(f"Bootstrap: installing {total} core marketplace items")
    status.advance_phase("downloading_items")
    
    for item in core_items:
        item_id = item.get("id")
        retries = 0
        
        while retries < max_retries:
            try:
                log.info(f"[{installed+1}/{total}] Installing {item_id}...")
                
                # Install via PackageInstaller
                result = await installer.install(
                    item_id=item_id,
                    source_url=item.get("source"),
                    item_type=item.get("type", "mcp"),
                )
                
                if result.get("success"):
                    status.record_installed(item_id)
                    installed += 1
                    log.info(f"✓ Installed {item_id}")
                    break
                else:
                    raise Exception(result.get("error", "Unknown installation error"))
                    
            except Exception as e:
                retries += 1
                error_msg = str(e)
                log.warning(f"[Retry {retries}/{max_retries}] Failed to install {item_id}: {error_msg}")
                
                if retries >= max_retries:
                    status.record_failed(item_id, error_msg)
                    log.error(f"✗ Failed to install {item_id} after {max_retries} retries")
                    break
    
    return {
        "total": total,
        "installed": installed,
        "failed": len(status.failed_items),
        "failed_items": status.failed_items,
    }


async def bootstrap_install_recommended_items(
    index: dict,
    user_choice: bool = False,
) -> dict:
    """Optionally download and install recommended marketplace items.
    
    Returns:
        Summary: {"total": int, "installed": int, "skipped": int}
    """
    from hooks.sha512_checker import get_recommended_items
    from marketplace.installer import PackageInstaller
    
    if not user_choice:
        log.debug("Bootstrap: skipping recommended items (user declined)")
        recommended_items = get_recommended_items(index)
        return {"total": len(recommended_items), "installed": 0, "skipped": len(recommended_items)}
    
    recommended_items = get_recommended_items(index)
    installer = PackageInstaller()
    
    total = len(recommended_items)
    installed = 0
    skipped = 0
    
    log.info(f"Bootstrap: installing {total} recommended marketplace items")
    
    for item in recommended_items:
        item_id = item.get("id")
        
        try:
            log.info(f"Installing recommended: {item_id}...")
            result = await installer.install(
                item_id=item_id,
                source_url=item.get("source"),
                item_type=item.get("type", "mcp"),
            )
            
            if result.get("success"):
                installed += 1
                log.info(f"✓ Installed {item_id}")
            else:
                skipped += 1
                log.warning(f"⊘ Skipped {item_id}: {result.get('error', 'unknown error')}")
                
        except Exception as e:
            skipped += 1
            log.warning(f"⊘ Skipped {item_id}: {e}")
    
    return {
        "total": total,
        "installed": installed,
        "skipped": skipped,
    }
