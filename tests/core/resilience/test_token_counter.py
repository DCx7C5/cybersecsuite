"""Tests for routing token counter best-effort estimation."""

from css.core.resilience.routing import TokenCounter


def test_token_counter_estimates_for_openai_payload() -> None:
    count = TokenCounter().count(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hello world"}],
        provider_id="openai",
    )
    assert count is None or count >= 1


def test_token_counter_accepts_plain_string_messages() -> None:
    count = TokenCounter().count(
        model="gpt-4o-mini",
        messages="explain token estimation briefly",
        provider_id="openai",
    )
    assert count is None or count >= 1


def test_token_counter_returns_none_on_unserializable_payload() -> None:
    count = TokenCounter().count(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hello"}],
        tools={1, 2, 3},
        provider_id="openai",
    )
    assert count is None

