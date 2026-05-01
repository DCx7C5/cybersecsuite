# Rubber-Duck Analysis: Qwen3-0.6B Routing Layer for CyberSecSuite
**Date:** 2025 | **Phase:** 1a (ModelExecutor) | **Status:** Architectural Feasibility Study

---

## Executive Summary

**Question:** Should CyberSecSuite use Qwen3-0.6B (local, <1s latency) as a routing/triage layer before expensive cloud calls?

**Rubber-Duck Recommendation:** ✅ **YES, but only for specific use cases in Phase 2+** (not Phase 1a critical path)

- **Phase 1a Priority:** Focus on ModelExecutor extraction, provider registry, core routing strategies (existing 13 strategies)
- **Phase 2 Optimization:** Layer in Qwen triage for cost optimization, not decision framework
- **Risk Level:** LOW if properly isolated; MEDIUM if coupled to core routing logic
- **Latency Impact:** ~200-500ms overhead acceptable *only* for non-critical-path decisions (filtering, validation, classification)

---

## 1. Architecture Fit Analysis

### 1.1 Current State: Where Does It Fit?

**CyberSecSuite 7-Layer Architecture:**
```
Layer 1 (API)     ← User request comes in
Layer 2 (Routing) ← [13 strategies] select provider/model 
Layer 3 (Orch)    ← A2A protocol coordinates agents
Layer 4 (MCP)     ← 6 MCPs execute forensic tools
Layer 5 (Logic)   ← Business logic (IOC extraction, analysis)
Layer 6 (Data)    ← SQLite, vector memory
Layer 7 (Storage) ← Artifacts, configs
```

**Qwen Routing Layer Position:**
```
Layer 1.5 (Triage) ← [NEW] Qwen3-0.6B classifies request
  ↓
Layer 2 (Routing)  ← ModelExecutor decides provider/model (existing)
```

### 1.2 Architecture Decision: SEPARATE or EMBEDDED?

**Option A: Separate Triage Layer (Recommended)**
```
┌─────────────────────────────────────────┐
│         User Request (HTTP)             │
└─────────────────────┬───────────────────┘
                      │
                ┌─────▼──────────┐
                │ TRIAGE LAYER   │  (NEW)
                │ Qwen3-0.6B     │
                │ - Classify     │
                │ - Filter       │
                │ - Validate     │
                └─────┬──────────┘
                      │
            ┌─────────▼────────────┐
            │  ModelExecutor       │  (EXISTING)
            │ - Select provider    │
            │ - Retry logic        │
            │ - Error mapping      │
            └─────────┬────────────┘
                      │
            ┌─────────▼────────────┐
            │   Orchestrator       │  (EXISTING)
            │   A2A + MCP routing  │
            └──────────────────────┘
```

**Pros:**
- ✅ Loose coupling, no changes to ModelExecutor critical path
- ✅ Can disable/fallback without affecting routing logic
- ✅ Testable in isolation
- ✅ Clear responsibility boundary

**Cons:**
- ⚠️ Extra network hop (local Ollama → response)
- ⚠️ Requires new error handling for triage failures

**Option B: Embedded in ModelExecutor** ❌ Not recommended
- Couples core routing logic to ML inference (higher risk)
- Complicates testing of routing strategies
- Creates dependency on Ollama availability for all requests
- Violates single-responsibility principle

**Decision:** **Option A (Separate Triage Layer)** — Lower risk, cleaner boundaries.

### 1.3 Critical Path Assessment

**Phase 1a Critical Path:** `ModelExecutor extraction + core routing`
- Does NOT depend on Qwen triage
- Qwen is Phase 2+ optimization layer

**Non-Critical Path (Acceptable overhead):** 
- Triage decisions (classification only)
- Validation (yes/no checks)
- Filtering (pre-call validation)

**Critical Path (UNACCEPTABLE overhead):**
- Core routing logic (provider selection)
- Retry decisions
- Error mapping

**Verdict:** Qwen fits cleanly in non-critical path. ✅

---

## 2. CyberSecSuite-Specific Use Cases

### 2.1 HIGH-VALUE Triage Use Cases

#### **Case 1: IOC Classification & Urgency Detection**
```
Input:  "I found 192.0.2.5 communicating with my database server"
Qwen:   ► Classification: active_incident (urgent)
        ► Route to: Claude Opus + immediate response
        ► Reasoning: Real-time threat indicator
        
vs.

Input:  "What are the DNS record types?"
Qwen:   ► Classification: general_knowledge (routine)
        ► Route to: Qwen local or GPT-3.5 (cheaper)
        ► Reasoning: Reference material, no urgency
```

