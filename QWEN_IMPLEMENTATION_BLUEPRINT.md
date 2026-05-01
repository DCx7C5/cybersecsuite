# Qwen3-0.6B Triage Layer Implementation Blueprint

Quick-reference implementation guide for Phase 2 (post-ModelExecutor extraction).

---

## File Structure (Phase 2)

```
src/core/triage/
├── __init__.py
├── router.py          # Main triage router (public API)
├── qwen_client.py     # Ollama/Qwen integration
├── prompts.py         # Prompt templates by use case
├── cache.py           # Redis-backed triage cache
└── models.py          # Pydantic models (TriageDecision, etc.)

tests/unit/core/triage/
├── test_router.py     # Router logic tests
├── test_qwen_client.py  # Qwen integration tests
├── test_cache.py      # Cache effectiveness tests
└── test_fallback.py   # Fallback + error handling

tests/integration/core/
├── test_triage_e2e.py # End-to-end with real Qwen
```

---

## 1. Core Module: `src/core/triage/models.py`

```python
"""Triage decision models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TriageClassification(str, Enum):
    """Request classification levels."""
    URGENT = "urgent"
    ROUTINE = "routine"
    COMPLEX = "complex"
    VALIDATION = "validation"
    LOOKUP = "lookup"


class TriageDecision(BaseModel):
    """Triage decision output."""
    classification: TriageClassification
    recommended_provider: str  # e.g., "claude-opus", "gpt-3.5", "local"
    confidence: float = Field(ge=0, le=1, description="0.0-1.0 confidence")
    reasoning: str = Field(max_length=200)
    estimated_cost_usd: float = Field(ge=0)
    cache_ttl_seconds: int = Field(default=3600)
    
    class Config:
        use_enum_values = True


class TriageRequest(BaseModel):
    """Input to triage system."""
    user_query: str = Field(max_length=5000)
    request_type: Optional[str] = None  # e.g., "ioc_lookup", "artifact"
    context: Optional[dict] = None  # Additional metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
```

---

## 2. Prompt Registry: `src/core/triage/prompts.py`

```python
"""Triage prompts by use case."""

from dataclasses import dataclass


@dataclass
class TriagePrompt:
    system: str
    examples: list[str]
    max_tokens: int = 200


PROMPTS = {
    "urgency": TriagePrompt(
        system="""You are a cybersecurity incident triage agent.
Classify request urgency: CRITICAL, HIGH, MEDIUM, or LOW.

CRITICAL: Active exploitation, ongoing attack, real-time threat
HIGH: Suspicious activity, malware, potential compromise
MEDIUM: Anomaly detected, policy violation, failed auth
LOW: Informational, historical data, general knowledge

Respond with: [LEVEL] → [PROVIDER] | [REASONING]
Keep reasoning under 50 tokens.""",
        
        examples=[
            "Input: 'Found 192.0.2.5 connecting to C2 in prod logs'\nOutput: CRITICAL → claude-opus | Active C2 communication, requires immediate analysis",
            "Input: 'What is the OSI model?'\nOutput: LOW → local | General knowledge, no urgency",
            "Input: 'Malware detected on workstation'\nOutput: HIGH → gpt-4 | Compromised system, needs rapid response",
        ],
    ),
    
    "domain_validation": TriagePrompt(
        system="""Classify domain/email as: LEGITIMATE, SUSPICIOUS, or MALICIOUS.
LEGITIMATE: Known good, major TLD, proper DNS
SUSPICIOUS: Typo, uncommon TLD, homograph similarity
MALICIOUS: Known phishing/C2, on blocklist

Respond: [CLASS] | [SCORE 0-1] | [REASON]""",
        
        examples=[
            "microsoft.com → LEGITIMATE | 0.99 | Well-known domain",
            "microsof t.com → SUSPICIOUS | 0.85 | Typosquatting (space)",
            "μicrosoft.com → SUSPICIOUS | 0.92 | Homograph (Greek mu)",
        ],
        max_tokens=100,
    ),
    
    "complexity": TriagePrompt(
        system="""Assess request complexity: SIMPLE, MODERATE, or COMPLEX.
SIMPLE: Single IOC, one tool, local can handle
MODERATE: Multi-part, 2-3 tools, some coordination
COMPLEX: Full investigation, artifact analysis, orchestration needed

Respond: [LEVEL] | [REASON] | [ESTIMATED_TOOLS_COUNT]""",
        
        examples=[
            "What's an IP address? → SIMPLE | Reference question | 0 tools",
            "Check if file is malicious → MODERATE | Requires VirusTotal + hashing | 2 tools",
            "Investigate APT28 infrastructure → COMPLEX | Multi-IOC, cross-reference | 5+ tools",
        ],
    ),
}


def get_prompt(use_case: str) -> TriagePrompt:
    """Retrieve prompt template by use case."""
    if use_case not in PROMPTS:
        raise ValueError(f"Unknown use case: {use_case}")
    return PROMPTS[use_case]


def build_prompt(use_case: str, user_query: str) -> str:
    """Build full prompt with examples."""
    prompt_cfg = get_prompt(use_case)
    
    # System + examples + query
    full_prompt = f"""{prompt_cfg.system}

EXAMPLES:
{chr(10).join(prompt_cfg.examples)}

REQUEST:
{user_query}

RESPONSE:"""
    
    return full_prompt
```

