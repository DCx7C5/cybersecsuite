# @triage — Local Intelligence Layer

> **Current path**: `src/css/modules/triage/`
> **Planned rename**: `src/css/modules/intelligence/`
> **Tracking todo**: `triage-rename-module` in `.plan/session.db`
> **Scope**: routing, memory tagging, confidence/quality gates, tone adaptation, and future retrieval hints.

> **Ollama runtime**: managed natively via `core/ollama/`; no Docker dependency is assumed in current planning.
> Expected local models include `qwen3:0.6b`, `phi4-mini:3.8b-q4_K_M`, and `qwen3:4b-q4_K_M`.

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track TODO/TASK/PHASE state in `.plan/session.db`. Keep this file aligned with current planning, but use `session.db` as the actual progress tracker.

---

**Status**: Planned local intelligence expansion (major work in Phase 21)  
**Model direction**: Qwen3 0.6B + small local helpers via Ollama  
**Location**: `src/css/modules/triage/`  
**5-file pattern**: Present in current module path

## Integration Alignment

This module is part of the wider memory/retrieval/graph architecture.

- `core/memory`: Phase 21 `triage-memory-tagger` attaches semantic tags after memory writes.
- `core/vector_rag`: Phase 21 may later provide `AUTO` retrieval route hints, but retrieval stays owned by `core/vector_rag`.
- `modules/workflows` + `modules/graphs`: triage can classify intent, complexity, or approvals, while workflow/graph state stays outside this module.
- `core/prompt_cache`: local-model prompt/response caching belongs there, not in retrieval caches.

See `.plan/architecture/intelligence-retrieval-graph.md` for the combined system design.

---

## Purpose

The **triage module** is a lightweight background LLM service running locally via Ollama for:

1. **Binary Classification** — Yes/no decisions, approval/rejection, escalate/handle
2. **Query Complexity Assessment** — Classify as simple/moderate/complex for strategy selection
3. **Intent Routing** — Route to appropriate handler: agent, team, skill, or queue
4. **Event Categorization** — Categorize security incidents, threat levels, recommendations

**Key Design Principle**: Local LLM (no API costs, low latency, privacy-preserving)

---

## Model Specifications

