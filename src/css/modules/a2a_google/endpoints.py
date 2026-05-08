
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .enums import A2AErrorCode, TaskState
from .exceptions import A2AAgentError, A2ACommunicationError, PauseRequestError
from css.core.logger import getLogger
from .types import (
    A2ACommunicatorProtocol,
    AgentCardProtocol,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    TaskQueryParams,
    TaskSendParams,
)

log = getLogger(__name__)

# ── Module-level routers (discovered by core/endpoints/loader.py) ────────────

# App-scoped routes — mounted at /a2a_google/*
router = APIRouter(prefix="/a2a_google", tags=["a2a_google"])

# Root-level routes — mounted without prefix (e.g. /.well-known/agents.json)
root_router = APIRouter(tags=["a2a_google"])


# ── Dependency ───────────────────────────────────────────────────────────────

def _get_communicator(request: Request) -> A2ACommunicatorProtocol:
    """Read A2ACommunicator from app.state (set by init_a2a_endpoints)."""
    comm = getattr(request.app.state, "a2a_communicator", None)
    if comm is None:
        raise A2AAgentError(
            "A2A communicator not initialized — call init_a2a_endpoints(app, comm) at startup"
        )
    return comm


def _get_agent_card(request: Request) -> AgentCardProtocol | None:
    return getattr(request.app.state, "a2a_agent_card", None)


def _task_state_value(task: object) -> str | None:
    if isinstance(task, dict):
        status = task.get("status")
        if isinstance(status, dict):
            state = status.get("state")
            return state if isinstance(state, str) else None
        return None

    status = getattr(task, "status", None)
    if status is None:
        return None

    state = getattr(status, "state", None)
    if isinstance(state, TaskState):
        return state.value
    if isinstance(state, str):
        return state
    return None


def _set_task_canceled(task: object) -> None:
    if isinstance(task, dict):
        status = task.get("status")
        if isinstance(status, dict):
            status["state"] = TaskState.CANCELED.value
            return
        task["status"] = {"state": TaskState.CANCELED.value}
        return

    status = getattr(task, "status", None)
    if status is None:
        raise PauseRequestError("Task has no status and cannot be canceled")

    if isinstance(status, dict):
        status["state"] = TaskState.CANCELED.value
        return

    if hasattr(status, "state"):
        setattr(status, "state", TaskState.CANCELED)
        return

    raise PauseRequestError("Task status is not mutable and cannot be canceled")


def _serialize_payload(payload: object) -> dict[str, object]:
    if isinstance(payload, dict):
        return payload

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        data = model_dump()
        if isinstance(data, dict):
            return data
        raise A2ACommunicationError("Serialized payload is not a dictionary")

    payload_dict = getattr(payload, "__dict__", None)
    if isinstance(payload_dict, dict):
        return {str(key): value for key, value in payload_dict.items()}

    raise A2ACommunicationError(
        "Unsupported task payload type",
        context={"type": type(payload).__name__},
    )


# ── JSON-RPC dispatcher ──────────────────────────────────────────────────────

async def _dispatch(req: JSONRPCRequest, comm: A2ACommunicatorProtocol) -> JSONRPCResponse:
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
            code=A2AErrorCode.METHOD_NOT_FOUND,
            message=f"Method not found: {req.method}",
        ),
    )


async def _handle_tasks_create(req: JSONRPCRequest, comm: A2ACommunicatorProtocol) -> JSONRPCResponse:
    try:
        params = TaskSendParams.model_validate(req.params or {})
    except ValidationError as exc:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INVALID_PARAMS,
                message=f"Invalid parameters: {exc}",
            ),
        )
    try:
        task = await comm.create_task(
            task_id=params.id,
            message=params.message,
            session_id=params.session_id,
        )
        log.info("A2A task created: %s (session: %s)", params.id, params.session_id)
        return JSONRPCResponse(id=req.id, result=_serialize_payload(task))
    except (ValueError, TypeError, RuntimeError, AttributeError, A2ACommunicationError) as exc:
        log.exception("Error creating A2A task %s", params.id)
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INTERNAL_ERROR,
                message=f"Failed to create task: {exc}",
            ),
        )


async def _handle_tasks_get(req: JSONRPCRequest, comm: A2ACommunicatorProtocol) -> JSONRPCResponse:
    try:
        params = TaskQueryParams.model_validate(req.params or {})
    except ValidationError as exc:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INVALID_PARAMS,
                message=f"Invalid parameters: {exc}",
            ),
        )
    try:
        task = await comm.get_task(params.id)
        return JSONRPCResponse(id=req.id, result=_serialize_payload(task))
    except ValueError:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INVALID_REQUEST,
                message=f"Task not found: {params.id}",
            ),
        )
    except (TypeError, RuntimeError, AttributeError, A2ACommunicationError) as exc:
        log.exception("Error fetching A2A task %s", params.id)
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INTERNAL_ERROR,
                message=f"Failed to fetch task: {exc}",
            ),
        )


async def _handle_tasks_cancel(req: JSONRPCRequest, comm: A2ACommunicatorProtocol) -> JSONRPCResponse:
    try:
        params = TaskQueryParams.model_validate(req.params or {})
    except ValidationError as exc:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INVALID_PARAMS,
                message=f"Invalid parameters: {exc}",
            ),
        )

    try:
        task_id = params.id
        task = await comm.get_task(task_id)
        state = _task_state_value(task)
        if state in {TaskState.COMPLETED.value, TaskState.FAILED.value, TaskState.CANCELED.value}:
            return JSONRPCResponse(
                id=req.id,
                error=JSONRPCError(
                    code=A2AErrorCode.INVALID_REQUEST,
                    message=f"Cannot cancel task in state: {state}",
                ),
            )
        _set_task_canceled(task)
        log.info("A2A task canceled: %s", task_id)
        return JSONRPCResponse(id=req.id, result=_serialize_payload(task))
    except (ValueError, PauseRequestError) as exc:
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INVALID_REQUEST,
                message=str(exc),
            ),
        )
    except (TypeError, RuntimeError, AttributeError, A2ACommunicationError) as exc:
        log.exception("Error canceling A2A task")
        return JSONRPCResponse(
            id=req.id,
            error=JSONRPCError(
                code=A2AErrorCode.INTERNAL_ERROR,
                message=f"Failed to cancel task: {exc}",
            ),
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
    except ValueError:
        log.error("Invalid JSON in A2A request")
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": A2AErrorCode.PARSE_ERROR, "message": "Invalid JSON"},
                "id": None,
            },
        )

    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": A2AErrorCode.INVALID_REQUEST, "message": "Invalid JSON-RPC request"},
                "id": None,
            },
        )

    try:
        req = JSONRPCRequest.model_validate(body)
    except ValidationError:
        log.error("Invalid A2A JSON-RPC structure")
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": A2AErrorCode.INVALID_REQUEST, "message": "Invalid JSON-RPC request"},
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
    a2a_comm: A2ACommunicatorProtocol,
    agent_card: AgentCardProtocol | None = None,
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