**Value:** 40-60% cost savings on routine queries (no expensive cloud call needed).
**Latency:** +300ms acceptable for initial classification.

#### **Case 2: Artifact Validation Before Deep Analysis**
```
Input:  User uploads "suspicious_binary.exe"
Qwen:   ► Binary scan: Is this actually malware? (heuristic check)
        ► If low confidence → Skip expensive sandbox run
        ► If high confidence → Route to VirusTotal + analysis
```

**Value:** Avoid unnecessary expensive API calls for obvious safe files.
**Latency:** +100-200ms worth it to save $5-20 per false positive.

#### **Case 3: Log Line Parsing & Triage**
```
Input:  "10.0.0.5 - - [29/Apr] "GET /api/users" 200 1234"
Qwen:   ► Extract: IP, method, status, timestamp
        ► Classify: normal_web_traffic (routine)
        ► Or classify: 403_error_spike (alert-worthy)
        ► Route accordingly
```

**Value:** Fast filtering of noise from security logs (99% are benign).
**Latency:** +200ms acceptable for batch log processing.

#### **Case 4: Domain/Email Validation**
```
Input:  "Is 'thisis-definitely-a-phishing-domain.tk' a legitimate domain?"
Qwen:   ► Binary decision: No (confidence: 0.95)
        ► Skip expensive DNS + reputation checks
        ► Flag as suspicious immediately
```

**Value:** Block obvious scams without cost/latency of external reputation API.
**Latency:** +50ms completely acceptable.

#### **Case 5: Request Complexity Assessment**
```
Input:  Multi-part forensic query with 50 IOCs, 3 file uploads, 5 analysis requests
Qwen:   ► Complexity: extreme
        ► Decompose into: 5 smaller requests
        ► Route each to appropriate tier
        ► Estimated cost: $150 (vs. $400 if sent to single expensive model)
```

**Value:** Intelligent request decomposition → 60% cost savings.
**Latency:** +500ms acceptable (one-time upfront cost).

### 2.2 MEDIUM-VALUE Use Cases (Lower Priority)

- **Tone detection:** Urgent vs. routine (routing to priority queue)
- **Required output format detection:** JSON vs. text vs. markdown → auto-format
- **Tool requirement prediction:** "Will need VirusTotal?" → Pre-fetch
- **Language detection:** Multi-language support routing

### 2.3 NOT SUITABLE (Don't Use Qwen For These)

❌ **Core routing decisions** — Model selection needs full context, use existing 13 strategies  
❌ **Security validations** — Taint analysis, credential detection (use hardened checks)  
❌ **Compliance checks** — GDPR/data handling (rule-based only)  
❌ **Error recovery** — Already handled by retry layer  

---

## 3. Implementation Concerns & Mitigations

### 3.1 Latency Budget

**Current System Latency Baseline:** 
- ModelExecutor call: ~50-100ms (provider selection)
- MCP execution: ~500-5000ms (actual forensics work)
- **Total P95:** ~1-5 seconds

**Qwen Latency Impact:**
```
Qwen3-0.6B on CPU (typical):
- Model load: ~50ms (cached)
- Inference: ~150-300ms
- Post-processing: ~50-100ms
- Total per call: ~200-500ms

Added to total latency: +200-500ms
As % of system P95: +4-50%
```

**Latency Recommendation:**
- ✅ **Acceptable:** Triage decisions (once per request, ~200-300ms added)
- ⚠️ **Borderline:** Used for every request without caching (~300-500ms)
- ❌ **Unacceptable:** Used in retry loops or per-token classification

**Mitigation:** Cache triage decisions by request type hash
```python
cache_key = hash(request_type, user_intent)  # ~95% hit rate
if cached_route := get_route_from_cache(cache_key):
    return cached_route  # <1ms
else:
    route = await triage_with_qwen(request)  # ~300ms
    cache_route(cache_key, route)
    return route
```

### 3.2 Fallback Strategy When Ollama Down

**Option 1: Skip Triage, Use Default Route** ✅ (Recommended)
```python
try:
    triage_result = await qwen_triage(request)
    route = apply_triage_decision(triage_result)
except OllamaUnavailableError:
    logger.warning("Ollama unavailable, using default routing strategy")
    route = default_routing_strategy(request)  # Use existing Layer 2 logic
    return route  # Request proceeds normally, just slower
```

**Pros:**
- Graceful degradation, request still succeeds
- No user-facing errors
- Measured in logging/metrics

