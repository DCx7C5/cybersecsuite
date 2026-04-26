"""
Cost Estimator — pre-request token estimation and cost tracking with headers.

Implements:
- Token estimation before request via tokenizer
- Cost calculation: tokens * model_rate[tier]
- Response headers: X-Tier-Cost, X-Tier-Speed
- Redis-based cost tracking per session/user
- Budget enforcement and threshold warnings
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import redis.asyncio as aioredis

from ai_proxy.services.token_counter import token_counter

logger = logging.getLogger("ai_proxy.autopilot.cost_estimator")


@dataclass
class CostEstimate:
    """Pre-request cost estimate."""
    model: str = ""
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    total_estimated_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0


@dataclass
class CostResult:
    """Post-request cost result."""
    request_id: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    latency_ms: float = 0.0
    headers: dict[str, str] = field(default_factory=dict)


# Model cost rates per 1M tokens (USD)
MODEL_COSTS = {
    # Claude Sonnet (Tier 2 - Execution)
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
    # Claude Haiku (Tier 0 - Triage)
    "claude-3-haiku-20240307": {"input": 0.8, "output": 4.0},
    # Claude Opus (Tier 3 - Complex)
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    # Qwen (Tier 1 - Fast)
    "qwen-max": {"input": 0.5, "output": 1.5},
    "qwen-turbo": {"input": 0.2, "output": 0.6},
    # Ollama (Tier 0 - Free)
    "ollama-local": {"input": 0.0, "output": 0.0},
    # Default rates
    "default": {"input": 1.0, "output": 3.0},
}


class CostEstimator:
    """Estimate and track request costs."""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        enable_redis_tracking: bool = True,
    ) -> None:
        """
        Initialize cost estimator.

        Args:
            redis_url: Redis connection URL (from env if not provided)
            enable_redis_tracking: Enable Redis-based cost tracking
        """
        self.redis_url = redis_url or os.environ.get("CYBERSEC_REDIS_URL", "redis://localhost:6379/0")
        self.enable_redis_tracking = enable_redis_tracking
        self._redis: Optional[aioredis.Redis] = None
        self._estimate_cache: dict[str, CostEstimate] = {}

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Get or create Redis client."""
        if not self.enable_redis_tracking:
            return None

        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
                logger.info("Connected to Redis for cost tracking")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.enable_redis_tracking = False
                return None

        return self._redis

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _get_model_cost(self, model: str) -> dict[str, float]:
        """Get cost rates for model."""
        # Exact match
        if model in MODEL_COSTS:
            return MODEL_COSTS[model]

        # Pattern match
        for key, cost in MODEL_COSTS.items():
            if key in model or model in key:
                return cost

        logger.warning(f"Model {model} not found in cost table, using defaults")
        return MODEL_COSTS["default"]

    async def estimate_cost(
        self,
        model: str,
        messages: list[dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> CostEstimate:
        """
        Estimate request cost before sending.

        Args:
            model: Model identifier
            messages: Request messages
            system: System prompt
            tools: Tool definitions
            max_tokens: Max output tokens

        Returns:
            CostEstimate
        """
        # Try to count input tokens
        input_tokens = await token_counter.count(
            model=model,
            messages=messages,
            system=system,
            tools=tools,
        )

        if input_tokens is None:
            # Fallback: estimate based on message length
            msg_text = json.dumps(messages)
            input_tokens = len(msg_text) // 4  # Rough estimate: ~4 chars per token
            logger.debug(f"Token counting unavailable for {model}, using estimate: {input_tokens}")

        # Estimate output tokens (heuristic)
        output_tokens = min(max_tokens, 2048)  # Conservative estimate

        costs = self._get_model_cost(model)
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]

        estimate = CostEstimate(
            model=model,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            total_estimated_tokens=input_tokens + output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=input_cost + output_cost,
            cost_per_1m_input=costs["input"],
            cost_per_1m_output=costs["output"],
        )

        logger.debug(
            f"Estimated cost for {model}: {estimate.total_estimated_tokens} tokens, "
            f"${estimate.total_cost_usd:.4f}"
        )

        return estimate

    async def record_cost(
        self,
        request_id: str,
        model: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float = 0.0,
    ) -> CostResult:
        """
        Record actual request cost.

        Args:
            request_id: Request identifier
            model: Model used
            session_id: Session identifier
            user_id: User identifier
            input_tokens: Actual input tokens
            output_tokens: Actual output tokens
            latency_ms: Request latency

        Returns:
            CostResult with response headers
        """
        total_tokens = input_tokens + output_tokens
        costs = self._get_model_cost(model)
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        total_cost = input_cost + output_cost

        result = CostResult(
            request_id=request_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost,
            latency_ms=latency_ms,
        )

        # Build response headers
        result.headers["X-Tier-Cost"] = f"${total_cost:.4f}"
        result.headers["X-Tier-Speed"] = f"{latency_ms:.0f}ms"
        result.headers["X-Tier-Tokens"] = str(total_tokens)
        result.headers["X-Tier-Model"] = model

        logger.info(
            f"Request {request_id} ({model}): {total_tokens} tokens, "
            f"${total_cost:.4f}, {latency_ms:.0f}ms"
        )

        # Track in Redis if enabled
        if session_id:
            await self._track_redis(
                session_id=session_id,
                user_id=user_id,
                request_id=request_id,
                model=model,
                tokens=total_tokens,
                cost=total_cost,
            )

        return result

    async def _track_redis(
        self,
        session_id: str,
        user_id: Optional[str],
        request_id: str,
        model: str,
        tokens: int,
        cost: float,
    ) -> None:
        """Track cost in Redis."""
        redis = await self._get_redis()
        if not redis:
            return

        try:
            # Session-level totals
            session_key = f"cost:session:{session_id}"
            await redis.hincrby(session_key, "tokens", tokens)
            await redis.hincrbyfloat(session_key, "cost_usd", cost)
            await redis.hincrby(session_key, "requests", 1)
            await redis.expire(session_key, 86400)  # 24-hour expiry

            # User-level totals (if available)
            if user_id:
                user_key = f"cost:user:{user_id}"
                await redis.hincrby(user_key, "tokens", tokens)
                await redis.hincrbyfloat(user_key, "cost_usd", cost)
                await redis.hincrby(user_key, "requests", 1)
                await redis.expire(user_key, 86400)

            # Request log
            log_key = f"cost:log:{session_id}"
            log_entry = {
                "request_id": request_id,
                "model": model,
                "tokens": tokens,
                "cost": cost,
                "timestamp": time.time(),
            }
            await redis.lpush(log_key, json.dumps(log_entry))
            await redis.ltrim(log_key, 0, 999)  # Keep last 1000 requests
            await redis.expire(log_key, 86400)

            logger.debug(f"Tracked cost in Redis: {session_id} +${cost:.4f}")

        except Exception as e:
            logger.warning(f"Failed to track cost in Redis: {e}")

    async def get_session_usage(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """
        Get session usage summary from Redis.

        Args:
            session_id: Session identifier

        Returns:
            Usage summary dict
        """
        redis = await self._get_redis()
        if not redis:
            return {
                "error": "Redis tracking disabled",
                "session_id": session_id,
            }

        try:
            session_key = f"cost:session:{session_id}"
            data = await redis.hgetall(session_key)

            if not data:
                return {
                    "session_id": session_id,
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "requests": 0,
                }

            return {
                "session_id": session_id,
                "tokens": int(data.get("tokens", 0)),
                "cost_usd": float(data.get("cost_usd", 0.0)),
                "requests": int(data.get("requests", 0)),
            }

        except Exception as e:
            logger.warning(f"Failed to get session usage from Redis: {e}")
            return {"error": str(e), "session_id": session_id}

    async def get_user_usage(
        self,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Get user usage summary from Redis.

        Args:
            user_id: User identifier

        Returns:
            Usage summary dict
        """
        redis = await self._get_redis()
        if not redis:
            return {
                "error": "Redis tracking disabled",
                "user_id": user_id,
            }

        try:
            user_key = f"cost:user:{user_id}"
            data = await redis.hgetall(user_key)

            if not data:
                return {
                    "user_id": user_id,
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "requests": 0,
                }

            return {
                "user_id": user_id,
                "tokens": int(data.get("tokens", 0)),
                "cost_usd": float(data.get("cost_usd", 0.0)),
                "requests": int(data.get("requests", 0)),
            }

        except Exception as e:
            logger.warning(f"Failed to get user usage from Redis: {e}")
            return {"error": str(e), "user_id": user_id}

    async def get_request_log(
        self,
        session_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get recent request log for session.

        Args:
            session_id: Session identifier
            limit: Maximum requests to return

        Returns:
            List of request log entries
        """
        redis = await self._get_redis()
        if not redis:
            return []

        try:
            log_key = f"cost:log:{session_id}"
            entries = await redis.lrange(log_key, 0, limit - 1)
            return [json.loads(e) for e in entries]

        except Exception as e:
            logger.warning(f"Failed to get request log: {e}")
            return []


# Global singleton
_cost_estimator: Optional[CostEstimator] = None


async def get_cost_estimator() -> CostEstimator:
    """Get or create global cost estimator."""
    global _cost_estimator
    if _cost_estimator is None:
        _cost_estimator = CostEstimator()
    return _cost_estimator
