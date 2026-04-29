"""
A2A routing configuration for FastAPI.

Registers A2A JSON-RPC endpoints:
  - ``POST /a2a/rpc`` — JSON-RPC 2.0 A2A protocol handler
  - ``GET /.well-known/agent.json`` — Agent identity card

Usage:
    from fastapi import FastAPI
    from apps.a2a.a2a_comms import A2ACommunicator
    from apps.a2a.urls import init_a2a_routes

    app = FastAPI()
    comm = A2ACommunicator(agent_id="research:analyst", dispatcher=dispatcher)
    init_a2a_routes(app, comm, agent_card=agent_card)
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from a2a.models import AgentCard

from .endpoints import init_a2a_endpoints
from .a2a_comms import A2ACommunicator


async def get_agent_card_handler(card: AgentCard):
    """Serve agent identity at /.well-known/agent.json"""
    return JSONResponse(content=card.model_dump(mode="json"))


def init_a2a_routes(
    app: FastAPI,
    a2a_comm: A2ACommunicator,
    agent_card: AgentCard | None = None,
) -> None:
    """Initialize A2A protocol routes on a FastAPI app.

    Args:
        app: FastAPI application instance.
        a2a_comm: Initialized A2ACommunicator instance.
        agent_card: Optional AgentCard to serve at /.well-known/agent.json.

    Routes registered:
        - ``POST /a2a/rpc`` — JSON-RPC 2.0 A2A task API
        - ``GET /.well-known/agent.json`` — Agent identity (if card provided)
    """
    # Register JSON-RPC endpoint
    init_a2a_endpoints(app, a2a_comm)

    # Register agent card endpoint (optional)
    if agent_card:

        async def agent_card_route():
            return await get_agent_card_handler(agent_card)

        app.add_api_route(
            "/.well-known/agent.json",
            agent_card_route,
            methods=["GET"],
            tags=["a2a"],
            response_description="Agent identity descriptor (A2A protocol)",
        )