---

## 3. Qwen Client: `src/core/triage/qwen_client.py`

```python
"""Ollama/Qwen3 client wrapper."""

import httpx
import logging
from typing import Optional
from .models import TriageDecision, TriageClassification

logger = logging.getLogger(__name__)


class QwenClient:
    """Ollama-based Qwen3-0.6B client."""
    
    def __init__(
        self,
        ollama_base_url: str = "http://localhost:11434",
        model_name: str = "qwen3:0.6b",
        timeout_seconds: float = 30,
    ):
        self.base_url = ollama_base_url
        self.model = model_name
        self.timeout = timeout_seconds
        self.client = httpx.AsyncClient(timeout=timeout_seconds)
    
    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = await self.client.get(f"{self.base_url}/api/tags")
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            logger.warning("Ollama health check failed")
            return False
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
    ) -> str:
        """
        Generate response from Qwen3.
        
        Args:
            prompt: Full prompt (system + examples + request)
            max_tokens: Max response tokens
        
        Returns:
            Raw response text
        
        Raises:
            OllamaUnavailableError: If Ollama not responding
        """
        try:
            resp = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens,
                    "temperature": 0.3,  # Low temperature for consistency
                },
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except httpx.RequestError as e:
            logger.error(f"Ollama request failed: {e}")
            raise OllamaUnavailableError(str(e)) from e


class OllamaUnavailableError(Exception):
    """Raised when Ollama is not available."""
    pass
```

---

## 4. Router: `src/core/triage/router.py`

