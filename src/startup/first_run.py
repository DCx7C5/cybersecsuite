"""First-run setup and marketplace loader."""

import json
from pathlib import Path

_CYBERSECSUITE_DIR = Path.home() / ".cybersecsuite"
_MARKETPLACE: dict = {}
_IS_FIRST_RUN: bool = False


def is_first_run() -> bool:
    """Check if this is the first run (no .cybersecsuite directory exists)."""
    global _IS_FIRST_RUN
    return _IS_FIRST_RUN


def get_marketplace() -> dict:
    """Get loaded marketplace dict."""
    return _MARKETPLACE


async def first_run_setup() -> dict:
    """Check and initialize on first run. Returns dict with init status."""
    global _IS_FIRST_RUN, _MARKETPLACE

    base_dir = _CYBERSECSUITE_DIR
    is_first = not base_dir.exists()

    if is_first:
        _IS_FIRST_RUN = True
        base_dir.mkdir(parents=True, exist_ok=True)

        dirs = ["sessions", "templates", "cache", "logs"]
        for d in dirs:
            sub = base_dir / d
            sub.mkdir(exist_ok=True)

        market_file = base_dir / "marketplace.json"
        if not market_file.exists():
            _MARKETPLACE = {
                "providers": [],
                "skills": [],
                "agents": [],
            }
            market_file.write_text(json.dumps(_MARKETPLACE, indent=2))
    else:
        market_file = base_dir / "marketplace.json"
        if market_file.exists():
            try:
                _MARKETPLACE = json.loads(market_file.read_text())
            except Exception:
                _MARKETPLACE = {}

    try:
        from accounts.sync import sync_providers_to_db
        await sync_providers_to_db()
    except Exception:
        pass

    return {
        "is_first_run": is_first_run(),
        "marketplace": get_marketplace(),
        "cybersecsuite_dir": str(base_dir),
    }