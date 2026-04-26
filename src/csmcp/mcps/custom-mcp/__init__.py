"""
Custom MCP bridge for CyberSecSuite externalized MCPs.

Provides integration layer for loading and accessing 6 external MCPs
(csscore, canvas, memory, template, playwright, dystopian-crypto)
as SDK-mode compatible tool handlers.
"""
from __future__ import annotations

from fastmcp import mcp
import importlib
from typing import Any

# Initialize MCP server for custom bridge
mcp_server = mcp()

# Externalized MCP modules to load
EXTERNAL_MCPS = [
    "csscore_mcp",
    "canvas_mcp",
    "memory_mcp",
    "template_mcp",
    "playwright_mcp",
    "dystopian_crypto_mcp",
]


def load_external_mcps() -> dict[str, Any]:
    """Dynamically load external MCP modules and extract tools."""
    loaded_mcps = {}
    
    for mcp_module_name in EXTERNAL_MCPS:
        try:
            module = importlib.import_module(mcp_module_name)
            loaded_mcps[mcp_module_name] = module
        except ImportError as e:
            print(f"Warning: Failed to load {mcp_module_name}: {e}")
    
    return loaded_mcps


@mcp_server.tool()
def list_external_mcps() -> dict[str, list[str]]:
    """List all available external MCPs and their tools.
    
    Returns:
        Dictionary mapping MCP names to available tools
    """
    mcps = load_external_mcps()
    result = {}
    
    for mcp_name, module in mcps.items():
        tools = []
        if hasattr(module, "ALL_TOOLS"):
            tools = [t.name for t in module.ALL_TOOLS]
        elif hasattr(module, "__all__"):
            tools = list(module.__all__)
        result[mcp_name] = tools
    
    return result


@mcp_server.tool()
def get_mcp_info(mcp_name: str) -> dict[str, Any]:
    """Get detailed information about a specific MCP.
    
    Args:
        mcp_name: Name of the MCP module (e.g., 'csscore_mcp')
        
    Returns:
        Dictionary with MCP metadata and available tools
    """
    try:
        module = importlib.import_module(mcp_name)
        
        info = {
            "name": mcp_name,
            "module": module.__name__,
            "version": getattr(module, "__version__", "unknown"),
            "description": module.__doc__ or "",
        }
        
        if hasattr(module, "ALL_TOOLS"):
            info["tools"] = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": getattr(t, "input_schema", {}),
                }
                for t in module.ALL_TOOLS
            ]
        
        return info
    except ImportError as e:
        return {"error": f"MCP not found: {mcp_name}", "details": str(e)}


@mcp_server.tool()
def health_check_mcps() -> dict[str, bool]:
    """Check health status of all external MCPs.
    
    Returns:
        Dictionary mapping MCP names to health status
    """
    mcps = load_external_mcps()
    health = {}
    
    for mcp_name in EXTERNAL_MCPS:
        health[mcp_name] = mcp_name in mcps
    
    return health


def main() -> None:
    """Entry point for custom MCP bridge."""
    mcp_server.run()


if __name__ == "__main__":
    main()