```python
"""Main triage router with caching + fallback."""

import logging
from typing import Optional
from .models import TriageDecision, TriageRequest, TriageClassification
from .qwen_client import QwenClient, OllamaUnavailableError
from .cache import TriageCache
from .prompts import build_prompt
from src.core.redis.client import RedisClient

logger = logging.getLogger(__name__)


class TriageRouter:
    """
    Main router: Classifies requests and routes to appropriate provider.
    
    Architecture:
    1. Check cache (key: hash of request)
    2. If hit: return cached decision (<1ms)
    3. If miss: call Qwen (300ms)
    4. Cache result
    5. If Ollama down: skip triage, use default routing
    """
    
    def __init__(
        self,
        qwen_client: QwenClient,
        redis_client: RedisClient,
        cache_ttl_seconds: int = 3600,
    ):
        self.qwen = qwen_client
        self.cache = TriageCache(redis_client, ttl_seconds=cache_ttl_seconds)
    
    async def triage(self, request: TriageRequest) -> TriageDecision:
        """
        Triage a request and return routing decision.
        
        Args:
            request: TriageRequest with user_query
        
        Returns:
            TriageDecision with classification, provider, confidence
        
        Fallback:
            If Ollama down or error occurs, returns None
            → Caller uses default routing
        """
        
        # 1. Generate cache key
        cache_key = self._cache_key(request)
        
        # 2. Check cache
        if cached_decision := await self.cache.get(cache_key):
            logger.info(f"Triage cache hit: {cache_key}")
            return cached_decision
        
        # 3. Check Ollama health
        if not await self.qwen.health_check():
            logger.warning("Ollama unavailable, skipping triage")
            return None  # Caller will use default routing
        
        # 4. Build prompt
        use_case = request.request_type or "urgency"
        prompt = build_prompt(use_case, request.user_query)
        
        # 5. Call Qwen
        try:
            response = await self.qwen.generate(
                prompt,
                max_tokens=200,
            )
        except OllamaUnavailableError:
            logger.warning("Qwen inference failed, skipping triage")
            return None
        
        # 6. Parse response
        try:
            decision = self._parse_response(response, use_case)
        except ValueError as e:
            logger.error(f"Failed to parse Qwen response: {e}")
            return None
        
        # 7. Cache decision
        await self.cache.set(cache_key, decision)
        
        return decision
    
    def _cache_key(self, request: TriageRequest) -> str:
        """Generate cache key from request."""
        import hashlib
        key_parts = (
            request.request_type or "general",
            request.user_query[:100],  # Truncate for hashing
        )
        key_str = "|".join(key_parts)
        return f"triage:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _parse_response(self, response: str, use_case: str) -> TriageDecision:
        """
        Parse Qwen response into TriageDecision.
        
        Expected format:
        [LEVEL] → [PROVIDER] | [REASONING]
        
        Example:
        CRITICAL → claude-opus | Active C2 communication
        """
        lines = response.strip().split("|")
        if len(lines) < 2:
            raise ValueError(f"Unexpected response format: {response}")
        
        # Parse classification and provider
        level_provider = lines[0].strip().split("→")
        classification = level_provider[0].strip().lower()
        provider = level_provider[1].strip().lower() if len(level_provider) > 1 else "local"
        reasoning = lines[1].strip() if len(lines) > 1 else ""
        
        # Map classification
        class_map = {
            "critical": TriageClassification.URGENT,
            "urgent": TriageClassification.URGENT,
            "high": TriageClassification.URGENT,
            "routine": TriageClassification.ROUTINE,
            "medium": TriageClassification.ROUTINE,
            "low": TriageClassification.ROUTINE,
            "complex": TriageClassification.COMPLEX,
            "validation": TriageClassification.VALIDATION,
            "lookup": TriageClassification.LOOKUP,
        }
        
        return TriageDecision(
            classification=class_map.get(classification, TriageClassification.ROUTINE),
            recommended_provider=provider,
            confidence=0.75,  # Estimated, can be improved
            reasoning=reasoning[:200],
        )
```

---

## 5. Cache: `src/core/triage/cache.py`

```python
"""Redis-backed triage decision cache."""

import json
import logging
from typing import Optional
from .models import TriageDecision
from src.core.redis.client import RedisClient

logger = logging.getLogger(__name__)


class TriageCache:
    """Cache for triage decisions."""
    
    def __init__(self, redis_client: RedisClient, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.key_prefix = "triage:decision:"
    
    async def get(self, cache_key: str) -> Optional[TriageDecision]:
        """Get cached triage decision."""
        try:
            value = await self.redis.get(f"{self.key_prefix}{cache_key}")
            if value:
                data = json.loads(value)
                return TriageDecision(**data)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    async def set(self, cache_key: str, decision: TriageDecision):
        """Cache triage decision."""
        try:
            await self.redis.setex(
                f"{self.key_prefix}{cache_key}",
                self.ttl,
                decision.model_dump_json(),
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
    
    async def clear_all(self):
        """Clear all cached decisions."""
        pattern = f"{self.key_prefix}*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            logger.info(f"Cleared {len(keys)} cached decisions")
```

