import pytest

from css.core.events import get_event_store, shutdown_event_runtime
from css.core.events.instrument import instrument


def _reset_store() -> None:
    shutdown_event_runtime()
    get_event_store().clear()


@pytest.mark.asyncio
async def test_instrument_decorator_async_emits_correlated_events() -> None:
    _reset_store()

    @instrument("unit.async", source="test")
    async def run(value: int) -> int:
        return value + 1

    assert await run(1) == 2

    started = get_event_store().get_by_kind("unit.async.started")
    completed = get_event_store().get_by_kind("unit.async.completed")
    assert len(started) == 1
    assert len(completed) == 1
    assert started[0].metadata["correlation_id"] == completed[0].metadata["correlation_id"]
    assert completed[0].metadata["function"].endswith("run")
    assert completed[0].metadata["source"] == "test"


def test_instrument_decorator_sync_failure_emits_failed_event() -> None:
    _reset_store()

    @instrument("unit.sync", source="test")
    def fail() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        fail()

    started = get_event_store().get_by_kind("unit.sync.started")
    failed = get_event_store().get_by_kind("unit.sync.failed")
    assert len(started) == 1
    assert len(failed) == 1
    assert started[0].metadata["correlation_id"] == failed[0].metadata["correlation_id"]
    assert failed[0].metadata["error_type"] == "ValueError"


@pytest.mark.asyncio
async def test_instrument_context_manager_keeps_existing_usage() -> None:
    _reset_store()

    async with instrument("unit.ctx", source="test") as payload:
        payload["result"] = "ok"

    started = get_event_store().get_by_kind("unit.ctx.started")
    completed = get_event_store().get_by_kind("unit.ctx.completed")
    assert len(started) == 1
    assert len(completed) == 1
    assert started[0].metadata["correlation_id"] == completed[0].metadata["correlation_id"]
