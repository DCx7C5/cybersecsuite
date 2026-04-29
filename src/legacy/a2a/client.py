"""
A2A Client — send tasks to remote A2A agents over HTTP.
Supports both request/response and SSE streaming.
"""


import json
import uuid
from typing import Any, AsyncIterator, Dict, Optional

import httpx

from a2a.models import (
    AgentCard,
    JSONRPCRequest,
    JSONRPCResponse,
    Task,
    TaskSendParams,
    TaskQueryParams,
    TaskIdParams,
    Message,
    TextPart,
)
from a2a.enums import MessageRole, PartType


class A2AClientError(Exception):
    """Raised on A2A protocol or transport errors."""
    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data


class A2AClient:
    """
    Async HTTP client for communicating with A2A agents.

    Usage:
        async with A2AClient("https://agent.example.com") as client:
            card = await client.get_agent_card()
            task = await client.send_task("Hello, agent!")
            print(task.status.state)
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        ed25519_private_key_pem: Optional[bytes] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._extra_headers = headers or {}
        self._ed25519_key_pem = ed25519_private_key_pem
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "A2AClient":
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            headers=self._extra_headers,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()

    # ── Agent Card ────────────────────────────────────────────────────────────

    async def get_agent_card(self) -> AgentCard:
        """Fetch the remote agent's AgentCard."""
        resp = await self._get("/.well-known/agent.json")
        return AgentCard(**resp)

    # ── Task Operations ───────────────────────────────────────────────────────

    async def send_task(
        self,
        text: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Send a text message as a new task.

        Args:
            text: Message text to send
            task_id: Optional task ID (auto-generated if omitted)
            session_id: Optional session context
            metadata: Optional task metadata

        Returns:
            Completed Task with status and artifacts
        """
        params = TaskSendParams(
            id=task_id or str(uuid.uuid4()),
            session_id=session_id,
            message=Message(
                role=MessageRole.USER,
                parts=[TextPart(type=PartType.TEXT, text=text)],
            ),
            metadata=metadata,
        )
        result = await self._rpc("tasks/send", params.model_dump(mode="json", exclude_none=True))
        return Task(**result)

    async def send_task_with_message(
        self,
        message: Message,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Send a fully constructed message as a task."""
        params = TaskSendParams(
            id=task_id or str(uuid.uuid4()),
            session_id=session_id,
            message=message,
            metadata=metadata,
        )
        result = await self._rpc("tasks/send", params.model_dump(mode="json", exclude_none=True))
        return Task(**result)

    async def get_task(self, task_id: str, history_length: Optional[int] = None) -> Task:
        """Retrieve task status and artifacts."""
        params = TaskQueryParams(id=task_id, history_length=history_length)
        result = await self._rpc("tasks/get", params.model_dump(mode="json", exclude_none=True))
        return Task(**result)

    async def cancel_task(self, task_id: str) -> Task:
        """Cancel a running task."""
        params = TaskIdParams(id=task_id)
        result = await self._rpc("tasks/cancel", params.model_dump(mode="json", exclude_none=True))
        return Task(**result)

    # ── Streaming ─────────────────────────────────────────────────────────────

    async def stream_task(
        self,
        text: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AsyncIterator[Task]:
        """
        Stream task updates via SSE.

        First sends the task, then subscribes to the SSE stream.
        """
        task = await self.send_task(text, task_id=task_id, session_id=session_id)

        url = f"{self.base_url}/a2a/stream/{task.id}"
        async with httpx.AsyncClient(timeout=None) as stream_client:
            async with stream_client.stream("GET", url, headers=self._extra_headers) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        yield Task(**json.loads(data))

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    async def _rpc(self, method: str, params: Dict[str, Any]) -> Any:
        """Execute a JSON-RPC call and return the result."""
        payload = JSONRPCRequest(
            id=str(uuid.uuid4()),
            method=method,
            params=params,
        ).model_dump(mode="json", exclude_none=True)

        raw = await self._post("/a2a", payload)
        rpc_resp = JSONRPCResponse(**raw)

        if rpc_resp.error:
            raise A2AClientError(
                code=rpc_resp.error.code,
                message=rpc_resp.error.message,
                data=rpc_resp.error.data,
            )
        return rpc_resp.result

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        client = self._ensure_client()
        resp = await client.post(
            f"{self.base_url}{path}",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    async def _get(self, path: str) -> Dict[str, Any]:
        client = self._ensure_client()
        resp = await client.get(f"{self.base_url}{path}")
        resp.raise_for_status()
        return resp.json()

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Use A2AClient as async context manager: async with A2AClient(...)")
        return self._client