### Qwen3 0.6B (Alibaba)
- **Parameters**: 610 million (ultra-lightweight, edge-deployable)
- **Context Window**: 32K tokens
- **Architecture**: Transformer decoder-only
- **Languages**: English + Chinese (multilingual support)
- **Instruction Tuning**: Optimized for few-shot classification
- **Inference Speed**: 50-200ms per token on GPU
- **License**: Qianwen License (research + commercial use)
- **Availability**: HuggingFace ([Qwen/Qwen3-0.5B](https://huggingface.co/Qwen/Qwen3-0.5B))

### Strengths
✅ Ultra-fast inference (suitable for real-time routing)  
✅ Low memory footprint (runs on modest GPUs)  
✅ Instruction-following (few-shot examples work well)  
✅ No API costs or rate limits  
✅ Privacy-preserving (runs locally)

### Limitations
⚠️ Lower accuracy than larger models (GPT-4, Claude 3)  
⚠️ Occasional hallucinations on unfamiliar domains  
⚠️ Requires careful prompt engineering  
⚠️ Cold-start latency: ~2-3 seconds first inference

---

## Infrastructure

### Native Ollama Runtime
- **Runtime owner**: `core/ollama/OllamaProcessManager`
- **API endpoint**: local Ollama HTTP API on port `11434`
- **Model storage**: local Ollama model directory managed outside this module
- **Healthcheck**: `curl -fs http://localhost:11434/api/tags`
- **Planning stance**: native process management, not a required Docker service

**Pull Qwen3 on First Run**:
```bash
# Manual local model pull:
ollama pull qwen3:0.6b
ollama list  # Verify model loaded
curl -s http://localhost:11434/api/tags | jq .
```

---

## SDK Integration

### OllamaClient (api_services/ollama/client.py)
- **Status**: ✅ Implemented (288 lines)
- **Usage**: Direct HTTP calls to local Ollama
- **Methods**:
  - `get_models()` — List available models
  - `call()` — Inference with streaming support
  - `get_execution_context()` — Timing data (load_duration_ms, eval_count)
- **Example**:
```python
from css.api_services.ollama import OllamaClient

client = OllamaClient(base_url="http://localhost:11434")
models = await client.get_models()
response = await client.call(
    model="qwen3:0.6b",
    messages=[{"role": "user", "content": "Is this complex?"}]
)
```

### OllamaApiService (api_services/ollama/service.py)
- **Status**: ⚠️ Partial (Phase 2+ implementation, has TODO stubs)
- **Design**: `BaseApiServiceClient` + `StreamingHandler`
- **Missing**: `get_models()`, `call()` implementations
- **Blocker**: Must complete before Phase 3A.1 triage implementation

### UniversalLLMClient (core/types/universal_client.py)
- **Pattern**: SDKRegistry with lazy-load + caching
- **Status**: ✅ Ready
- **Pre-registration**: `register_sdk("local-ollama", OllamaClient)`
- **Usage**:
```python
from css.core.types.universal_client import UniversalLLMClient

client = UniversalLLMClient()
ollama = await client.get("local-ollama")
response = await ollama.call(model="qwen3:0.6b", messages=[...])
```

---

## Architecture: Request Flow

```
User Query / Event
      ↓
TriageRequest
  (query, context, examples)
      ↓
triage.classify(request)
      ↓
UniversalLLMClient.get("local-ollama")
      ↓
OllamaClient HTTP POST
      ↓
http://localhost:11434/api/generate
      ↓
Qwen3 0.6B Model (Streaming)
      ↓
Response Parser
  (extract: decision + confidence)
      ↓
TriageDecision
  (decision: str, confidence: 0.0-1.0, reasoning: str)
      ↓
Cache (Redis, 5min TTL)
      ↓
Consumer (response_strategy_router, task router, etc)
```

---

## 5-File Pattern Implementation

### Required Files

#### 1. `models.py` (120 lines)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class TriageRequest(BaseModel):
    """Input: User query or event for classification."""
    query: str = Field(..., description="Query or event text")
    context: Optional[str] = Field(None, description="Additional context")
    examples: Optional[list[str]] = Field(None, description="Few-shot examples")
    decision_type: str = Field("binary", description="binary|classification|routing")

class TriageDecision(BaseModel):
    """Output: Classification result with confidence."""
    decision: str = Field(..., description="Decision value (yes/no/simple/etc)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0.0-1.0")
    reasoning: str = Field(..., description="Why this decision")
    alternatives: Optional[list[str]] = Field(None)
    latency_ms: float = Field(..., description="Inference latency")
    model: str = Field("qwen3:0.6b", description="Model used")
```

#### 2. `types.py` (90 lines)
```python
from typing import Literal

# Decision routing targets
RoutingTarget = Literal["agent", "team", "skill", "queue", "escalate", "queue-high"]

# Classification levels
DecisionLevel = Literal["binary", "multiclass", "confidence"]

# Complexity spectrum
QueryComplexity = Literal["simple", "moderate", "complex"]

# Escalation types
EscalationType = Literal["priority", "expertise", "approval", "availability"]
```

#### 3. `enums.py` (60 lines)
```python
from enum import Enum

class DecisionType(str, Enum):
    """Types of triage decisions."""
    BINARY = "binary"              # yes/no, can_handle/escalate
    CLASSIFICATION = "classification"  # simple/moderate/complex
    CONFIDENCE = "confidence"      # 0.0-1.0 score
    ROUTING = "routing"            # agent/team/skill

class ConfidenceLevel(str, Enum):
    """Confidence tiers for decision certainty."""
    HIGH = "high"      # 0.8-1.0 (auto-decision)
    MEDIUM = "medium"  # 0.5-0.8 (human review)
    LOW = "low"        # 0.0-0.5 (fallback routing)

class TriageErrorCode(str, Enum):
    """Error classifications."""
    MODEL_LOAD = "model_load_error"
    INFERENCE = "inference_error"
    TIMEOUT = "timeout_error"
    PARSE = "parse_error"
    UNAVAILABLE = "ollama_unavailable"
```

#### 4. `exceptions.py` (40 lines)
```python
class TriageError(Exception):
    """Base exception for triage module."""
    pass

class ModelLoadError(TriageError):
    """Raised when Qwen3 model fails to load."""
    pass

class InferenceError(TriageError):
    """Raised when inference fails (model error, malformed output)."""
    pass

class TimeoutError(TriageError):
    """Raised when inference exceeds timeout (2s default)."""
    pass

class OllamaUnavailableError(TriageError):
    """Raised when Ollama service is unreachable."""
    pass
```

#### 5. `__init__.py` (40 lines)
```python
"""Triage module: Background LLM for classification and routing.

Provides:
- TriageEngine: Abstract base for triage implementations
- QwenTriageEngine: Qwen3 0.6B implementation via Ollama
- TriageRequest/Decision: Request/response models
"""

from .models import TriageRequest, TriageDecision
from .enums import DecisionType, ConfidenceLevel, TriageErrorCode
from .exceptions import TriageError, ModelLoadError, InferenceError, TimeoutError

__all__ = [
    "TriageRequest",
    "TriageDecision",
    "DecisionType",
    "ConfidenceLevel",
    "TriageError",
    "ModelLoadError",
    "InferenceError",
    "TimeoutError",
]
```

### Extension Files (Not in 5-file pattern, but in module)

#### `base.py` (80 lines)
```python
from abc import ABC, abstractmethod
from .models import TriageRequest, TriageDecision

class TriageEngine(ABC):
    """Abstract base for triage implementations."""
    
    @abstractmethod
    async def classify(self, request: TriageRequest) -> TriageDecision:
        """Perform classification/routing decision."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if triage engine is healthy."""
        pass
```

#### `qwen.py` (250 lines)
```python
from .base import TriageEngine
from .models import TriageRequest, TriageDecision
from .exceptions import *
from css.core.types.universal_client import UniversalLLMClient

class QwenTriageEngine(TriageEngine):
    """Triage engine using Qwen3 0.6B via Ollama."""
    
    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = cache_ttl_seconds
        self.model_name = "qwen3:0.6b"
        self._cache = {}
        self._client = None
    
    async def classify(self, request: TriageRequest) -> TriageDecision:
        """Call Qwen3 with few-shot prompt."""
        # Implementation details...
        pass
    
    async def health_check(self) -> bool:
        """Verify Ollama is responsive."""
        pass
```

---

## Use Cases & Integration Points

### 1. Response Strategy Selection
**File**: `src/css/core/orchestration/response_strategy_router.py` (Line 55)  
**Current**: Heuristic-based (keyword counting)  
**TODO**: Replace with actual Qwen triage call

```python
# BEFORE (heuristic)
def qwen_classify_complexity(query_text: str) -> QueryComplexity:
    q_count = query_text.count("?")
    # ... more heuristics ...
    return QueryComplexity.MODERATE

# AFTER (real triage)
from triage import QwenTriageEngine, TriageRequest

async def qwen_classify_complexity(query_text: str) -> QueryComplexity:
    engine = QwenTriageEngine()
    request = TriageRequest(
        query=query_text,
        decision_type="classification",
        examples=[
            "Is user admin? → simple",
            "Summarize findings. → moderate",
            "Synthesize & compare data. → complex"
        ]
    )
    decision = await engine.classify(request)
    return QueryComplexity(decision.decision)
```

### 2. Task Routing & Escalation
**File**: `src/css/modules/tasks/` (routing enums)  
**Decision**: escalate / handle / defer  
**Use Case**: Task priority, urgency, skill requirements

### 3. Agent Skill Matching
**File**: `src/css/modules/agents/` (agent selection)  
**Decision**: can_handle / needs_delegation / escalate  
**Use Case**: Route complex queries to appropriate agent

### 4. Event Categorization
**File**: `src/css/core/events/` (event classification)  
**Decision**: threat_level, recommendation_type  
**Use Case**: Auto-categorize security incidents

---

## Prompt Templates

### Binary Classification (Yes/No)
```
System: You are a decision engine. Answer with YES or NO only.

Examples:
- Is the user an admin? → YES (confidence: 0.95)
- Should this task be escalated? → NO (confidence: 0.8)
- Does this query need human review? → YES (confidence: 0.75)

Query: {user_query}

Answer: {YES|NO} (confidence: 0.0-1.0) Reason: ...
```

### Complexity Classification
```
System: Classify query complexity: SIMPLE, MODERATE, or COMPLEX.

Examples:
- "Is user admin?" → SIMPLE (0.95) — Binary yes/no check
- "Find all recent incidents" → MODERATE (0.85) — Data retrieval, sorting
- "Correlate incidents & suggest fixes" → COMPLEX (0.8) — Multi-step reasoning

Query: {user_query}

Classification: {SIMPLE|MODERATE|COMPLEX} (confidence: 0.0-1.0)
Reasoning: ...
```

### Escalation Decision
```
System: Decide if this task should be escalated.

Context: Task priority={priority}, estimated_duration={hours}h, expertise={level}

Examples:
- Priority=LOW, duration=0.5h, expertise=junior → NO ESCALATE
- Priority=CRITICAL, duration=2h, expertise=needed → ESCALATE
- Priority=MEDIUM, duration=4h, expertise=specialist → ESCALATE

Query: {task_description}

Decision: {ESCALATE|HANDLE|DEFER} (confidence: 0.0-1.0)
Reasoning: ...
```

---

## Implementation Roadmap

### Phase 3A: Foundation (Week 1)
- [ ] **Task 3A.1**: Complete OllamaApiService (remove TODOs) ⚠️ **BLOCKER**
- [ ] **Task 3A.2**: Create 5-file module structure (models → __init__)
- [ ] **Task 3A.3**: Implement TriageEngine base class
- [ ] **Task 3A.4**: Implement QwenTriageEngine (Ollama integration)
- [ ] **Task 3A.5**: Background task queue integration

**Deliverable**: 5-file compliant triage module, <200ms latency, basic classification working

### Phase 3B: Integration (Week 2)
- [ ] **Task 3B.1**: Integrate response_strategy_router (replace TODO)
- [ ] **Task 3B.2**: Integrate task routing & escalation
- [ ] **Task 3B.3**: Integrate agent skill matching
- [ ] **Task 3B.4**: End-to-end integration tests

**Deliverable**: Real triage in production request path, all integrations passing

### Phase 3C: Optimization (Week 3)
- [ ] **Task 3C.1**: Prompt tuning on 100+ real queries
- [ ] **Task 3C.2**: Error handling & fallback patterns
- [ ] **Task 3C.3**: Monitoring & observability
- [ ] **Task 3C.4**: Load testing (100 concurrent requests)

**Deliverable**: 85%+ accuracy, production-ready, monitoring in place

---

## Performance Targets

### Latency
| Scenario | Target | Notes |
|----------|--------|-------|
| Warm inference | <50ms | Cache hit, model already loaded |
| Average inference | <200ms | Excluding model load time |
| Cold start | <3s | First call after container restart |
| Timeout | 2s | Hard limit for any inference |

### Accuracy
| Task | Target | Notes |
|------|--------|-------|
| Binary classification | 85%+ | yes/no decisions |
| Complexity classification | 80%+ | simple/moderate/complex |
| Escalation decisions | 80%+ | escalate/handle/defer |

### Reliability
| Metric | Target | Notes |
|--------|--------|-------|
| Uptime | 99%+ | Graceful fallback if unavailable |
| Concurrent requests | 10+ | Before queue buildup |
| Error rate | <5% | Malformed input, timeouts |

---

## Error Handling & Fallback

### Cascade Strategy
```
1. Try Qwen3 triage (ideal, <200ms)
   ↓ Timeout/error?
2. Check cache (previous decision, <5min old)
   ↓ No cache?
3. Use deterministic fallback (heuristic rules)
   ↓ Escalation? 
4. Route to human review
```

### Fallback Rules
- **If Ollama unavailable**: Use response_strategy_router heuristic (keyword counting)
- **If inference times out**: Return cached result or fallback decision with LOW confidence
- **If malformed output**: Retry once, then fallback
- **Circuit breaker**: Disable triage if >5 consecutive errors in 1min

---

## Monitoring & Observability

### Metrics to Track
- **Latency distribution**: p50, p95, p99 (milliseconds)
- **Cache hit rate**: % decisions from cache vs fresh inference
- **Accuracy**: Post-hoc feedback from human reviewers
- **Confidence calibration**: Are 0.9 decisions actually correct 90% of the time?
- **Model load time**: How long to load model on startup
- **Error rates**: Timeouts, malformed output, Ollama unavailable

### Logging
```python
logger.info(f"Triage decision: {decision.decision} "
            f"(confidence={decision.confidence:.2f}, "
            f"latency={decision.latency_ms:.1f}ms)")

logger.warning(f"Low confidence decision: {decision.decision} "
               f"(confidence={decision.confidence:.2f})")

logger.error(f"Triage inference failed: {error}")
```

### Health Checks
- HTTP endpoint: `/health/triage` → `{"status": "healthy", "model": "qwen3:0.6b"}`
- Ollama ping: `curl -s http://localhost:11434/api/tags`
- Model test: Send dummy query, measure latency

---

## Success Criteria

### Functional Requirements
- ✅ Triage module follows 5-file pattern (models, types, enums, exceptions, __init__)
- ✅ QwenTriageEngine successfully calls Qwen3 0.6B via Ollama
- ✅ Binary classification works (85%+ accuracy on test set)
- ✅ Complexity classification works (80%+ accuracy)
- ✅ response_strategy_router TODO replaced with real triage
- ✅ All integrations (router, tasks, agents) passing

### Performance Requirements
- ✅ <200ms average latency (excluding cold-start)
- ✅ <3s cold start (first inference after restart)
- ✅ Handles 10 concurrent requests without timeout
- ✅ 85%+ binary classification accuracy
- ✅ 80%+ complexity classification accuracy

### Reliability Requirements
- ✅ Ollama health check passing
- ✅ Graceful fallback if Ollama unavailable
- ✅ No crashes on malformed input
- ✅ Retry logic for transient failures
- ✅ Circuit breaker if >5 consecutive errors

### Code Quality Requirements
- ✅ All 5 files follow PEP 8 + type hints
- ✅ Unit tests: TriageRequest/TriageDecision parsing
- ✅ Integration test: end-to-end classification
- ✅ Docstrings on all public methods
- ✅ No hardcoded values (use config.py)

---

## Dependencies

### Hard Blockers (Must Fix First)
1. ⚠️ **OllamaApiService completion** — `get_models()`, `call()` stubs (api_services/ollama/service.py)
2. ⚠️ **Phase 21 wiring** — connect planned intelligence features into the live triage engine

### Soft Dependencies (Nice to Have)
- @tasks module background queue (fallback: manual async)
- Redis pub/sub (fallback: simple in-memory queue)
- Monitoring dashboard (fallback: log files)

### Infrastructure Dependencies
- ✅ Native Ollama runtime via `core/ollama/`
- ✅ OllamaClient (already implemented)
- ✅ UniversalLLMClient (already ready)

---

## Open Questions

1. **Model warm-up on startup?** Pre-load Qwen3 (adds 2-3s startup) to eliminate cold-start latency?

2. **Cache invalidation strategy?** TTL-only (5min default)? Manual flush? Versioning?

3. **Confidence threshold for auto-decision?** Default 0.7? Configurable per use-case?

4. **Multi-language support?** Qwen3 is multilingual but lower quality for non-English. Force English prompts?

5. **Fallback to larger model?** For high-stakes decisions, should we call GPT-4 if Qwen confidence <0.8?

---

## See Also

- **Ollama SDK**: `src/css/api_services/ollama/`
- **Response Router**: `src/css/core/orchestration/response_strategy_router.py` (has TODO)
- **Task Routing**: `src/css/modules/tasks/enums.py` (RoutingStrategy enum)
- **Agent Selection**: `src/css/modules/agents/` (skill matching)
- **Events Module**: `src/css/core/events/` (event categorization)

---

**Last Updated**: 2026-05-03 17:30:24 UTC  
**Status**: Planning → Ready for Implementation  
**Awaiting**: User approval to begin Phase 3A
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/plan.md for current audit and phase status.

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`


---

## ⚠️ Tier Design Updated (Phase 13 — 2026-05-04)

The original 5-tier system (`tier0_simple` → `tier4_critical`) has been **replaced**
by a 11-tier `PROVIDER_TIER_LIST` (rank 0–10). See `.plan/plan.md` Phase 13.

**New tiers (lowest → highest):**

| Rank | Label | Models | Hardware |
|------|-------|--------|----------|
| 0 | LOCAL_MINIMAL | qwen3:0.6b, llama3.2:1b | CPU only (works on any PC) |
| 1 | LOCAL_LIGHT | qwen3:1.7b, phi3:mini | 4GB VRAM |
| 2 | LOCAL_STANDARD | qwen3:4b, llama3.1:8b | 8GB VRAM |
| 3 | LOCAL_CAPABLE | qwen3:8b, deepseek-r1:8b | 16GB VRAM |
| 4 | FREE_CLOUD | gemini-2.0-flash-lite, groq/llama | None (API, free) |
| 5 | BUDGET_CLOUD | gemini-2.0-flash, deepseek-chat, grok-3-mini | None |
| 6 | STANDARD_CLOUD | gpt-4o-mini, claude-3-haiku | None |
| 7 | ADVANCED_CLOUD | gpt-4o, claude-3-5-sonnet | None |
| 8 | PREMIUM_CLOUD | gpt-4.5, claude-3-7-sonnet, o3-mini | None |
| 9 | ELITE_CLOUD | claude-opus-4-5, gpt-5, o3 | None |
| 10 | **S_PLUS** ← always last | claude-opus-4-7, o3-pro | None |

`PROVIDER_TIER_LIST[-1]` is **always** S+. Insert new tiers above it, never after.

**Complexity → minimum tier:**

| Complexity | Min Rank | Notes |
|------------|----------|-------|
| TRIVIAL | 0 | Qwen3 0.6B handles it |
| SIMPLE | 0 | Local preferred, free cloud fallback |
| MODERATE | 1 | Light local or free cloud |
| COMPLEX | 5 | Budget cloud minimum |
| CRITICAL | 7 | Advanced cloud minimum |
| security_level≥9 | 9 | Elite or S+ only |
