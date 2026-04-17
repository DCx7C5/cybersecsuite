"""Tests for MCP server tools — cybersec + dystopian."""
import json
import pytest

from csmcp.cybersec import all_servers


class TestMcpServerTools:
    """Test MCP server initialization and tool registry."""

    def test_cybersec_server_registered(self):
        """Test that cybersec MCP server is registered."""
        servers = all_servers()
        assert "cybersec" in servers
        cybersec = servers["cybersec"]
        assert cybersec is not None

    def test_dystopian_server_registered(self):
        """Test that dystopian MCP server is registered."""
        servers = all_servers()
        assert "dystopian" in servers
        dystopian = servers["dystopian"]
        assert dystopian is not None

    def test_total_tools_count(self):
        """Test that we have 31+5=36 total tools."""
        from csmcp import allowed_tools
        tools = allowed_tools()
        # Should contain tool names like "mcp__cybersec__case_open", etc.
        assert len(tools) >= 36
        assert any("cybersec" in t for t in tools)
        assert any("dystopian" in t for t in tools)

    def test_tool_categories(self):
        """Test presence of main tool categories."""
        from csmcp import allowed_tools
        tools = allowed_tools()
        tools_str = " ".join(tools)

        # Cybersec categories
        assert "case_open" in tools_str or "case" in tools_str
        assert "finding" in tools_str or "ioc" in tools_str
        assert "proxy" in tools_str or "route" in tools_str

        # Crypto category
        assert "crypto" in tools_str.lower() or "sign" in tools_str.lower()


@pytest.mark.asyncio
async def test_case_open_tool_callable():
    """Test that case_open tool can be imported and is callable."""
    from csmcp.cybersec.cases import case_open
    assert callable(case_open)


@pytest.mark.asyncio
async def test_findings_tools_available():
    """Test that findings-related tools are available."""
    from csmcp.cybersec.findings import add_finding, query_findings
    assert callable(add_finding)
    assert callable(query_findings)


@pytest.mark.asyncio
async def test_crypto_tools_available():
    """Test that crypto tools are available."""
    from csmcp.dystopian import (
        crypto_generate_keypair,
        crypto_sign_artifact,
        crypto_verify_artifact,
    )
    assert callable(crypto_generate_keypair)
    assert callable(crypto_sign_artifact)
    assert callable(crypto_verify_artifact)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

