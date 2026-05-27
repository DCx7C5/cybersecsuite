from css.core.prompt_cache.manager import PromptCacheManager, toggle_hash
from css.core.prompt_cache.types import CachingCapability
from css.core.settings.qol import QoLSettings, QoLToggle


class _DummyAdapter:
    @property
    def cache_capability(self) -> CachingCapability:
        return CachingCapability.EXACT_ONLY


def test_toggle_hash_order_independent() -> None:
    manager = PromptCacheManager(adapter=_DummyAdapter())
    messages = [{"role": "user", "content": "hello"}]

    settings_a = QoLSettings(
        enabled_toggles={QoLToggle.NO_CHAT, QoLToggle.NO_MARKDOWN},
        scope="session",
    )
    settings_b = QoLSettings(
        enabled_toggles={QoLToggle.NO_MARKDOWN, QoLToggle.NO_CHAT},
        scope="session",
    )

    key_a = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_a)
    key_b = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_b)

    assert key_a == key_b


def test_toggle_hash_returns_empty_for_none_or_empty_settings() -> None:
    empty_settings = QoLSettings(enabled_toggles=set(), scope="session")
    assert toggle_hash(None) == ""
    assert toggle_hash(empty_settings) == ""


def test_toggle_hash_empty_equals_default() -> None:
    manager = PromptCacheManager(adapter=_DummyAdapter())
    messages = [{"role": "user", "content": "hello"}]

    empty_settings = QoLSettings(enabled_toggles=set(), scope="session")
    key_default = manager.compute_exact_match_key(messages=messages, model="test-model")
    key_empty = manager.compute_exact_match_key(
        messages=messages,
        model="test-model",
        qol_settings=empty_settings,
    )

    assert key_default == key_empty


def test_toggle_hash_different_sets_produce_distinct_keys() -> None:
    manager = PromptCacheManager(adapter=_DummyAdapter())
    messages = [{"role": "user", "content": "hello"}]

    settings_a = QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session")
    settings_b = QoLSettings(enabled_toggles={QoLToggle.NO_THINKING}, scope="session")

    key_a = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_a)
    key_b = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_b)

    assert key_a != key_b


def test_toggle_hash_integration_with_fake_cache_backend() -> None:
    manager = PromptCacheManager(adapter=_DummyAdapter())
    messages = [{"role": "user", "content": "same visible prompt"}]

    settings_a = QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session")
    settings_b = QoLSettings(enabled_toggles={QoLToggle.NO_THINKING}, scope="session")

    key_a = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_a)
    key_b = manager.compute_exact_match_key(messages=messages, model="test-model", qol_settings=settings_b)

    fake_backend: dict[str, str] = {}
    fake_backend[key_a] = "cached-response-for-no-chat"

    assert fake_backend.get(key_a) == "cached-response-for-no-chat"
    assert fake_backend.get(key_b) is None
