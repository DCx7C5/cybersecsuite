"""UnifiedLLMClient — routing-aware LLM completion client."""

from typing import Any

from css.core.resilience.routing.qwen_triage import QwenTriageRouter, qwen_triage_router as _triage_router_singleton
from css.core.resilience.routing.router import ComboRouter, combo_router as _combo_router_singleton


class UnifiedLLMClient:
    """Canonical provider-routing client for LLM execution."""

    def __init__(
        self,
        combo_router: ComboRouter | None = None,
        triage_router: QwenTriageRouter | None = None,
    ) -> None:
        self._combo_router = combo_router or _combo_router_singleton
        self._triage_router = triage_router or _triage_router_singleton

    async def complete(
        self,
        messages: list[dict[str, object]],
        combo_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        **kw: Any,
    ) -> Any:
        if combo_id is not None:
            return await self._combo_router.route(combo_id, messages, **kw)

        triage = self._triage_router.triage({"messages": messages})
        primary = triage.primary_provider
        if primary is None:
            raise RuntimeError("No primary provider selected by triage router")
        return await self._combo_router._call_target(primary, model or "", messages, kw)

    async def stream(
        self,
        messages: list[dict[str, object]],
        combo_id: str | None = None,
        **kw: Any,
    ) -> Any:
        if combo_id is not None:
            return await self._combo_router.route(combo_id, messages, **kw)
        triage = self._triage_router.triage({"messages": messages})
        primary = triage.primary_provider
        if primary is None:
            raise RuntimeError("No primary provider selected by triage router")
        return await self._combo_router._call_target(primary, "", messages, kw)

    async def routed_complete(
        self,
        messages: list[dict[str, object]],
        combo_id: str | None = None,
        **kw: Any,
    ) -> Any:
        return await self.complete(messages, combo_id=combo_id, **kw)
