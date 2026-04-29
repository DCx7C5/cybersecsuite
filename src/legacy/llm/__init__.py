"""LLM orchestration layer — session-aware, OTEL-traced, cost-tracked.

Quick start::

    from llm import get_orchestrator

    orc = get_orchestrator()            # picks up GWT_SID automatically
    async for chunk in await orc.chat([{"role": "user", "content": "Hello"}]):
        print(chunk, end="")
"""
from llm.orchestrator import LLMOrchestrator, get_orchestrator, resolve_sid
from llm.client import AsyncLLMClient
from llm.pricing import cost_usd

__all__ = [
    "LLMOrchestrator",
    "AsyncLLMClient",
    "cost_usd",
    "get_orchestrator",
    "resolve_sid",
]
