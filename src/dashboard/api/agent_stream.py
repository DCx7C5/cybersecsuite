"""Dashboard streaming chat API: task start, SSE stream, and cancel."""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from a2a.agent_sdk import run_agent_stream


def _ensure_stream_state(
    request: Request,
) -> tuple[dict[str, asyncio.Task[Any]], dict[str, asyncio.Queue[dict[str, Any]]]]:
    """Ensure app.state has stream task + queue registries."""
    state = request.app.state
    if not hasattr(state, "agent_stream_tasks"):
        state.agent_stream_tasks = {}
    if not hasattr(state, "agent_stream_queues"):
        state.agent_stream_queues = {}
    return state.agent_stream_tasks, state.agent_stream_queues


def _to_stream_flag(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().lower() not in {"0", "false", "no", "off"}
    return bool(raw)


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def _ttl_cleanup(app: Any, task_id: str, ttl_seconds: int = 30) -> None:
    """Cleanup finished stream tasks that were never consumed."""
    if not hasattr(app.state, "agent_stream_tasks"):
        return
    tasks = app.state.agent_stream_tasks
    queues = app.state.agent_stream_queues
    while True:
        await asyncio.sleep(1)
        task = tasks.get(task_id)
        if task is None:
            return
        if task.done():
            await asyncio.sleep(ttl_seconds)
            tasks.pop(task_id, None)
            queues.pop(task_id, None)
            return


async def api_agent_run_start(request: Request) -> JSONResponse:
    """POST /api/agent-run — start a streaming agent run."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "error": "invalid JSON body"}, status_code=400)

    agent_name = body.get("agent", "cybersec-agent")
    prompt = (body.get("prompt") or "").strip()
    stream = _to_stream_flag(body.get("stream", True))
    model_override = (body.get("model") or "").strip() or None

    if not prompt:
        return JSONResponse({"status": "error", "error": "prompt is required"}, status_code=400)

    tasks, queues = _ensure_stream_state(request)
    task_id = str(uuid.uuid4())
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    queues[task_id] = queue
    tasks[task_id] = asyncio.create_task(
        run_agent_stream(agent_name=agent_name, prompt=prompt, queue=queue, stream=stream, model=model_override)
    )
    asyncio.create_task(_ttl_cleanup(request.app, task_id, ttl_seconds=30))

    return JSONResponse({"task_id": task_id}, status_code=201)


async def sse_agent_run(request: Request) -> StreamingResponse:
    """GET /sse/agent-run/{task_id} — stream queue events via SSE."""
    task_id = request.path_params.get("task_id", "")
    tasks, queues = _ensure_stream_state(request)
    queue = queues.get(task_id)

    if queue is None:
        async def _not_found() -> Any:
            yield _sse("error", {"error": "task not found"})

        return StreamingResponse(
            _not_found(),
            media_type="text/event-stream",
            status_code=404,
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    async def _event_stream() -> Any:
        finished = False
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield _sse("error", {"error": "stream timeout"})
                    break

                event_type = event.get("type")
                if event_type == "token":
                    yield _sse("token", {"text": event.get("text", "")})
                    continue

                if event_type == "tool_start":
                    yield _sse(
                        "tool_start",
                        {
                            "name": event.get("name", "tool"),
                            "ts": int(event.get("ts", 0)),
                        },
                    )
                    continue

                if event_type == "tool_done":
                    yield _sse(
                        "tool_done",
                        {
                            "name": event.get("name", "tool"),
                            "elapsed_ms": int(event.get("elapsed_ms", 0)),
                        },
                    )
                    continue

                if event_type == "done":
                    payload: dict[str, Any] = {
                        "elapsed_ms": int(event.get("elapsed_ms", 0)),
                        "stop_reason": event.get("stop_reason", "end_turn"),
                    }
                    if "text" in event:
                        payload["text"] = event.get("text", "")
                    yield _sse("done", payload)
                    finished = True
                    break

                if event_type == "error":
                    yield _sse("error", {"error": event.get("error", "unknown error")})
                    finished = True
                    break
        finally:
            task = tasks.pop(task_id, None)
            queues.pop(task_id, None)
            if task is not None and not task.done() and not finished:
                task.cancel()

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def api_agent_run_cancel(request: Request) -> JSONResponse:
    """DELETE /api/agent-run/{task_id} — cancel an active run."""
    task_id = request.path_params.get("task_id", "")
    tasks, queues = _ensure_stream_state(request)
    task = tasks.pop(task_id, None)
    queue = queues.pop(task_id, None)

    cancelled = task is not None or queue is not None
    if task is not None and not task.done():
        task.cancel()
    if queue is not None:
        try:
            queue.put_nowait({"type": "error", "error": "cancelled"})
        except Exception:
            pass

    return JSONResponse({"cancelled": cancelled})
