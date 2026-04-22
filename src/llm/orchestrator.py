"""LLMOrchestrator — session-aware high-level API.

SID resolution order:
  1. Constructor ``sid`` argument
  2. ``GWT_SID`` environment variable
  3. ``CYBERSEC_SESSION_ID`` environment variable
  4. ``.worktree-session`` file walk (current dir → repo root)
  5. ``"global"`` fallback
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger("llm.orchestrator")

_instance: LLMOrchestrator | None = None


def resolve_sid(sid: str | None = None) -> str:
    """Resolve the active worktree SID from multiple sources."""
    if sid:
        return sid
    for env_key in ("GWT_SID", "CYBERSEC_SESSION_ID"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    # Walk up directory tree looking for .worktree-session marker
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        marker = parent / ".worktree-session"
        if marker.exists():
            text = marker.read_text().strip()
            if text:
                return text
    return "global"


class LLMOrchestrator:
    """Session-aware orchestrator wrapping AsyncLLMClient.

    Example::

        orc = LLMOrchestrator()
        async for chunk in await orc.chat([{"role": "user", "content": "Hello"}]):
            print(chunk, end="")
    """

    def __init__(
        self,
        default_model: str = "claude-sonnet-4-5",
        sid: str | None = None,
        log_prompts: bool = False,
    ) -> None:
        self.sid = resolve_sid(sid)
        self._model = default_model
        self._log_prompts = log_prompts
        log.debug("LLMOrchestrator init sid=%s model=%s", self.sid, self._model)

    def _make_client(self, model: str | None = None):
        from llm.client import AsyncLLMClient

        oo_index = None
        try:
            from openobserve.writer import bulk_index
            oo_index = bulk_index
        except Exception:
            pass

        return AsyncLLMClient(
            model=model or self._model,
            sid=self.sid,
            log_prompts=self._log_prompts,
            oo_index_fn=oo_index,
        )

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        **kwargs: Any,
    ):
        """Stream or complete a chat.

        Returns AsyncIterator[str] by default (stream=True).
        Returns anthropic.types.Message when stream=False.
        """
        return await self._make_client(model).chat(messages, **kwargs)

    async def structured(
        self,
        messages: list[dict],
        schema,
        model: str | None = None,
        **kwargs: Any,
    ):
        """Return a Pydantic model instance via Anthropic tool_use.

        ``schema`` must be a Pydantic ``BaseModel`` subclass.
        """
        from pydantic import BaseModel
        assert issubclass(schema, BaseModel), "schema must be a pydantic BaseModel"

        tool = {
            "name": "structured_output",
            "description": "Return a structured JSON response matching the schema",
            "input_schema": schema.model_json_schema(),
        }
        msg = await self._make_client(model).chat(
            messages,
            stream=False,
            tools=[tool],
            tool_choice={"type": "tool", "name": "structured_output"},
            **kwargs,
        )
        for block in msg.content:
            if block.type == "tool_use" and block.name == "structured_output":
                return schema.model_validate(block.input)
        raise ValueError("No structured_output tool block found in response")

    async def summarize(
        self,
        text: str,
        max_tokens: int = 256,
        model: str | None = None,
    ) -> str:
        """Single-turn summarisation helper."""
        messages = [{"role": "user", "content": f"Summarize concisely:\n\n{text}"}]
        parts: list[str] = []
        async for chunk in await self._make_client(model).chat(
            messages, max_tokens=max_tokens
        ):
            parts.append(chunk)
        return "".join(parts)


def get_orchestrator(**kwargs: Any) -> LLMOrchestrator:
    """Return the process-level singleton orchestrator (lazy init)."""
    global _instance
    if _instance is None:
        _instance = LLMOrchestrator(**kwargs)
    return _instance
