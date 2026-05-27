from css.core.events import (
    configure_event_runtime,
    get_event_store,
    get_otel_bridge,
    shutdown_event_runtime,
)


def test_event_runtime_singletons_are_stable() -> None:
    shutdown_event_runtime()
    store_a, bridge_a, observer_a = configure_event_runtime()
    store_b, bridge_b, observer_b = configure_event_runtime()

    assert store_a is store_b is get_event_store()
    assert bridge_a is bridge_b is get_otel_bridge()
    assert observer_a is observer_b
    assert observer_a.event_store is store_a
    assert observer_a.otel_bridge is bridge_a


def test_shutdown_event_runtime_resets_instances() -> None:
    shutdown_event_runtime()
    store_a, bridge_a, observer_a = configure_event_runtime()
    shutdown_event_runtime()
    store_b, bridge_b, observer_b = configure_event_runtime()

    assert store_a is not store_b
    assert bridge_a is not bridge_b
    assert observer_a is not observer_b
