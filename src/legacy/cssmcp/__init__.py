"""csmcp — cybersec in-process SDK MCP server with externalized MCP support.

Usage:
    from cssmcp import all_servers, allowed_tools, getLogger, load_external_mcps
    options = ClaudeAgentOptions(
        mcp_servers=all_servers(),
        allowed_tools=allowed_tools()
    )

SDK Mode Features:
    - Supports both in-process (local) MCPs and externalized (isolated) MCPs
    - Dynamically loads external MCPs from installed packages
    - Graceful degradation when external MCPs unavailable
    - Configuration via environment variables (SDK_MODE, EXTERNAL_MCPS)
"""
from __future__ import annotations

from legacy.logger import getLogger  # noqa: F401

import os
from typing import Any
import importlib


# SDK Mode Configuration
SDK_MODE = os.getenv("SDK_MODE", "hybrid").lower()  # hybrid, local, external
EXTERNAL_MCPS_ENABLED = os.getenv("EXTERNAL_MCPS_ENABLED", "true").lower() == "true"

# List of external MCPs that can be loaded
AVAILABLE_EXTERNAL_MCPS = [
    "csscore_mcp",
    "canvas_mcp", 
    "memory_mcp",
    "template_mcp",
    "playwright_mcp",
    "dystopian_crypto_mcp",
    "custom_mcp",
]


def load_external_mcps() -> dict[str, Any]:
    """Load external MCP servers from installed packages.
    
    Returns:
        Dictionary mapping MCP names to server instances.
        Empty if SDK_MODE is 'local' or EXTERNAL_MCPS_ENABLED is False.
        
    Raises:
        ImportError: If an external MCP fails to load in strict mode
    """
    if not EXTERNAL_MCPS_ENABLED or SDK_MODE == "local":
        return {}
    
    external_servers = {}
    strict_mode = SDK_MODE == "external"
    
    for mcp_module_name in AVAILABLE_EXTERNAL_MCPS:
        try:
            module = importlib.import_module(mcp_module_name)
            
            # Look for server instance or factory
            if hasattr(module, "mcp_server"):
                external_servers[mcp_module_name] = module.mcp_server
            elif hasattr(module, "server"):
                external_servers[mcp_module_name] = module.server
            else:
                getLogger(__name__).debug(f"No server found in {mcp_module_name}")
                
        except ImportError as e:
            msg = f"Failed to load external MCP {mcp_module_name}: {e}"
            if strict_mode:
                raise ImportError(msg) from e
            else:
                getLogger(__name__).warning(msg)
    
    return external_servers


def all_servers() -> dict[str, Any]:
    """Return all configured SDK MCP server instances keyed by server name.
    
    In hybrid mode (default), returns both local and external MCPs.
    In local mode, returns only built-in MCPs.
    In external mode, loads only external MCPs.
    
    Returns:
        Dictionary mapping server names to server instances
    """
    servers = {}
    
    # Always load local cybersec server unless in external-only mode
    if SDK_MODE != "external":
        from .cybersec import cybersec_server
        servers["cybersec"] = cybersec_server
    
    # Load external MCPs if enabled
    if SDK_MODE in ("hybrid", "external"):
        external = load_external_mcps()
        servers.update(external)
    
    return servers


def allowed_tools() -> list[str]:
    """Return all allowed tool names across all registered SDK MCP servers.
    
    Returns:
        List of tool names in format 'mcp__<server>__<tool_name>'
    """
    tools = []
    
    # Local cybersec tools (always included unless external-only mode)
    if SDK_MODE != "external":
        from .cybersec import _ALL_CYBERSEC_TOOLS
        tools.extend([
            f"mcp__cybersec__{t._sdk_tool_name}"
            for t in _ALL_CYBERSEC_TOOLS
            if getattr(t, "_sdk_tool_name", None)
        ])
    
    # External MCP tools
    if EXTERNAL_MCPS_ENABLED:
        external = load_external_mcps()
        for mcp_name, server in external.items():
            # Try to extract tools from external server
            if hasattr(server, "tools"):
                for tool_name in server.tools:
                    tools.append(f"mcp__{mcp_name}__{tool_name}")
    
    return tools


def get_sdk_mode() -> str:
    """Get current SDK mode configuration.
    
    Returns:
        Mode string: 'hybrid', 'local', or 'external'
    """
    return SDK_MODE


def get_external_mcps_status() -> dict[str, bool]:
    """Get status of each external MCP load attempt.
    
    Returns:
        Dictionary mapping MCP names to load status (True=loaded, False=failed)
    """
    status = {}
    external = load_external_mcps()
    
    for mcp_name in AVAILABLE_EXTERNAL_MCPS:
        status[mcp_name] = mcp_name in external
    
    return status
