"""
A2A JSON-RPC server router (ASGI/Starlette-compatible).
Mounts at /a2a and serves:
  GET  /.well-known/agent.json  → AgentCard
  POST /a2a                     → JSON-RPC dispatch
  GET  /a2a/stream/{task_id}    → SSE streaming
"""


import json
import time
import uuid
from typing import Any, AsyncIterator, Dict, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route, Router

from a2a.agent import BaseA2AAgent
from a2a.enums import TaskState
from a2a.models import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    A2AErrorCodes,
    TaskSendParams,
    TaskQueryParams,
    TaskIdParams,
    TaskPushNotificationConfig,
    Message,
    TextPart,
)
from a2a.enums import MessageRole, PartType
from a2a.otel import (
    check_jsonrpc_baseline,
    check_task_baseline,
)


class A2AServer:
    """
    ASGI-compatible A2A JSON-RPC server.

    Usage:
        agent = MyCybersecAgent(card=...)
        server = A2AServer(agent)
        app.mount("/", server.router)
    """

    def __init__(self, agent: BaseA2AAgent) -> None:
        self.agent = agent
        self.router = Router(routes=[
            Route("/.well-known/agent.json", self._agent_card, methods=["GET"]),
            Route("/a2a", self._jsonrpc, methods=["POST"]),
            Route("/a2a/stream/{task_id}", self._sse_stream, methods=["GET"]),
        ])

    # ── Agent Card ────────────────────────────────────────────────────────────

    async def _agent_card(self, request: Request) -> JSONResponse:
        """Serve the AgentCard at /.well-known/agent.json."""
        return JSONResponse(self.agent.card.model_dump(mode="json", exclude_none=True))

    # ── JSON-RPC dispatch ─────────────────────────────────────────────────────

    async def _jsonrpc(self, request: Request) -> JSONResponse:
        """Dispatch JSON-RPC method calls."""
        start_ms = time.time() * 1000
        request_id = None
        
        try:
            body = await request.json()
        except Exception:
            return self._error_response(None, A2AErrorCodes.PARSE_ERROR, "Parse error")

        try:
            rpc = JSONRPCRequest(**body)
            request_id = rpc.id
        except Exception:
            return self._error_response(None, A2AErrorCodes.INVALID_REQUEST, "Invalid request")

        method = rpc.method
        params = rpc.params or {}

        handlers: Dict[str, Any] = {
            "tasks/send": self._handle_tasks_send,
            "tasks/get": self._handle_tasks_get,
            "tasks/cancel": self._handle_tasks_cancel,
            "tasks/pushNotification/set": self._handle_push_set,
            "tasks/pushNotification/get": self._handle_push_get,
            "tasks/resubscribe": self._handle_resubscribe,
        }

        handler = handlers.get(method)
        if handler is None:
            return self._error_response(
                rpc.id, A2AErrorCodes.METHOD_NOT_FOUND, f"Method not found: {method}"
            )

        try:
            result = await handler(params, request_id=request_id)  # type: ignore[operator]
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_jsonrpc_baseline(duration, method)
            return JSONResponse(
                JSONRPCResponse(id=rpc.id, result=result).model_dump(
                    mode="json", exclude_none=True
                )
            )
        except ValueError as e:
            return self._error_response(rpc.id, A2AErrorCodes.INVALID_PARAMS, str(e))
        except LookupError as e:
            return self._error_response(rpc.id, A2AErrorCodes.TASK_NOT_FOUND, str(e))
        except Exception as e:
            return self._error_response(rpc.id, A2AErrorCodes.INTERNAL_ERROR, str(e))

    # ── Method handlers ───────────────────────────────────────────────────────

    async def _handle_tasks_send(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/send — create and execute a task."""
        start_ms = time.time() * 1000
        try:
            send_params = TaskSendParams(**params)

            # Auto-generate ID if not provided
            if not send_params.id:
                send_params.id = str(uuid.uuid4())

            # Create task in store
            task = self.agent.store.create(send_params)

            # Mark as working
            self.agent.store.update_status(task.id, TaskState.WORKING)

            # Execute agent (non-streaming)
            await self.agent.execute(task, send_params.message)

            result_task = self.agent.store.get(task.id) or task
            
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "send")
            
            return result_task.model_dump(mode="json", exclude_none=True)
        except Exception:
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "send")
            raise

    async def _handle_tasks_get(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/get — retrieve task status."""
        start_ms = time.time() * 1000
        try:
            qp = TaskQueryParams(**params)
            task = self.agent.store.get(qp.id)
            if not task:
                raise LookupError(f"Task not found: {qp.id}")

            # Trim history if requested
            if qp.history_length is not None and task.history:
                task.history = task.history[-qp.history_length:]

            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "get")
            
            return task.model_dump(mode="json", exclude_none=True)
        except Exception:
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "get")
            raise

    async def _handle_tasks_cancel(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/cancel — cancel a task."""
        start_ms = time.time() * 1000
        try:
            ip = TaskIdParams(**params)
            task = self.agent.store.cancel(ip.id)
            if task is None:
                raise LookupError(f"Task not found or not cancelable: {ip.id}")
            
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "cancel")
            
            return task.model_dump(mode="json", exclude_none=True)
        except Exception:
            end_ms = time.time() * 1000
            duration = end_ms - start_ms
            check_task_baseline(duration, "cancel")
            raise

    async def _handle_push_set(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/pushNotification/set — register push notification URL."""
        cfg = TaskPushNotificationConfig(**params)
        task = self.agent.store.get(cfg.id)
        if not task:
            raise LookupError(f"Task not found: {cfg.id}")
        if task.metadata is None:
            task.metadata = {}
        task.metadata["push_notification"] = cfg.push_notification_config.model_dump(
            mode="json", exclude_none=True
        )
        return cfg.model_dump(mode="json", exclude_none=True)

    async def _handle_push_get(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/pushNotification/get — retrieve push notification config."""
        ip = TaskIdParams(**params)
        task = self.agent.store.get(ip.id)
        if not task:
            raise LookupError(f"Task not found: {ip.id}")
        push_cfg = (task.metadata or {}).get("push_notification")
        if not push_cfg:
            raise LookupError(f"No push notification config for task: {ip.id}")
        return {"id": ip.id, "push_notification_config": push_cfg}

    async def _handle_resubscribe(self, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """tasks/resubscribe — acknowledge resubscription."""
        ip = TaskIdParams(**params)
        task = self.agent.store.get(ip.id)
        if not task:
            raise LookupError(f"Task not found: {ip.id}")
        return task.model_dump(mode="json", exclude_none=True)

    # ── SSE Streaming ─────────────────────────────────────────────────────────

    async def _sse_stream(self, request: Request) -> StreamingResponse:
        """Stream task updates as Server-Sent Events."""
        start_ms = time.time() * 1000
        task_id = request.path_params["task_id"]
        task = self.agent.store.get(task_id)

        if not task:
            error_data = json.dumps({"error": f"Task not found: {task_id}"})

            async def _not_found() -> AsyncIterator[str]:
                yield f"data: {error_data}\n\n"

            return StreamingResponse(_not_found(), media_type="text/event-stream", status_code=404)

        message: Message
        if task.history:
            message = task.history[-1]
        else:
            message = Message(
                role=MessageRole.USER,
                parts=[TextPart(type=PartType.TEXT, text="")],
            )

        async def event_stream() -> AsyncIterator[str]:
            try:
                async for updated_task in self.agent.stream(task, message):  # type: ignore[arg-type]
                    data = json.dumps(
                        updated_task.model_dump(mode="json", exclude_none=True)
                    )
                    yield f"data: {data}\n\n"
                yield "data: [DONE]\n\n"
                
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                check_jsonrpc_baseline(duration, "sse.stream")
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                check_jsonrpc_baseline(duration, "sse.stream")
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _error_response(
        rpc_id: Optional[Any],
        code: int,
        message: str,
        data: Optional[Any] = None,
    ) -> JSONResponse:
        """Build a JSON-RPC error response."""
        resp = JSONRPCResponse(
            id=rpc_id,
            error=JSONRPCError(code=code, message=message, data=data),
        )
        return JSONResponse(resp.model_dump(mode="json", exclude_none=True))