**Cons:**
- Cost optimization lost (route to expensive provider)
- User doesn't know they got suboptimal routing

**Option 2: Fail Fast, Return Error**  ❌ (Not recommended)
- Breaks user experience for non-critical requests
- Violates "graceful degradation" principle

**Decision:** **Option 1** — Skip triage layer, use default routing.

### 3.3 Caching Routing Decisions

**When to Cache:**
- Request type classification (e.g., "IOC lookup urgent?")
- Domain validation results
- Artifact metadata (malware classification)
- Complexity assessment

**When NOT to Cache:**
- Real-time threat status (may change between requests)
- User preference changes (settings update)
- Time-sensitive events (current time matters)

**Cache Strategy:**
```python
# Cache triage decisions by (request_type, request_hash)
class TriageCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, TriageDecision] = {}
        self.ttl = ttl_seconds
    
    def get_route(self, request_hash: str) -> Optional[TriageDecision]:
        """Get cached route if exists and not expired."""
        if request_hash in self.cache:
            decision, timestamp = self.cache[request_hash]
            if time.time() - timestamp < self.ttl:
                return decision
            else:
                del self.cache[request_hash]
        return None
    
    def cache_route(self, request_hash: str, decision: TriageDecision):
        """Cache triage decision for 1 hour."""
        self.cache[request_hash] = (decision, time.time())
```

**Expected Cache Hit Rate:** ~70-85% for typical forensics workflows

### 3.4 Model Prompt Engineering

**Key Challenge:** Qwen is tiny (600M params) → must use very tight, focused prompts

**Prompt Template Structure:**
```
Few-shot examples + system role + task + constraints
(Keep under 500 tokens total)

Example for IOC Classification:
─────────────────────────────────
SYSTEM ROLE:
You are a cybersecurity triage agent. Classify incoming requests 
into one of: URGENT, ROUTINE, or COMPLEX.

TASK:
Classify this security request and recommend which provider tier:
- URGENT (active incidents): Claude Opus / OpenAI GPT-4
- ROUTINE (general knowledge): Local Qwen / GPT-3.5
- COMPLEX (decomposition needed): Claude Opus (orchestrator)

EXAMPLES:
1. "I found 192.0.2.5 contacting C2 server" → URGENT (Opus)
2. "What's a DNS record?" → ROUTINE (Local)
3. "Analyze these 50 IOCs across 3 threat actors" → COMPLEX (Opus)

CONSTRAINTS:
- Answer in 1-2 sentences max
- Start with classification: [URGENT|ROUTINE|COMPLEX]
- Then provider recommendation
- Keep reasoning under 100 tokens

REQUEST:
{user_request}

CLASSIFICATION:
─────────────────────────────────
```

**Few-Shot Examples (Recommended):**
Create labeled examples for each use case (5-7 per category):
```python
TRIAGE_EXAMPLES = {
    "urgent": [
        ("Found malware on production server", "URGENT → Opus"),
        ("Active DDoS attack ongoing", "URGENT → Opus"),
    ],
    "routine": [
        ("What's the OSI model?", "ROUTINE → Local"),
        ("Explain MITRE ATT&CK", "ROUTINE → Local"),
    ],
    "complex": [
        ("Investigate APT28 infrastructure", "COMPLEX → Opus orchestrator"),
    ],
}
```

### 3.5 Token Cost Tracking

**Local Qwen: Zero API cost, but compute cost:**
```
Infrastructure cost:
- Ollama process: ~500MB RAM, ~5-10% CPU per inference
- Can run on: Laptop, small VM, GPU if available
- Annual cost (1 GPU): ~$3,000 (amortized)
- Per inference: ~$0.000001 (amortized)

Savings comparison:
- GPT-3.5: $0.50/1M input tokens → $0.0005 per 1K-token classification
- Claude: $3/1M input tokens → $0.003 per 1K-token classification
- Qwen local: Free (amortized hardware cost)

ROI if 30% of requests skip expensive calls:
- 1,000 requests/day = 300 skipped expensive calls
- 300 × $0.50 (GPT-3.5 savings) = $150/day
- $150/day × 365 = $54,750/year savings
```

**Recommendation:** Track as "triage overhead" in observability (compute usage), not token cost.

---

## 4. Risk Assessment

### 4.1 Silent Failures (Qwen Returns Wrong Classification)

**Risk:** Qwen classifies "active malware" as "routine" → routed to cheap provider → slow response

