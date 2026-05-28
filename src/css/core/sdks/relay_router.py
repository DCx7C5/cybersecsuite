"""Provider-priority routing policy for browser relay fallback flows."""

from typing import Literal

import msgspec

RelayAttemptStatus = Literal["skipped", "failed", "success"]
RelayAttemptReason = Literal["unavailable", "call_error", "selected"]

DEFAULT_RELAY_PROVIDER_ORDER = [
    "github",
    "codex",
    "openai",
    "deepseek",
    "nvidia",
    "web_relay",
]


class RelayAttempt(msgspec.Struct, frozen=True, kw_only=True):
    """Outcome for one relay-provider slot attempt."""

    provider_id: str
    status: RelayAttemptStatus
    reason: RelayAttemptReason
    detail: str | None = None


class RelayProviderPolicy(msgspec.Struct, frozen=True, kw_only=True):
    """Ordered relay-provider policy with deterministic deduplication."""

    provider_order: list[str] = msgspec.field(default_factory=lambda: list(DEFAULT_RELAY_PROVIDER_ORDER))
    web_relay_provider_id: str = "web_relay"

    def ordered_providers(self) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for provider_id in self.provider_order:
            normalized = provider_id.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(normalized)
        if self.web_relay_provider_id not in seen:
            ordered.append(self.web_relay_provider_id)
        return ordered

    def is_web_relay_provider(self, provider_id: str) -> bool:
        return provider_id.strip().lower() == self.web_relay_provider_id

    @classmethod
    def from_order(
        cls,
        provider_order: list[str] | tuple[str, ...] | None,
    ) -> "RelayProviderPolicy":
        if provider_order is None:
            return cls()
        return cls(provider_order=list(provider_order))

