# Qwen3-0.6B Routing Layer: Quick Decision Guide

**Use this for fast reference during Phase 1-2 discussions.**

---

## Should We Use Qwen? Quick Flowchart

```
Question: Do we need a small-LLM routing layer?
├─ Phase 1a (Now): ModelExecutor extraction
│  └─ Answer: ❌ NO, skip for Phase 1a
│     Reason: Focus on core routing strategies first
│
├─ Phase 1b (Weeks 3-4): Observability baseline established?
│  └─ Answer: ⚠️ WAIT, needed but not yet
│     Reason: Need cost/latency baseline before Phase 2
│
└─ Phase 2+ (Weeks 5-8): After observability baseline
   └─ Answer: ✅ YES, implement Qwen triage layer
      Reason: Strong ROI ($50-100K/year), low risk, high value
```

---

## Decision Matrix: When to Use Qwen for Each Query

| Query Type | Should Triage? | Why | Expected Savings |
|-----------|---|---|---|
| "Is 192.0.2.5 a C2 server?" | ✅ YES | Urgency classification | $100-200 |
| "What's DNS?" | ✅ YES | Routine → local | $0.50-1 |
| "Analyze this binary" | ✅ YES | Artifact validation | $5-20 |
| "Check 50 IOCs" | ❌ NO | Complex, needs orchestration | N/A |
| "Explain MITRE ATT&CK" | ✅ YES | General knowledge → local | $1-2 |
| "Real-time incident" | ✅ YES | Urgent → fast provider | $50-100 |
| "API integration" | ❌ NO | Highly specific, needs context | N/A |

---

## Architecture: 1-Minute Explanation

**Current (Phase 1):**
```
User Request → ModelExecutor → Provider Selection → MCP Execution
```

**With Qwen (Phase 2):**
```
User Request → Qwen Triage → ModelExecutor → Provider Selection → MCP
                   ↓
            Classification + Routing Hint
```

**Key:** Qwen is upstream, adds context for smarter provider selection.

---

## Risk-Benefit Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Cost savings potential** | 🟢 HIGH | $50-100K/year |
| **Implementation complexity** | 🟢 LOW | ~80 hours |
| **Risk level** | 🟢 LOW | Graceful fallback |
| **Latency impact** | 🟢 LOW | +90ms average (with caching) |
| **Operational overhead** | 🟢 LOW | ~5h/month maintenance |
| **Strategic value** | 🟢 MEDIUM | Cost optimization, not critical |
| **OVERALL** | ✅ PROCEED | Phase 2 candidate |

---

## Fallback Strategy (Handles Failures)

```
If Ollama unavailable?
  → Skip triage layer
  → Use default routing strategy
  → Request proceeds normally
  → Log warning + metric

If Qwen confidence < 0.7?
  → Use default routing (skeptical)
  → Don't trust low-confidence classifications

If cache miss + latency > 500ms?
  → Timeout, use default routing
  → Continue in background for cache warming
```

**Result:** System never breaks, graceful degradation.

---

## Cost Comparison: Example Request

**Scenario:** User asks "What is DNS?" (routine knowledge)

| Route | Provider | Cost | Latency |
|-------|----------|------|---------|
| **Without Qwen** | GPT-4 (default) | $0.50-1.00 | 2-3s |
| **With Qwen** | Local Qwen | ~$0.00 | <1s |
| **Savings** | — | -90-100% | -66% |

**Qwen Triage Cost:** +100-200ms (one-time)  
**Net:** -$0.50-1.00, -66% latency → Worth it

---

## Prompt Engineering: 3-Tier Complexity

### Tier 1 (Week 1): Binary Classification
```
"Is this request URGENT or ROUTINE?"
Accuracy: ~85%
Examples: 3-5 per category
Tokens: ~400
```

### Tier 2 (Week 2): Multi-Class
```
"Classify: URGENT, ROUTINE, COMPLEX, VALIDATION, LOOKUP?"
Accuracy: ~80%
Examples: 10-15 total
Tokens: ~800
```

### Tier 3 (Week 3): Provider Routing
```
"Recommend: local, gpt-3.5, gpt-4, claude-sonnet, claude-opus?"
Accuracy: ~75%
Examples: 15-20 total
Tokens: ~1000
```

---

## Caching: Expected Impact

| Scenario | Hit Rate | Avg Latency | Bandwidth |
|----------|----------|-------------|-----------|
| **No cache** | 0% | 300ms | High |
| **With cache** | 70-85% | 90ms | Low |
| **Redis cache** | 70-85% | <1ms | Very Low |

**Recommendation:** Use Redis cache with 1-hour TTL.

---

## Operational Checklist (Phase 2)

**Pre-Implementation:**
- [ ] Ollama running locally (healthcheck: `curl http://localhost:11434/api/tags`)
- [ ] Redis operational (healthcheck: `redis-cli ping`)
- [ ] Phase 1b observability baseline complete
- [ ] Team aligned on use cases