---

## 6. Integration: `src/core/asgi/router.py` (Modification)

```python
"""ASGI router integration with triage layer."""

from fastapi import APIRouter, Request, Depends
from ..triage.router import TriageRouter
from ..triage.models import TriageRequest

router = APIRouter()

# Dependency injection
async def get_triage_router(request: Request) -> Optional[TriageRouter]:
    """Get triage router from app state (or None if disabled)."""
    return getattr(request.app, "triage_router", None)


@router.post("/analyze")
async def analyze_request(
    payload: dict,
    triage_router: Optional[TriageRouter] = Depends(get_triage_router),
):
    """
    Main analysis endpoint with optional triage layer.
    
    Flow:
    1. If triage enabled: triage request
    2. Use triage decision to select provider
    3. Execute ModelExecutor with selected provider
    4. Return results
    """
    user_query = payload.get("query")
    request_type = payload.get("type", "general")
    
    # Step 1: Triage (if enabled)
    if triage_router:
        triage_req = TriageRequest(
            user_query=user_query,
            request_type=request_type,
        )
        triage_decision = await triage_router.triage(triage_req)
        
        if triage_decision:
            provider = triage_decision.recommended_provider
            logger.info(f"Triage routed to: {provider}")
        else:
            # Fallback to default routing
            provider = None
            logger.info("Triage skipped, using default routing")
    else:
        provider = None
    
    # Step 2: Execute ModelExecutor
    executor = ModelExecutor(provider_hint=provider)
    result = await executor.execute(
        query=user_query,
        context={"type": request_type},
    )
    
    return result
```

---

## 7. Unit Test: `tests/unit/core/triage/test_router.py`

```python
"""Triage router unit tests."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.triage.router import TriageRouter
from src.core.triage.models import TriageRequest, TriageDecision, TriageClassification


@pytest.mark.asyncio
async def test_triage_cache_hit():
    """Cached decisions return <5ms."""
    # Mock dependencies
    qwen = AsyncMock()
    redis = AsyncMock()
    
    # Setup cache to return existing decision
    cached_decision = TriageDecision(
        classification=TriageClassification.ROUTINE,
        recommended_provider="gpt-3.5",
        confidence=0.9,
        reasoning="Cached result",
    )
    redis.get.return_value = cached_decision.model_dump_json()
    
    # Test
    router = TriageRouter(qwen, redis)
    request = TriageRequest(user_query="What is DNS?")
    
    result = await router.triage(request)
    
    # Verify
    assert result.classification == TriageClassification.ROUTINE
    qwen.health_check.assert_not_called()  # Cache hit, no Qwen call
    qwen.generate.assert_not_called()


@pytest.mark.asyncio
async def test_triage_fallback_ollama_down():
    """Returns None if Ollama unavailable."""
    qwen = AsyncMock()
    qwen.health_check.return_value = False
    redis = AsyncMock()
    redis.get.return_value = None  # Cache miss
    
    router = TriageRouter(qwen, redis)
    request = TriageRequest(user_query="Urgent security alert")
    
    result = await router.triage(request)
    
    assert result is None  # Fallback: no triage
    redis.set.assert_not_called()  # Don't cache failed attempts


@pytest.mark.asyncio
async def test_triage_urgent_classification():
    """Classifies urgent requests correctly."""
    qwen = AsyncMock()
    qwen.health_check.return_value = True
    qwen.generate.return_value = "CRITICAL → claude-opus | Active malware"
    redis = AsyncMock()
    redis.get.return_value = None
    
    router = TriageRouter(qwen, redis)
    request = TriageRequest(user_query="Found ransomware on prod server")
    
    result = await router.triage(request)
    
    assert result.classification == TriageClassification.URGENT
    assert result.recommended_provider == "claude-opus"
    redis.set.assert_called_once()  # Result cached


@pytest.mark.asyncio
async def test_triage_parse_malformed_response():
    """Gracefully handles malformed Qwen responses."""
    qwen = AsyncMock()
    qwen.health_check.return_value = True
    qwen.generate.return_value = "Not a valid format"
    redis = AsyncMock()
    redis.get.return_value = None
    
    router = TriageRouter(qwen, redis)
    request = TriageRequest(user_query="Some query")
    
    result = await router.triage(request)
    
    # Should return None and log error, not crash
    assert result is None
```

