"""
Rate Limiter — async token-bucket implementation.

Enforces per-provider rate limits (RPM/TPM) and learns from upstream
x-ratelimit-* headers. Mirrors OmniRoute's rateLimitManager.ts.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _Bucket:
    """Token bucket with auto-refill."""
    capacity: float
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = field(default_factory=time.monotonic)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_acquire(self, cost: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def wait_time(self, cost: float = 1.0) -> float:
        self._refill()
        if self.tokens >= cost:
            return 0.0
        deficit = cost - self.tokens
        return deficit / self.refill_rate


@dataclass
class ProviderLimits:
    rpm: int = 60
    tpm: int = 1_000_000
    concurrent: int = 50


class RateLimiter:
    """Per-provider rate limiting with RPM and TPM buckets."""

    def __init__(self) -> None:
        self._rpm_buckets: dict[str, _Bucket] = {}
        self._tpm_buckets: dict[str, _Bucket] = {}
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._limits: dict[str, ProviderLimits] = {}

    def configure(self, provider_id: str, limits: ProviderLimits) -> None:
        self._limits[provider_id] = limits
        self._rpm_buckets[provider_id] = _Bucket(
            capacity=limits.rpm,
            tokens=limits.rpm,
            refill_rate=limits.rpm / 60.0,
        )
        self._tpm_buckets[provider_id] = _Bucket(
            capacity=limits.tpm,
            tokens=limits.tpm,
            refill_rate=limits.tpm / 60.0,
        )
        self._semaphores[provider_id] = asyncio.Semaphore(limits.concurrent)

    def _ensure_provider(self, provider_id: str) -> None:
        if provider_id not in self._rpm_buckets:
            self.configure(provider_id, ProviderLimits())

    async def acquire(self, provider_id: str, estimated_tokens: int = 1) -> bool:
        """Try to acquire rate limit tokens. Returns True if allowed."""
        self._ensure_provider(provider_id)

        # Check RPM
        rpm_bucket = self._rpm_buckets[provider_id]
        if not rpm_bucket.try_acquire(1.0):
            return False

        # Check TPM
        tpm_bucket = self._tpm_buckets[provider_id]
        if not tpm_bucket.try_acquire(float(estimated_tokens)):
            # Refund RPM token
            rpm_bucket.tokens = min(rpm_bucket.capacity, rpm_bucket.tokens + 1.0)
            return False

        return True

    async def wait_and_acquire(self, provider_id: str, estimated_tokens: int = 1) -> None:
        """Wait until rate limit allows, then acquire."""
        self._ensure_provider(provider_id)

        while True:
            if await self.acquire(provider_id, estimated_tokens):
                return

            rpm_wait = self._rpm_buckets[provider_id].wait_time(1.0)
            tpm_wait = self._tpm_buckets[provider_id].wait_time(float(estimated_tokens))
            wait = max(rpm_wait, tpm_wait, 0.1)
            await asyncio.sleep(min(wait, 5.0))

    def update_from_headers(self, provider_id: str, headers: dict[str, str]) -> None:
        """Learn rate limits from upstream response headers."""
        self._ensure_provider(provider_id)

        # Standard headers: x-ratelimit-limit-requests, x-ratelimit-remaining-requests
        remaining_rpm = headers.get("x-ratelimit-remaining-requests")
        if remaining_rpm is not None:
            try:
                self._rpm_buckets[provider_id].tokens = float(remaining_rpm)
            except ValueError:
                pass

        remaining_tpm = headers.get("x-ratelimit-remaining-tokens")
        if remaining_tpm is not None:
            try:
                self._tpm_buckets[provider_id].tokens = float(remaining_tpm)
            except ValueError:
                pass

        limit_rpm = headers.get("x-ratelimit-limit-requests")
        if limit_rpm is not None:
            try:
                new_rpm = int(limit_rpm)
                bucket = self._rpm_buckets[provider_id]
                bucket.capacity = new_rpm
                bucket.refill_rate = new_rpm / 60.0
            except ValueError:
                pass

    def get_status(self, provider_id: str) -> dict[str, Any]:
        """Return current rate limit status for a provider."""
        self._ensure_provider(provider_id)
        rpm = self._rpm_buckets[provider_id]
        tpm = self._tpm_buckets[provider_id]
        rpm._refill()
        tpm._refill()
        return {
            "provider_id": provider_id,
            "rpm_remaining": round(rpm.tokens, 1),
            "rpm_capacity": rpm.capacity,
            "tpm_remaining": round(tpm.tokens, 0),
            "tpm_capacity": tpm.capacity,
        }

    def get_all_status(self) -> list[dict[str, Any]]:
        return [self.get_status(pid) for pid in self._rpm_buckets]


# Global singleton
rate_limiter = RateLimiter()

