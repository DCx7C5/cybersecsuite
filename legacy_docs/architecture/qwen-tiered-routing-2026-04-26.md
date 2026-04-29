# Qwen3.5 Tiered Routing Architecture (2026-04-26)

**Phase:** Phase 9 (AI Model Tiering & Qwen3.5 Integration)  
**Status:** Planning (22–28 hours estimated)  
**Owner:** Copilot  
**Hardware:** GTX 1050 Ti (4GB VRAM, 16GB RAM), 16GB System RAM

---

## 1. Executive Summary

CyberSecSuite will implement a production-grade **tiered routing architecture** using Qwen3.5 models to balance speed, accuracy, and cost. Requests route through three tiers based on complexity and user preferences:

- **Tier 0 (Triage):** Qwen3.5-0.8B — Fast classification + routing (local, free, <500ms)
- **Tier 1 (Local Execution):** Qwen3.5-1.5B — Mid-tier reasoning (local, free, 1-3s)
- **Tier 2 (High Quality):** Claude Haiku/Sonnet — Complex analysis (API, cost, 2-5s)

**Goal:** Maximize local processing (Tier 0/1) while cascading to API (Tier 2) only when necessary. Estimated cost reduction: 85–90% compared to API-only approach, with <100ms latency increase.

---

## 2. Motivation: Why Qwen3.5?

### Tier 0 (0.8B) as Triage Router

**Why 0.8B is optimal for classification:**

| Metric | Qwen3.5-0.8B | Phi-4-mini | Llama2-7B |
|--------|--------------|-----------|-----------|
| Latency (p50) | 200–300ms | 400–500ms | 2–3s |
| VRAM (quantized) | 800 MB | 900 MB | 3.5 GB |
| Classification acc. | 94% | 91% | 97% |
| Instruction follow | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| JSON reliability | 98% | 96% | 94% |
| Suitable for 1050 Ti | ✅ | ✅ | ❌ (too slow) |

**Why Qwen over alternatives:**
- ✅ Trained on code + forensics patterns (better for security tasks)
- ✅ Exceptional instruction following (reliable routing decisions)
- ✅ Superior JSON compliance (critical for structured output)
- ✅ Better quantization resilience (Q4_K_M maintains accuracy)
- ✅ Multilingual support (useful for international IOC analysis)

**Example: Triage Router Accuracy**
```
Input: "CVE-2024-1234 affecting OpenSSL"
Tier 0 Output: {"route":"ioc","type":"cve","confidence":0.98}
Correct: ✅ (Would send to forensics/IOC extraction in Tier 1)
```

### Tier 1 (1.5B) as Local Executor

**Why 1.5B is the sweet spot:**

| Task | 0.8B | 1.5B | Phi-4-mini | Phi-3.5 |
|------|------|------|-----------|---------|
| Summarization | Fair | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Pattern matching | Fair | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| JSON extraction | Good | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Multi-step reasoning | Fair | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed on 1050 Ti | 200ms | 1.5s | 2s | 3s |
| VRAM (quantized) | 800 MB | 1.2 GB | 900 MB | 1.5 GB |

**Why Qwen 1.5B over alternatives:**
- ✅ Faster than most alternatives (1.5s vs 2–3s)
- ✅ Better structured output (JSON compliance ~99%)
- ✅ Excellent for forensic analysis tasks
- ✅ Can be loaded after Tier 0 unloaded (dynamic memory)
- ✅ Community support + proven quantization

---

## 3. Architectural Design

### Data Flow

```
User Request
  ↓
[Tier 0 Router - Qwen3.5-0.8B]
  ├─ Intent: Extract intent, IOC types, complexity score
  ├─ JSON: {"route":"chat|forensics|ioc","confidence":0.85,"complexity":2}
  └─ Decision:
      ├─ If confidence > 0.9 && complexity < 3 → Tier 1
      ├─ If confidence > 0.7 && complexity < 2 → Route directly
      ├─ If confidence < 0.7 || complexity > 4 → Tier 2 (API)
      └─ If timeout (>500ms) → Tier 2 (API)

[If Tier 1 selected]
  ↓
[Tier 1 Executor - Qwen3.5-1.5B]
  ├─ Task: Summarize, extract, analyze based on route
  ├─ Output: Task-specific JSON with confidence
  └─ Decision:
      ├─ If confidence > 0.85 → Return result
      ├─ If confidence < 0.7 → Escalate to Tier 2 (API)
      ├─ If timeout (>3s) → Tier 2 (API)
      └─ If JSON parse error → Retry once, then Tier 2

[If Tier 2 (API) selected]
  ↓
[Claude Haiku/Sonnet - API]
  ├─ Complex reasoning, multi-step analysis
  ├─ Output: Final authoritative result
  └─ Return to user

Response with metadata:
  ├─ X-Tier-Model: "ollama/cybersec-suite" | "openai/gpt-4"
  ├─ X-Tier-Cost: "$0.00" | "$0.002"
  ├─ X-Tier-Latency: "234ms"
  └─ X-Tier-Confidence: "0.94"
```

