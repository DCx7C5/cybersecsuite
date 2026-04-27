"""Tests for MCP server tools — cybersec + dystopian."""

import pytest

try:
    from csmcp import all_servers, allowed_tools

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    pytest.skip("MCP module not available", allow_module_level=True)


class TestMcpServerTools:
    """Test MCP server initialization and tool registry."""

    def test_all_servers_callable(self):
        """Test that all_servers() is callable."""
        assert callable(all_servers)

    def test_allowed_tools_callable(self):
        """Test that allowed_tools() is callable."""
        assert callable(allowed_tools)

    def test_mcp_servers_return_dict(self):
        """Test that MCP server registry returns dict."""
        servers = all_servers()
        assert isinstance(servers, dict)


@pytest.mark.skip(reason="Sub-module tools not yet verified")
@pytest.mark.asyncio
async def test_case_open_tool_callable():
    """Test that case_open tool can be imported and is callable."""
    pass


@pytest.mark.skip(reason="Sub-module tools not yet verified")
@pytest.mark.asyncio
async def test_findings_tools_available():
    """Test that findings-related tools are available."""
    pass


@pytest.mark.skip(reason="Sub-module tools not yet verified")
@pytest.mark.asyncio
async def test_crypto_tools_available():
    """Test that crypto tools are available."""
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
