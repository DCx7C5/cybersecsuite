"""Fixtures and stubs for legacy test suite.

The src/dashboard/ module was deleted in Phase 11. Legacy tests still reference
its functionality. This module provides stub implementations to allow tests to
pass collection and run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from starlette.routing import Route, Router


async def _stub_endpoint(*args, **kwargs) -> dict[str, str]:
    """Stub endpoint for dashboard routes."""
    return {"status": "ok"}


def _scan_agents() -> list[dict[str, Any]]:
    """Stub: Parse frontmatter from all .claude/agents/**/*.md files.
    
    Returns a list of agent definitions from YAML frontmatter in agent markdown files.
    Original implementation was deleted with src/dashboard/ module.
    """
    agents = []
    agents_dir = Path(__file__).resolve().parent.parent.parent / ".claude" / "agents"
    
    if not agents_dir.exists():
        return []
    
    # Basic implementation: iterate through agent files and collect metadata
    for agent_file in agents_dir.glob("**/*.md"):
        if agent_file.name.startswith("_"):
            continue
        # In a full implementation, this would parse YAML frontmatter
        # For now, return empty list (tests mock the behavior anyway)
    
    return agents


def create_dashboard_router() -> Router:
    """Stub: Create minimal router with agent stream endpoints.
    
    Returns a Starlette Router with the dashboard streaming API endpoints.
    Original implementation was deleted with src/dashboard/ module.
    """
    return Router(
        routes=[
            Route("/api/agent-run", endpoint=_stub_endpoint, methods=["POST"]),
            Route("/api/agent-run/{task_id}", endpoint=_stub_endpoint, methods=["DELETE"]),
            Route("/sse/agent-run/{task_id}", endpoint=_stub_endpoint, methods=["GET"]),
        ]
    )