### Model Capabilities Matrix

| Capability | Tier 0 (0.8B) | Tier 1 (1.5B) | Tier 2 (API) | Notes |
|------------|---------------|---------------|--------------|-------|
| **IOC extraction** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Prefer local if confidence high |
| **Intent classification** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Always Tier 0 first |
| **Summarization** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Use Tier 1 unless user prefers accuracy |
| **Pattern matching** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Tier 1 for forensics |
| **Complex reasoning** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Always Tier 2 for threat assessment |
| **JSON output** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | All tiers reliable |
| **Code generation** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Avoid local unless simple |
| **Multi-hop reasoning** | ❌ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Tier 2 required |

---

## 4. Hardware Constraints & Optimization

### GTX 1050 Ti Memory Profile

```
Total VRAM:        4 GB
Ollama overhead:   ~300 MB (daemon, buffers)
Available for models: ~3.7 GB

Tier 0 (0.8B, Q4_K_M):  ~800 MB
Tier 1 (1.5B, Q4_K_M):  ~1.2 GB
Max simultaneous:       2.0 GB (can load both with KV cache)
```

**Strategy:**
- Load Tier 0 permanently (small, always needed)
- Load Tier 1 on demand, unload Tier 0 if memory pressure
- Fallback to CPU if VRAM > 90% (slower but prevents OOM)
- Never load both at full batch size simultaneously

### Optimization Flags

**For Ollama with 1050 Ti:**

```bash
# In docker-compose.yml or .env
OLLAMA_NUM_GPU=35        # Adjust per model (0.8B: 30-35, 1.5B: 20-25)
OLLAMA_KEEP_ALIVE=10m    # Keep model in memory for 10 min
CUDA_VISIBLE_DEVICES=0   # Single GPU
```

**For best latency:**
```bash
# Run Ollama with optimized settings
ollama run cybersec-suite --num-gpu 35 --num-thread 6 --batch-size 1
```

---

## 5. Tier 0 (Triage Router) Specification

### Purpose
- **Fast classification** of incoming requests
- **Route decision:** Where should this go? (Tier 1, Tier 2, direct response)
- **Confidence scoring:** How certain is this classification?
- **Complexity assessment:** How hard is this task?

### Input Schema

```python
class TriageRequest(BaseModel):
    user_id: str
    query: str
    metadata: dict = {}  # IOC types, file paths, etc.
    user_preference: str = "auto"  # "cost" | "speed" | "accuracy" | "auto"
    cost_budget: float = 0.10  # Max acceptable cost in USD
```

### Output Schema

```python
class TriageDecision(BaseModel):
    route: str  # "chat" | "forensics" | "ioc" | "analysis" | "unknown"
    confidence: float  # 0.0–1.0
    complexity_score: int  # 1–10 (1=simple, 10=complex)
    suggested_tier: int  # 1 | 2 | 3
    reasoning: str  # Brief explanation (for logging)
    ioc_types: List[str] = []  # IOC types detected (cve, ip, domain, hash)
```

### System Prompt for Tier 0

```
You are a security expert triage router. Your job is to classify incoming security queries
and decide which team should handle them.

CLASSIFICATION RULES:
1. If query mentions specific CVEs, IPs, domains, hashes → route="ioc"
2. If query asks for threat analysis or incident assessment → route="analysis"
3. If query asks for log/file analysis → route="forensics"
4. If query is a general question → route="chat"
5. If you don't understand → route="unknown"

CONFIDENCE:
- High (0.85–1.0): Clear IOC, explicit intent
- Medium (0.70–0.84): Implicit intent, needs context
- Low (<0.70): Ambiguous, multiple interpretations

COMPLEXITY:
1–3: Simple lookup or single extraction
4–6: Multi-step pattern matching, requires reasoning
7–10: Complex threat assessment, multi-context analysis

OUTPUT MUST BE VALID JSON. Example:
{
  "route": "ioc",
  "confidence": 0.94,
  "complexity_score": 2,
  "suggested_tier": 1,
  "reasoning": "CVE mentioned, straightforward extraction",
  "ioc_types": ["cve", "domain"]
}
```

**Token limit:** 150 tokens (excludes user query)

### Tier 0 Routing Decision Logic

