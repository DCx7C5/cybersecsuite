"""Route mounting helpers for a2a_google."""

from fastapi import FastAPI

from .endpoints import init_a2a_endpoints, root_router, router
from .types import A2ACommunicatorProtocol, AgentCardProtocol


def init_a2a_routes(
    app: FastAPI,
    a2a_comm: A2ACommunicatorProtocol,
    agent_card: AgentCardProtocol | None = None,
) -> None:
    """Initialize state and mount module routes."""
    init_a2a_endpoints(app=app, a2a_comm=a2a_comm, agent_card=agent_card)
    app.include_router(router)
    app.include_router(root_router)