---

## 8. Integration Test: `tests/integration/core/test_triage_e2e.py`

```python
"""End-to-end triage tests with real Ollama."""

import pytest
import os
from src.core.triage.router import TriageRouter
from src.core.triage.models import TriageRequest


@pytest.mark.skipif(
    os.getenv("SKIP_OLLAMA_TESTS") == "true",
    reason="Ollama not available"
)
@pytest.mark.asyncio
async def test_triage_e2e_urgent():
    """End-to-end: Urgent request routed to expensive provider."""
    # Setup with real Ollama
    qwen = get_real_qwen_client()
    redis = get_redis_client()
    
    router = TriageRouter(qwen, redis)
    
    # Urgent security request
    request = TriageRequest(
        user_query="I found C2 traffic connecting from our prod servers to 192.0.2.100",
        request_type="ioc_lookup",
    )
    
    result = await router.triage(request)
    
    # Should classify as urgent
    assert result is not None
    assert result.classification.value in ["urgent", "critical"]
    assert result.recommended_provider != "local"
    assert result.confidence > 0.7


@pytest.mark.skipif(
    os.getenv("SKIP_OLLAMA_TESTS") == "true",
    reason="Ollama not available"
)
@pytest.mark.asyncio
async def test_triage_e2e_routine():
    """End-to-end: Routine request routed to cheap provider."""
    qwen = get_real_qwen_client()
    redis = get_redis_client()
    
    router = TriageRouter(qwen, redis)
    
    # Routine knowledge question
    request = TriageRequest(
        user_query="What is the OSI model?",
        request_type="general_knowledge",
    )
    
    result = await router.triage(request)
    
    # Should classify as routine
    assert result is not None
    assert result.classification.value in ["routine", "low"]
    assert result.recommended_provider in ["local", "gpt-3.5"]
    assert result.confidence > 0.7
```

---

## 9. Observability: OTEL Metrics

```python
"""OpenTelemetry instrumentation for triage layer."""

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import Counter, Histogram

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Metrics
triage_classification_counter = meter.create_counter(
    "triage_classification_count",
    description="Count of triage classifications by type",
    unit="1",
)

triage_latency_histogram = meter.create_histogram(
    "triage_latency_ms",
    description="Triage latency in milliseconds",
    unit="ms",
)

triage_cache_hit_rate = meter.create_counter(
    "triage_cache_hits",
    description="Triage cache hit count",
    unit="1",
)

triage_cost_savings = meter.create_counter(
    "triage_cost_savings_usd",
    description="Estimated cost savings from triage routing",
    unit="usd",
)


# Usage in router
async def triage(self, request):
    with tracer.start_as_current_span("triage.classify") as span:
        start = time.time()
        result = await self._execute_triage(request)
        elapsed = time.time() - start
        
        span.set_attribute("classification", result.classification)
        span.set_attribute("provider", result.recommended_provider)
        span.set_attribute("confidence", result.confidence)
        
        triage_latency_histogram.record(elapsed * 1000)
        triage_classification_counter.add(
            1,
            attributes={"classification": result.classification}
        )
        
        return result
```

---

## 10. Phase 2 Timeline

| Week | Task | Estimate |
|------|------|----------|
| 1 | Setup Ollama, implement core router | 3 days |
| 2 | Prompt engineering (urgency + domain validation) | 2 days |
| 3 | Caching layer + integration tests | 2 days |
| 4 | Production A/B test + monitoring | 3 days |

**Total:** ~2 weeks, ~80 hours engineering time