**Mitigation:**
1. **Confidence Score Threshold**
   ```python
   triage_confidence = qwen_triage(request)
   if triage_confidence < 0.7:
       # Low confidence, fall back to expensive provider
       route = expensive_provider
   ```

2. **Validation Layer**
   ```python
   # Post-triage validation
   if triage_result == "urgent":
       # Additional validation before expensive call
       is_really_urgent = validate_urgency(request)
       if not is_really_urgent:
           log_warning("Qwen classification mismatch")
           route = normal_provider
   ```

3. **User Feedback Loop**
   - Allow users to report "misclassified requests"
   - Retrain Qwen or adjust confidence thresholds based on feedback

**Risk Level:** MEDIUM → MITIGATED with confidence thresholds

### 4.2 Performance Regression (Extra 200-500ms Latency)

**Risk:** Every request adds 200-500ms → unacceptable for real-time forensics

**Mitigation:**
1. **Conditional Triage** — Only triage for specific request types:
   ```python
   if request_type in ["ioc_lookup", "artifact_validation", "domain_check"]:
       route = await qwen_triage(request)
   else:
       route = default_routing(request)
   ```

2. **Caching** — Hit rate ~70-85%, most requests <1ms
   ```
   Cache hit: ~1ms latency
   Cache miss: ~300ms latency
   Average: ~90ms latency (much better than 300ms)
   ```

3. **Async Processing** — Run triage in background while doing other work:
   ```python
   # Parallel execution
   triage_task = asyncio.create_task(qwen_triage(request))
   auth_task = asyncio.create_task(check_auth(user))
   
   auth_result = await auth_task  # ~50ms
   triage_result = await triage_task  # ~300ms, overlapped
   # Total latency: ~300ms (not 350ms)
   ```

**Risk Level:** LOW → Mitigated with caching + async + selective enablement

### 4.3 Token Cost Explosion

**Risk:** Qwen prompts are inefficient → use 10K tokens per call

**Mitigation:**
1. **Prompt Engineering** — Few-shot examples reduce token usage:
   ```
   Without examples: 800 tokens
   With 3 examples: 1,200 tokens (only +50% not +100%)
   ```

2. **Token Budgeting**
   ```python
   MAX_TRIAGE_TOKENS = 1000  # Hard limit
   if prompt_tokens > MAX_TRIAGE_TOKENS:
       skip_triage()
   ```

3. **Local-Only Execution** — Qwen runs locally → no token cost

**Risk Level:** LOW → Mitigation: run locally, not via API

---

## 5. Priority in Roadmap

### Timeline Recommendation:

```
PHASE 1a (Weeks 1-2): ModelExecutor Extraction
├─ Extract decision framework
├─ Implement core routing strategies (13 existing)
├─ Setup redis cache + error mapping
├─ Setup retry logic
└─ Status: DO NOT include Qwen yet

PHASE 1b (Weeks 3-4): Core Infrastructure Complete
├─ Integrate capability registry
├─ Provider fallback logic
├─ Observability baseline
└─ Status: Ready for Qwen integration

PHASE 2 (Weeks 5-8): Qwen Routing Layer [OPTIONAL OPTIMIZATION]
├─ Setup local Ollama (if not already running)
├─ Implement triage layer (separate from ModelExecutor)
├─ Add prompt engineering for 3-4 use cases
├─ Setup caching layer
├─ Integration tests
├─ Monitor cost/latency impact
└─ Status: Deploy after observability baseline established

PHASE 3+ (Post-launch optimization)
├─ Refine prompts based on production data
├─ Add more triage use cases
├─ Integrate with vault (forensic knowledge base)
└─ Status: Continuous optimization
```

### Why Phase 2+, Not Phase 1a?

1. **Phase 1a is about extraction and core logic** — Keep the critical path clean
2. **Phase 1b provides observability baseline** — Measure actual latency/cost without Qwen
3. **Phase 2 optimizes on data** — Use real production metrics to justify Qwen investment
4. **Blocks:** None. Qwen doesn't block any Phase 1a deliverables
5. **Priority:** Nice-to-have (cost optimization), not essential for MVP

### Is It Essential for Production?

**NO** — CyberSecSuite works fine without Qwen:
- Existing 13 routing strategies handle provider selection
- Retry logic handles failures
- Error mapping handles edge cases

**Qwen is a cost/latency optimizer**, not a critical feature. Launch Phase 1 without it, add in Phase 2 based on production data.

---

## 6. Recommendations & Best Practices

### 6.1 Prompt Engineering Framework

