from __future__ import annotations

import logging
from enum import IntEnum
from typing import Any, Optional

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from css.modules.a2a.models import Message as A2AMessage, TaskStatus
from css.modules.internal_a2a.enums import TaskState
from css.modules.internal_a2a.types import AgentCard
from css.modules.internal_a2a.a2a_comms import A2ACommunicator

log = logging.getLogger(__name__)


# ── JSON-RPC 2.0 Types ───────────────────────────────────────────────────────

class A2AErrorCodes(IntEnum):
    """A2A-specific JSON-RPC error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error object."""
    code: int
    message: str
    data: Any | None = None


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request object."""
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] | None = None
    id: str | int | None = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response object."""
    jsonrpc: str = "2.0"
    result: dict[str, Any] | None = None
    error: JSONRPCError | None = None
    id: str | int | None = None


# ── A2A Protocol Parameter Types ─────────────────────────────────────────────

class TaskSendParams(BaseModel):
    """Parameters for tasks/create method."""
    id: str
    message: dict[str, Any] | A2AMessage
    session_id: str | None = None


class TaskQueryParams(BaseModel):
    """Parameters for tasks/get method."""
    id: str


# ── Module-level routers (discovered by core/endpoints/loader.py) ────────────

# App-scoped routes — mounted at /google_a2a/*
router = APIRouter(prefix="/google_a2a", tags=["google_a2a"])

# Root-level routes — mounted without prefix (e.g. /.well-known/agents.json)
root_router = APIRouter(tags=["google_a2a"])


# ── Dependency ───────────────────────────────────────────────────────────────

def _get_communicator(request: Request) -> A2ACommunicator:
    """Read A2ACommunicator from app.state (set by init_a2a_endpoints)."""
    comm: A2ACommunicator | None = getattr(request.app.state, "a2a_communicator", None)
    if comm is None:
        raise RuntimeError(
            "A2ACommunicator not initialized — call init_a2a_endpoints(app, comm) at startup"
        )
    return comm


def _get_agent_card(request: Request) -> AgentCard | None:
    return getattr(request.app.state, "a2a_agent_card", None)


# ── JSON-RPC dispatcher ──────────────────────────────────────────────────────

async def _dispatch(req: JSONRPCRequest, comm: A2ACommunicator) -> JSONRPCResponse:
    """Route a JSON-RPC 2.0 request to the appropriate handler."""
    if req.method == "tasks/create":
        return await _handle_tasks_create(req, comm)
    if req.method == "tasks/get":
        return await _handle_tasks_get(req, comm)
    if req.method == "tasks/cancel":
        return await _handle_tasks_cancel(req, comm)
    return JSONRPCResponse(
        id=req.id,
        error=JSONRPCError(
            code=A2AErrorCodes.METHOD_NOT_FOUND,
            message=f"Method not found: {req.method}",
        ),
    )


async def _handle_tasks_create(req: JSONRPCRequest, comm: A2ACommunicator) -> JSONRPCResponse:
    try:
        params = TaskSendParams(**(req.params or {}))
    except Exception as e:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INVALID_PARAMS, message=f"Invalid parameters: {e}"),
        )
    try:
        msg = params.message if isinstance(params.message, A2AMessage) else A2AMessage(**params.message)
        task = await comm.create_task(task_id=params.id, message=msg, session_id=params.session_id)
        log.info("A2A task created: %s (session: %s)", params.id, params.session_id)
        return JSONRPCResponse(id=req.id, result=task.model_dump())
    except Exception as e:
        log.exception("Error creating A2A task %s", params.id)
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INTERNAL_ERROR, message=f"Failed to create task: {e}"),
        )


async def _handle_tasks_get(req: JSONRPCRequest, comm: A2ACommunicator) -> JSONRPCResponse:
    try:
        params = TaskQueryParams(**(req.params or {}))
    except Exception as e:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INVALID_PARAMS, message=f"Invalid parameters: {e}"),
        )
    try:
        task = await comm.get_task(params.id)
        return JSONRPCResponse(id=req.id, result=task.model_dump())
    except ValueError:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INVALID_REQUEST, message=f"Task not found: {params.id}"),
        )
    except Exception as e:
        log.exception("Error fetching A2A task %s", params.id)
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INTERNAL_ERROR, message=f"Failed to fetch task: {e}"),
        )


async def _handle_tasks_cancel(req: JSONRPCRequest, comm: A2ACommunicator) -> JSONRPCResponse:
    try:
        task_id = (req.params or {}).get("id")
        if not task_id:
            raise ValueError("Missing required parameter: id")
        task = await comm.get_task(task_id)
        if task.status.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED):
            return JSONRPCResponse(
                id=req.id,
                error=JSONRPCError(
                    code=A2AErrorCodes.INVALID_REQUEST,
                    message=f"Cannot cancel task in state: {task.status.state}",
                ),
            )
        task.status = TaskStatus(state=TaskState.CANCELED)
        log.info("A2A task canceled: %s", task_id)
        return JSONRPCResponse(id=req.id, result=task.model_dump())
    except ValueError as e:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INVALID_REQUEST, message=str(e)),
        )
    except Exception as e:
        log.exception("Error canceling A2A task")
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(code=A2AErrorCodes.INTERNAL_ERROR, message=f"Failed to cancel task: {e}"),
        )


# ── Route handlers ───────────────────────────────────────────────────────────

@router.post("/rpc")
async def a2a_rpc_handler(request: Request) -> JSONResponse:
    """A2A JSON-RPC 2.0 endpoint.

    Accepts ``tasks/create``, ``tasks/get``, ``tasks/cancel`` methods.
    Communicator is read from ``request.app.state.a2a_communicator``.
    """
    try:
        body = await request.json()
    except Exception:
        log.error("Invalid JSON in A2A request")
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": A2AErrorCodes.PARSE_ERROR, "message": "Invalid JSON"}, "id": None},
        )
    try:
        req = JSONRPCRequest(**body)
    except Exception:
        log.error("Invalid A2A JSON-RPC structure")
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": A2AErrorCodes.INVALID_REQUEST, "message": "Invalid JSON-RPC request"},
                "id": body.get("id"),
            },
        )

    comm = _get_communicator(request)
    response = await _dispatch(req, comm)
    return JSONResponse(content=response.model_dump(exclude_none=True))


@root_router.get("/.well-known/agent.json")
async def agent_card_handler(request: Request) -> JSONResponse:
    """Serve the agents identity card (A2A discovery endpoint)."""
    card = _get_agent_card(request)
    if card is None:
        return JSONResponse(status_code=404, content={"detail": "No agents card configured"})
    return JSONResponse(content=card.model_dump(mode="json"))


# ── Initialization ───────────────────────────────────────────────────────────

def init_a2a_endpoints(
    app: FastAPI,
    a2a_comm: A2ACommunicator,
    agent_card: Optional[AgentCard] = None,
) -> None:
    """Store A2A dependencies on app.state.

    Call this once at startup after creating the FastAPI app and the
    communicator.  The ``router`` and ``root_router`` are mounted separately
    via ``mount_app_routers`` (or ``app.include_router``).

    Args:
        app:        FastAPI application instance.
        a2a_comm:   Initialized ``A2ACommunicator``.
        agent_card: Optional agents identity card for ``/.well-known/agents.json``.
    """
    app.state.a2a_communicator = a2a_comm
    if agent_card is not None:
        app.state.a2a_agent_card = agent_card
    log.info("A2A endpoints initialized (agent_id=%s)", a2a_comm.agent_id)