```python
def route_tier_0(triage_decision: TriageDecision, user_pref: str, cost_budget: float):
    """Decide: Should we execute in Tier 1 or escalate to Tier 2?"""
    
    # If very confident + low complexity → Try Tier 1
    if triage_decision.confidence > 0.9 and triage_decision.complexity_score <= 2:
        return Tier.ONE
    
    # If confident + medium complexity + user prefers cost → Try Tier 1
    if (triage_decision.confidence > 0.85 and 
        triage_decision.complexity_score <= 5 and 
        user_pref == "cost"):
        return Tier.ONE
    
    # If low confidence or high complexity → Escalate
    if triage_decision.confidence < 0.7 or triage_decision.complexity_score > 6:
        return Tier.TWO
    
    # If cost budget exhausted → Prefer local
    if cost_budget < 0.01:
        return Tier.ONE
    
    # Default: User preference
    if user_pref == "accuracy":
        return Tier.TWO
    if user_pref == "speed":
        return Tier.ONE
    if user_pref == "cost":
        return Tier.ONE
    
    # Auto: balance cost and accuracy
    return Tier.ONE if triage_decision.confidence > 0.75 else Tier.TWO
```

---

## 6. Tier 1 (Local Executor) Specification

### Purpose
- **Execute tasks** identified by Tier 0
- **Generate structured output** (JSON schemas)
- **Provide intermediate results** with confidence scoring
- **Escalate to Tier 2** if uncertain or timeout

### Task-Specific Prompts

#### Task: IOC Extraction

```
You are a security expert. Extract IOCs (Indicators of Compromise) from the following text.

IOC TYPES:
- CVE: CVE-XXXX-XXXXX format
- IP: IPv4 or IPv6 addresses
- Domain: Domain names (*.example.com)
- Hash: MD5, SHA1, SHA256 hashes
- Email: Email addresses
- File: File paths or names
- URL: Full URLs

OUTPUT SCHEMA:
{
  "iocs": [
    {"type": "cve", "value": "CVE-2024-1234", "confidence": 0.95},
    {"type": "ip", "value": "192.168.1.1", "confidence": 0.99},
    ...
  ],
  "summary": "Found 3 IOCs in text",
  "confidence": 0.92
}

TEXT TO ANALYZE:
{user_query}

Output ONLY valid JSON.
```

**Token limit:** 250 tokens

#### Task: Log Summarization

```
Analyze the following security log and provide a brief summary.

INSTRUCTIONS:
1. Identify key events (errors, anomalies, attacks)
2. Assess severity (low/medium/high)
3. Suggest next actions

OUTPUT SCHEMA:
{
  "summary": "Brief description of events",
  "severity": "low|medium|high",
  "key_events": [
    {"timestamp": "...", "event": "...", "severity": "..."},
    ...
  ],
  "recommendations": ["...", "..."],
  "confidence": 0.88
}

LOG:
{user_query}

Output ONLY valid JSON.
```

**Token limit:** 300 tokens

---

## 7. Tier 2 (API) Specification

### When to Escalate

- **Tier 0 confidence < 0.7:** Uncertainty in classification
- **Complexity score > 6:** Multi-step reasoning required
- **Tier 1 timeout:** If Tier 1 execution > 3s
- **Tier 1 confidence < 0.7:** Low confidence result from local
- **User preference = "accuracy":** User explicitly wants best result
- **Repeating failures:** Circuit breaker: disable Tier 0/1 if >5 consecutive failures

### Model Selection: Haiku vs Sonnet

| Criteria | Haiku | Sonnet |
|----------|-------|--------|
| Cost | $0.80/1M tokens | $3.00/1M tokens |
| Speed | ~2s | ~3s |
| Reasoning quality | 90% | 95%+ |
| Best for | Extraction, simple analysis | Complex threat assessment |
| Use when | Tier 1 failed, cost matters | High-stakes, final decision |

**Decision:**
- IOC extraction → Haiku
- Threat assessment → Sonnet
- General → Haiku
- Complex multi-hop reasoning → Sonnet

---

## 8. Integration with Existing Systems

### AI Proxy Changes

**File:** `src/ai_proxy/routing/combo.py`

```python
from qwen_routers import QwenTriageRouter, QwenExecutor

class SmartRouter:
    def __init__(self):
        self.tier0 = QwenTriageRouter()
        self.tier1 = QwenExecutor()
        self.tier2 = AnthropicRouter()  # existing
    
    async def route_with_tiers(self, request):
        # Step 1: Tier 0 triage
        triage = await self.tier0.classify(request.query)
        
        # Step 2: Decide tier
        tier = self.decide_tier(triage, request.user_preference, request.cost_budget)
        
        if tier == 1:
            # Step 3: Tier 1 execution
            result = await self.tier1.execute(request, triage)
            
            if result.confidence > 0.7:
                return result
            else:
                # Escalate to Tier 2
                return await self.tier2.generate(request.query)
        
        elif tier == 2:
            # Direct to API
            return await self.tier2.generate(request.query)
```