**Start Simple, Iterate:**

1. **Phase 2a: Binary Classification** (Week 1)
   ```
   Prompt: "Is this request URGENT or ROUTINE?"
   Labels: [URGENT, ROUTINE]
   Examples: 3-5 per category
   Expected accuracy: ~85-90%
   ```

2. **Phase 2b: Multi-Class Classification** (Week 2)
   ```
   Prompt: "Classify request intent: [URGENT, ROUTINE, COMPLEX, VALIDATION, LOOKUP]"
   Labels: 5 categories
   Examples: 10-15 total
   Expected accuracy: ~80-85%
   ```

3. **Phase 2c: Provider Routing** (Week 3)
   ```
   Prompt: "Recommend provider tier for this request"
   Labels: [local, gpt35, gpt4, claude-sonnet, claude-opus]
   Examples: 15-20 total
   Expected accuracy: ~75-80%
   ```

**Validation Strategy:**
```python
# A/B test: Qwen vs. default routing
if random.random() < 0.1:  # 10% of requests
    route_qwen = await qwen_triage(request)
    route_default = default_routing(request)
    
    # Compare which saved more money
    cost_qwen = estimate_cost(route_qwen)
    cost_default = estimate_cost(route_default)
    
    log_metric("triage_savings", cost_default - cost_qwen)
```

### 6.2 Example Prompts for Each Use Case

#### **Use Case 1: IOC Urgency Classification**
```
SYSTEM:
You are a cybersecurity incident triage agent. Classify each IOC 
sighting by urgency level.

LABELS:
- CRITICAL: Active exploitation, ongoing attack, data exfiltration
- HIGH: Suspicious activity, malware detected, potential compromise
- MEDIUM: Detected anomaly, failed auth attempts, policy violation
- LOW: Informational, historical data, known FP

EXAMPLES:
1. "Found 192.0.2.5 C2 connection in prod firewall logs" → CRITICAL
2. "Noticed 10.0.0.0/8 in VirusTotal results" → LOW (internal network)
3. "Domain registered 2 hours ago with IoCs" → HIGH

REQUEST: {ioc_context}

CLASSIFICATION:
```

#### **Use Case 2: Domain/Email Validation**
```
SYSTEM:
Validate if domain/email looks suspicious.

LABELS:
- LEGITIMATE: Known good, well-known TLD, proper format
- SUSPICIOUS: Typosquatting, uncommon TLD, homograph similarity
- MALICIOUS: Known phishing, known C2, blocklist match

EXAMPLES:
1. "microsoft.com" → LEGITIMATE
2. "microsof t.com" (space) → SUSPICIOUS
3. "μicrosoft.com" (Greek mu) → SUSPICIOUS
4. "totallyfakebank.tk" → SUSPICIOUS

REQUEST: {domain_or_email}

CLASSIFICATION:
```

#### **Use Case 3: Request Complexity**
```
SYSTEM:
Assess if request can be handled by local LLM or needs orchestration.

LABELS:
- SIMPLE: Single IOC lookup, one tool, <5 min response
- MODERATE: Multi-part request, 2-3 tools, cross-reference needed
- COMPLEX: Full investigation, artifact analysis, requires coordination

EXAMPLES:
1. "What's an IP?" → SIMPLE (local)
2. "Analyze this file and get reputation" → MODERATE (2 tools)
3. "Investigate APT28 infrastructure across 50 IOCs" → COMPLEX (orchestration)

REQUEST: {user_request}

COMPLEXITY:
```

### 6.3 Test Cases for Validation

**Unit Tests:**
```python
def test_triage_urgency_classification():
    """Qwen correctly identifies urgent requests."""
    urgent_requests = [
        "Found ransomware on production server",
        "Active data exfiltration detected",
        "Credentials compromised in real-time",
    ]
    for req in urgent_requests:
        result = triage_urgency(req)
        assert result["classification"] == "URGENT"

def test_triage_fallback_when_ollama_down():
    """Graceful degradation if Ollama unavailable."""
    with mock.patch("ollama.generate", side_effect=ConnectionError):
        result = triage(request)
        assert result["provider"] == "default_provider"
        assert result["fallback_reason"] == "ollama_unavailable"

def test_triage_cache_hit():
    """Cached classifications return <5ms."""
    cache.set("req_hash_123", {"classification": "ROUTINE"})
    start = time.time()
    result = triage(request_hash="req_hash_123")
    elapsed = time.time() - start
    assert elapsed < 0.005  # <5ms
    assert result["classification"] == "ROUTINE"
    assert result["source"] == "cache"
```

