"""Token-bucket rate limiter per provider (RPM / TPM / concurrency)."""

import asyncio
from time import time

import msgspec


class ProviderLimits(msgspec.Struct, frozen=True, kw_only=True):
    rpm: int = 60
    tpm: int = 60000
    concurrent: int = 2


class _Bucket:
    __slots__ = ("capacity", "tokens", "refill_rate", "updated_at")

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = float(capacity)
        self.tokens = self.capacity
        self.refill_rate = refill_rate
        self.updated_at = time()

    def _refill(self) -> None:
        now = time()
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.updated_at = now

    def try_consume(self, amount: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

    def wait_seconds(self, amount: float = 1.0) -> float:
        self._refill()
        if self.tokens >= amount:
            return 0.0
        deficit = amount - self.tokens
        return deficit / self.refill_rate if self.refill_rate > 0 else float("inf")


class RateLimiter:
    """Provider-wide rate limiter using token-bucket RPM and TPM."""

    def __init__(self) -> None:
        self._limits: dict[str, ProviderLimits] = {}
        self._rpm_buckets: dict[str, _Bucket] = {}
        self._tpm_buckets: dict[str, _Bucket] = {}
        self._concurrent: dict[str, int] = {}

    def configure(self, provider_id: str, limits: ProviderLimits) -> None:
        self._limits[provider_id] = limits
        self._rpm_buckets[provider_id] = _Bucket(limits.rpm, limits.rpm / 60.0)
        self._tpm_buckets[provider_id] = _Bucket(limits.tpm, limits.tpm / 60.0)
        self._concurrent.setdefault(provider_id, 0)

    def acquire(self, provider_id: str, estimated_tokens: int = 0) -> bool:
        limits = self._limits.get(provider_id)
        if limits is None:
            return True

        rpm_bucket = self._rpm_buckets.get(provider_id)
        tpm_bucket = self._tpm_buckets.get(provider_id)
        if rpm_bucket is None or tpm_bucket is None:
            return True

        if not rpm_bucket.try_consume():
            return False

        if estimated_tokens > 0 and not tpm_bucket.try_consume(float(estimated_tokens)):
            return False

        if self._concurrent.get(provider_id, 0) >= limits.concurrent:
            return False

        self._concurrent[provider_id] = self._concurrent.get(provider_id, 0) + 1
        return True

    async def wait_and_acquire(
        self,
        provider_id: str,
        estimated_tokens: int = 0,
        max_wait: float = 10.0,
    ) -> bool:
        limits = self._limits.get(provider_id)
        if limits is None:
            return True

        deadline = time() + max_wait
        while time() < deadline:
            if self.acquire(provider_id, estimated_tokens):
                return True

            rpm_bucket = self._rpm_buckets.get(provider_id)
            tpm_bucket = self._tpm_buckets.get(provider_id)
            wait = 0.0
            if rpm_bucket is not None:
                wait = max(wait, rpm_bucket.wait_seconds())
            if tpm_bucket is not None and estimated_tokens > 0:
                wait = max(wait, tpm_bucket.wait_seconds(float(estimated_tokens)))
            if wait <= 0:
                wait = 0.05

            remaining = deadline - time()
            await asyncio.sleep(min(wait, remaining))

        return False

    def release(self, provider_id: str) -> None:
        current = self._concurrent.get(provider_id, 0)
        if current > 0:
            self._concurrent[provider_id] = current - 1

    def update_from_headers(self, provider_id: str, headers: dict[str, str]) -> None:
        rpm_remaining = headers.get("x-ratelimit-remaining-requests")
        tpm_remaining = headers.get("x-ratelimit-remaining-tokens")
        rpm_bucket = self._rpm_buckets.get(provider_id)
        tpm_bucket = self._tpm_buckets.get(provider_id)

        if rpm_remaining is not None and rpm_bucket is not None:
            try:
                rpm_bucket.tokens = min(rpm_bucket.capacity, float(rpm_remaining))
                rpm_bucket.updated_at = time()
            except (ValueError, TypeError):
                pass

        if tpm_remaining is not None and tpm_bucket is not None:
            try:
                tpm_bucket.tokens = min(tpm_bucket.capacity, float(tpm_remaining))
                tpm_bucket.updated_at = time()
            except (ValueError, TypeError):
                pass

    def get_status(self) -> dict[str, dict[str, float | int | bool]]:
        result: dict[str, dict[str, float | int | bool]] = {}
        for provider_id in self._limits:
            rpm_bucket = self._rpm_buckets.get(provider_id)
            tpm_bucket = self._tpm_buckets.get(provider_id)
            result[provider_id] = {
                "rpm_remaining": rpm_bucket.tokens if rpm_bucket else 0,
                "tpm_remaining": tpm_bucket.tokens if tpm_bucket else 0,
                "concurrent": self._concurrent.get(provider_id, 0),
                "configured_concurrent": self._limits[provider_id].concurrent,
            }
        return result


rate_limiter: RateLimiter = RateLimiter()