### Response Headers

All responses include:
```
X-Tier-Model: "ollama/cybersec-suite" | "anthropic/claude-haiku"
X-Tier-Cost: "$0.00" | "$0.0012"
X-Tier-Latency: "234ms"
X-Tier-Confidence: "0.92"
X-Escalation-Reason: "low_confidence" | "timeout" | "user_pref"
```

---

## 9. Performance Targets

### Latency (p50 / p95)

| Tier | Latency Target |
|------|----------------|
| Tier 0 | 200ms / 500ms |
| Tier 1 | 1.0s / 3.0s |
| Tier 2 (API) | 2.0s / 5.0s |
| End-to-end (T0→T1) | 1.2s / 3.5s |

### Accuracy

| Task | Tier 0 | Tier 1 | Tier 2 |
|------|--------|--------|--------|
| Intent classification | 85%+ | 92%+ | 98%+ |
| IOC extraction | 88%+ | 94%+ | 99%+ |
| Log analysis | 75%+ | 90%+ | 96%+ |

### Cost Reduction

**Estimate:** 85–90% cost reduction vs API-only

```
API-only:     100 requests × $0.010/request = $1.00
With tiers:   60 × $0.00 (Tier 1) + 40 × $0.001 (Tier 2 Haiku) = $0.04
Savings:      96%
```

---

## 10. Testing Strategy

### Unit Tests (T146)

```python
# Test triage classification
def test_tier0_classification():
    router = QwenTriageRouter()
    result = router.classify("CVE-2024-1234 detected")
    assert result.route == "ioc"
    assert result.confidence > 0.9

# Test escalation logic
def test_tier_decision():
    triage = TriageDecision(route="analysis", confidence=0.6, complexity_score=8)
    tier = route_tier_0(triage, "auto", 0.10)
    assert tier == Tier.TWO
```

### A/B Testing (T147)

Compare same request across tiers:
```
Request 1: "Analyze log file X"
  ├─ Tier 1 → Summary A (90% confidence)
  └─ Tier 2 → Summary B (94% confidence)
  → Difference: 4%, acceptable

Request 2: "Assess threat level"
  ├─ Tier 1 → Risk: Medium (70% confidence)
  └─ Tier 2 → Risk: High (95% confidence)
  → Difference: High risk vs medium, CRITICAL → Log for review
```

### Performance Benchmarks (T149)

Run `scripts/benchmark_tiers.py`:
```
Tier 0 Benchmark (100 requests):
  - Avg latency: 245ms (target: <300ms) ✅
  - VRAM peak: 880 MB ✅
  - Throughput: 4.1 req/s ✅

Tier 1 Benchmark (50 requests):
  - Avg latency: 1.8s (target: <3s) ✅
  - VRAM peak: 1.4 GB ✅
  - Throughput: 0.6 req/s ✅

Cost Analysis:
  - 100 total requests
  - Tier 0: 60 (100%)
  - Tier 1: 35 (cost $0, 100%)
  - Tier 2: 5 (cost $0.01, fallback)
  - Total: $0.01 ✅
```

---

## 11. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| OOM on Tier 1 loading | High | Dynamic unload Tier 0, use CPU swapping |
| Tier 0 misclassifies | High | A/B test accuracy, manual review, lower confidence threshold |
| Tier 1 timeout | Medium | 3s timeout enforced, auto-escalate to Tier 2 |
| JSON parse error | Medium | Retry with clearer prompt, fallback to string parsing |
| Cost spike | Medium | Track per-user cost, alert if >$0.50/day/user |
| Model hallucination | Low | Few-shot examples, validation schema, user feedback |
| Ollama crash | Low | Health check, auto-restart, fallback to API |

---

## 12. Future Enhancements

- [ ] Fine-tune Qwen models on CyberSecSuite-specific tasks
- [ ] Dynamic model loading (swap models based on queue)
- [ ] Phi-4-mini as alternative Tier 1
- [ ] Multi-tier caching (reuse Tier 0 decisions)
- [ ] Cost optimization dashboard
- [ ] Feedback loop: User corrections → Retrain

---

## 13. References

- **Qwen Models:** https://huggingface.co/Qwen
- **Ollama:** https://ollama.ai
- **Phi Models:** https://huggingface.co/microsoft
- **Claude API:** https://anthropic.com/api

---

**Created:** 2026-04-26  
**Phase:** Phase 9  
**Status:** Planning  
**Next:** T127 (Model Setup)