**Integration Tests:**
```python
@pytest.mark.integration
async def test_triage_cost_savings():
    """Qwen triage saves money vs. default routing."""
    request = create_test_request("routine_question")
    
    # Route with triage
    route_with_triage = await triage_router(request)
    cost_with_triage = estimate_cost(route_with_triage)
    
    # Route without triage
    route_without_triage = default_router(request)
    cost_without_triage = estimate_cost(route_without_triage)
    
    # Triage should save money
    assert cost_with_triage <= cost_without_triage
    assert savings_metric.record(cost_without_triage - cost_with_triage)

@pytest.mark.integration
async def test_triage_latency_impact():
    """Triage adds <300ms overhead."""
    start = time.time()
    result = await triage(request)
    elapsed = time.time() - start
    assert elapsed < 0.3  # <300ms
```

**A/B Test (Production):**
```python
def ab_test_triage_accuracy():
    """10% of requests routed both ways, compare outcomes."""
    test_group = random.sample(0.1)  # 10% test group
    
    for request in test_group:
        route_a = default_router(request)
        route_b = await triage_router(request)
        
        # Execute both
        result_a = execute(route_a)
        result_b = execute(route_b)
        
        # Compare:
        # - Cost delta
        # - Latency delta
        # - User satisfaction
        log_ab_result(route_a, route_b, result_a, result_b)
```

---

## 7. Implementation Checklist (Phase 2)

### Pre-Implementation
- [ ] Ensure Ollama running locally (separate playbook)
- [ ] Baseline latency/cost metrics established (Phase 1b)
- [ ] Redis cache fully operational
- [ ] Observability (OTEL) instrumented

### Core Implementation
- [ ] Triage service module (`src/core/triage/router.py`)
- [ ] Qwen client wrapper (`src/core/triage/qwen_client.py`)
- [ ] Prompt templates (`src/core/triage/prompts.py`)
- [ ] Triage cache layer (`src/core/triage/cache.py`)
- [ ] Error handling + fallback logic

### Testing
- [ ] Unit tests for triage logic
- [ ] Integration tests with Qwen
- [ ] Fallback tests (Ollama down)
- [ ] Cache effectiveness tests
- [ ] Latency budget validation

### Observability
- [ ] Metrics: triage_classification_distribution
- [ ] Metrics: triage_latency_ms
- [ ] Metrics: triage_cost_savings_usd
- [ ] Metrics: triage_cache_hit_rate
- [ ] Traces: triage request/response
- [ ] Alerts: triage service failures

### Documentation
- [ ] Architecture decision record (ADR)
- [ ] Operational runbook (Ollama management)
- [ ] Prompt engineering guide
- [ ] Cost/benefit analysis update

---

## 8. Conclusion: Rubber-Duck Verdict

### ✅ RECOMMENDED: Proceed with Phase 2 Qwen Integration

**Rationale:**
1. **Architectural fit is clean** — Separate layer, no coupling to core routing
2. **Use cases are strong** — 30-60% cost savings likely on routine queries
3. **Risk is low** — Graceful fallback if Ollama down
4. **Latency is acceptable** — 200-500ms overhead for non-critical path
5. **Easy to iterate** — Start simple (binary classification), add complexity

**However:**
- **Not critical for Phase 1a** — Focus on ModelExecutor extraction first
- **Requires observability baseline** — Know your real costs/latency before optimizing
- **Measure before optimizing** — A/B test to prove value

### 📋 Next Steps:
1. **Phase 1a:** Focus on ModelExecutor + core routing (no Qwen)
2. **Phase 1b:** Establish observability baseline + cost tracking
3. **Phase 2:** Implement Qwen triage layer with A/B testing
4. **Phase 3+:** Refine based on production data, expand use cases

---

## Appendix: Quick Reference

| Aspect | Recommendation |
|--------|---|
| **Architecture** | Separate triage layer (not embedded) |
| **Fallback** | Skip triage, use default routing if Ollama down |
| **Caching** | Yes, expect ~70-85% hit rate |
| **Latency** | Acceptable: 200-500ms added to triage decision |
| **Phase** | Phase 2+ (not Phase 1a critical path) |
| **Priority** | Nice-to-have optimization (cost), not essential |
| **Risk Level** | LOW (with mitigations) |
| **ROI** | $50K-100K+/year (depending on usage) |
| **Start With** | 1 use case (IOC urgency), expand iteratively |
| **Test Strategy** | A/B test + production metrics before full rollout |