**Implementation:**
- [ ] QwenClient wrapper (3-4 hours)
- [ ] TriageRouter logic (4-5 hours)
- [ ] Prompt templates (2-3 hours)
- [ ] Caching layer (2-3 hours)
- [ ] Integration tests (3-4 hours)

**Validation (Week 4):**
- [ ] A/B test on 10% traffic (48 hours)
- [ ] Monitor: cost savings, latency, accuracy
- [ ] Decision: roll out to 100% or iterate

**Total:** ~2 weeks, ~80 hours

---

## Metrics to Track

**Essential (Day 1):**
- `triage_classification_distribution` — How many URGENT vs ROUTINE?
- `triage_latency_ms` — 50th, 95th, 99th percentiles
- `triage_cache_hit_rate` — Should be 70-85%

**Important (Week 2):**
- `triage_cost_savings_usd` — Estimated savings vs. default routing
- `triage_confidence_distribution` — Are we confident in classifications?
- `ollama_availability_percent` — Is Ollama stable?

**Nice-to-Have (Week 3+):**
- `triage_accuracy_vs_user_feedback` — Did Qwen classify correctly?
- `provider_routing_breakdown` — Which providers are being selected?
- `fallback_frequency` — How often does Ollama go down?

---

## Common Concerns & Answers

| Concern | Answer |
|---------|--------|
| "Won't add latency?" | No, caching makes it <1ms for most requests |
| "What if Ollama crashes?" | Graceful fallback to default routing |
| "Is Qwen reliable?" | Moderate — validate with A/B test first |
| "Will it break existing routing?" | No, it's a separate layer |
| "How do we know it saves money?" | A/B test + metrics tracking |
| "Can we disable it?" | Yes, single toggle (environment variable) |
| "Is it worth Phase 2 effort?" | YES, 3-7x ROI in Year 1 |
| "What if Qwen gets it wrong?" | Confidence thresholds + fallback |

---

## Phase Comparison

| Aspect | Phase 1a | Phase 1b | Phase 2 | Phase 3+ |
|--------|----------|----------|---------|----------|
| **ModelExecutor** | ✅ Extract | ✅ Integrate | ✅ Use | ✅ Optimize |
| **Qwen Triage** | ❌ No | ⏳ Wait | ✅ Implement | ✅ Expand |
| **Observability** | 🟡 Partial | ✅ Complete | ✅ Monitor | ✅ Optimize |
| **A/B Testing** | ❌ No | ❌ No | ✅ Start | ✅ Ongoing |
| **Production Ready** | 🟡 MVP | ✅ Ready | ✅ Phase 2 | ✅ Mature |

---

## One-Page Decision Template

**Use this for approval/discussion:**

```
PROPOSAL: Implement Qwen3-0.6B Triage Layer (Phase 2)

ROI:
- Year 1 Cost: ~$13K (infra + engineering)
- Year 1 Benefit: $50-100K (cost savings)
- Net: +$37-87K (3-7x ROI)

RISK: 🟢 LOW
- Fallback: Skip triage if Ollama unavailable
- Testing: A/B test before full rollout
- Iteration: Start 1 use case, expand based on data

TIMELINE:
- Phase 1a: Skip (focus on ModelExecutor)
- Phase 1b: Wait for observability baseline
- Phase 2: Implement (2 weeks, 80 hours)
- Phase 3+: Optimize and expand

FIRST STEP:
1. Confirm Phase 1a focus
2. Schedule Phase 2 planning after Phase 1b
3. Setup Ollama infrastructure (parallel)

DECISION: ✅ PROCEED to Phase 2 implementation
```

---

## When to Say "NO" to Qwen

❌ **Don't implement Qwen if:**
- Phase 1a critical path is delayed
- No observability baseline established
- Ollama infrastructure not available
- Team skeptical about ROI (→ do pilot first)
- Security concerns about local LLM (→ evaluate separately)

✅ **Do implement Qwen if:**
- Phase 1a complete and stable
- Observability baseline shows cost patterns
- Ollama infrastructure ready
- A/B test framework in place
- Team aligned on use cases

---

## Reference Links

- **Full Analysis:** [`QWEN_ROUTING_ANALYSIS.md`](QWEN_ROUTING_ANALYSIS.md) (788 lines)
- **Implementation:** [`QWEN_IMPLEMENTATION_BLUEPRINT.md`](QWEN_IMPLEMENTATION_BLUEPRINT.md) (743 lines)
- **Executive Summary:** [`QWEN_EXECUTIVE_SUMMARY.md`](QWEN_EXECUTIVE_SUMMARY.md)
- **This Document:** [`QWEN_QUICK_DECISION_GUIDE.md`](QWEN_QUICK_DECISION_GUIDE.md) (Quick ref)

---

**Last Updated:** 2025 | **Status:** Ready for Phase 2 Planning | **Recommendation:** ✅ PROCEED

