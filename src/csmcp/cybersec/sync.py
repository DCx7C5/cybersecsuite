"""Sync tools — reload pricing/provider config from disk and optional upstream sources."""
from __future__ import annotations

import os
import time
from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "sync_pricing",
    "Reload provider pricing and custom provider config from disk. Returns count of loaded providers.",
    {"config_path": {"type": "string", "nullable": True}},
)
async def sync_pricing(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import load_custom_providers
    except ImportError:
        return sdk_error("ai_proxy not available")

    config_path = args.get("config_path") or os.environ.get(
        "CYBERSEC_PROVIDERS_CONFIG",
        os.path.expanduser("~/.cybersecsuite/providers.yaml"),
    )

    t0 = time.perf_counter()
    try:
        count = load_custom_providers(config_path)
    except Exception as exc:
        return sdk_error(f"Failed to load providers from '{config_path}': {exc}")

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    return sdk_result({
        "status": "success",
        "config_path": config_path,
        "providers_loaded": count,
        "elapsed_ms": elapsed_ms,
    })


ALL_TOOLS = [sync_pricing]
