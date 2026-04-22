# Phase 9 Reference Guide — Qwen Tiered Routing

**Quick Links & Key Documents**

---

## 📋 Master Plan

**File:** `plans/plan.md` (Line 706+)

**Key Sections:**
- Tier architecture overview
- 24 todos (T127–T150) with effort estimates
- Decision criteria matrix
- Performance targets & cost analysis
- Hardware optimization (GTX 1050 Ti)
- Risks & mitigations

**View:** `grep "Phase 9:" plans/plan.md -A 300`

---

## 📖 Comprehensive Architecture Document

**File:** `docs/architecture/qwen-tiered-routing-2026-04-26.md` (16 KB)

**Contains:**
1. **Executive Summary** — Project goals & benefits
2. **Why Qwen3.5?** — Comparison to alternatives (Phi, Llama)
3. **Architectural Design** — Data flow, capability matrix
4. **Hardware Optimization** — Memory strategy for 1050 Ti
5. **Tier 0 Specification** — Triage router spec, system prompt
6. **Tier 1 Specification** — Task-specific execution specs
7. **Integration Points** — How to modify AI proxy
8. **Performance Targets** — Latency, accuracy, cost
9. **Testing Strategy** — Unit, A/B, E2E, benchmarks
10. **Risks & Mitigations** — What can go wrong & how to prevent it

---

## 🎯 Implementation Todos

### Quick Access

**All Phase 9 Todos:**
```sql
SELECT * FROM todos WHERE id BETWEEN 't127' AND 't150' ORDER BY id;
```

**With Dependencies:**
```sql
SELECT t.id, t.title, COUNT(td.depends_on) as blocked_by
FROM todos t
LEFT JOIN todo_deps td ON t.id = td.todo_id
WHERE t.id BETWEEN 't127' AND 't150'
GROUP BY t.id
ORDER BY t.id;
```

### Todo Breakdown

#### Part A: Model Setup (T127–T132)
- **T127** — Add Qwen3.5-1.5B (4h)
- **T128** — Optimize for 1050 Ti (1h)
- **T129** — Create system prompts (1h)
- **T130** — Create Modelfiles (1h)
- **T131** — Capabilities matrix (30m)
- **T132** — GPU memory verification (30m)

#### Part B: AI Proxy (T133–T140)
- **T133** — Extend routing logic (2h)
- **T134** — Tier 0 router class (2h)
- **T135** — Tier 1 executor class (2h)
- **T136** — Update decision matrix (1h)
- **T137** — Error handling (1h)
- **T138** — Logging (30m)
- **T139** — Cost estimator (1h)
- **T140** — Diagnostics API (30m)

#### Part C: Prompt Engineering (T141–T145)
- **T141** — Prompt templates (1.5h)
- **T142** — JSON validation (1h)
- **T143** — Token optimization (30m)
- **T144** — Few-shot examples (1h)
- **T145** — Best practices guide (30m)

#### Part D: Testing (T146–T150)
- **T146** — Unit tests (2h)
- **T147** — A/B testing (1h)
- **T148** — E2E tests (1h)
- **T149** — Benchmarks (30m)
- **T150** — Monitoring docs (30m)

---

## 🔑 Key Files to Create/Modify

### New Files
```
src/ai_proxy/models/qwen_routers.py       — QwenTriageRouter, QwenExecutor classes
src/ai_proxy/prompts/tier_templates.py    — System prompts for all tiers
src/ai_proxy/schemas/tier_outputs.py      — Pydantic schemas
src/ai_proxy/logging/tier_decisions.py    — Tier decision logging
src/ai_proxy/testing/ab_test.py           — A/B testing framework
tests/unit/test_tier_routing.py           — Routing logic tests
tests/e2e/tier_routing.spec.ts            — Playwright E2E tests
scripts/benchmark_tiers.py                — Performance benchmarking
docs/architecture/model-capabilities.md   — Capability matrix & decisions
docs/development/prompt-engineering.md    — Prompt best practices
docs/deployment/routing-monitoring.md     — Metrics & dashboards
```

### Modified Files
```
src/ai_proxy/routing/combo.py             — Add route_with_tiers(), tier selection logic
docker-compose.yml                        — Add 1.5B model service (T127)
.docker/ollama/Modelfile-qwen-1.5b        — New Modelfile for 1.5B (T130)
```

---

## 💡 Key Concepts

### Tier Selection Logic
```
Request arrives
  ↓
Tier 0 (0.8B): Classify intent, assess complexity
  ├─ If confidence > 0.9 && complexity < 3 → Tier 1
  ├─ If confidence < 0.7 || complexity > 6 → Tier 2 (API)
  └─ Otherwise → User preference
  ↓
Tier 1 (1.5B): Execute task
  ├─ If confidence > 0.85 → Return result
  ├─ If confidence < 0.7 || timeout → Escalate to Tier 2
  └─ If timeout > 3s → Tier 2 (API)
  ↓
Tier 2 (Claude): Final authority
  └─ Complex reasoning, edge cases
```

### Cost Optimization
```
Request 1: "What is CVE-2024-1234?"
  → Tier 0: Route to IOC extraction
  → Tier 1: Extract (confidence 0.94)
  → Result: Cost $0.00, Latency 1.2s

Request 2: "Is this a ransomware attack?"
  → Tier 0: Complex forensics (complexity 8)
  → Tier 2: Send to Claude
  → Result: Cost $0.002, Latency 2.5s

100 requests: ~96% cost reduction vs API-only
```

### VRAM Strategy (1050 Ti)
```
Tier 0 (0.8B, 800 MB):  Always loaded
  ↓
On Tier 1 request:
  • Unload Tier 0 KV cache (free ~200 MB)
  • Load Tier 1 (1.2 GB)
  • Execute
  • Unload Tier 1
  • Reload Tier 0

Result: No OOM, dynamic memory management
```

---

## 🚀 Execution Plan

### Phase Sequence
```
Phase 7C (Sidebar)    ← NOW (8–10h)
    ↓
Phase 7D (Router)     ← NEXT (4–5h)
    ↓
Phase 8 (Ollama)      ← AFTER 7D (2–3h, T122–T126)
    ↓
Phase 9 (Qwen)        ← AFTER 8 (22–28h, T127–T150)
    ↓ Can run parallel with 7C-7D
    ↓
Phase 1 (QoL)         ← After 7D (8–10h, T002–T015)
```

### Critical Path for Phase 9
```
T127 (Model Setup)      [4h]     ← Start here
    ↓
T133–T135 (Core)        [4h]     ← After T127
    ↓ (Parallel: T141 Prompts)
T146–T148 (Testing)     [4h]     ← After T135
    ↓
T150 (Monitoring)       [1h]     ← Final
```

**Wall time: ~12–14 hours (with parallelization)**

---

## 📊 Decision Matrix

**When to use each tier:**

| Scenario | Tier 0 | Tier 1 | Tier 2 |
|----------|--------|--------|--------|
| Simple IOC lookup | ✅ | — | — |
| Classification | ✅ | — | — |
| Log summarization | — | ✅ | — |
| Pattern matching | — | ✅ | — |
| Threat assessment | — | — | ✅ |
| Complex reasoning | — | — | ✅ |
| High accuracy required | — | — | ✅ |
| Cost optimization | ✅ | ✅ | — |
| Speed required | ✅ | — | — |

---

## 🔍 Performance Targets

### Latency (p50 / p95)
- **Tier 0:** 200ms / 500ms
- **Tier 1:** 1.0s / 3.0s
- **Tier 2 (API):** 2.0s / 5.0s

### Accuracy
| Task | Tier 0 | Tier 1 | Tier 2 |
|------|--------|--------|--------|
| Intent classification | 85%+ | 92%+ | 98%+ |
| IOC extraction | 88%+ | 94%+ | 99%+ |
| Log analysis | 75%+ | 90%+ | 96%+ |

### Cost (per 100 requests)
- **API-only:** $1.00
- **With tiering:** $0.04
- **Savings:** 96%

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| OOM on 1050 Ti | Dynamic loading, CPU swap, monitoring |
| Tier 0 misclassification | A/B testing, confidence threshold, manual review |
| Tier 1 timeout | 3s timeout enforced, auto-escalate |
| JSON parse error | Retry, schema validation, fallback parsing |
| Cost spike | Budget tracking, alerting, prioritize local |
| Hallucinations | Few-shot examples, schema validation |

---

## 📚 References

### Models
- **Qwen3.5:** https://huggingface.co/Qwen
- **Ollama:** https://ollama.ai
- **Phi Models:** https://huggingface.co/microsoft
- **Claude API:** https://anthropic.com/api

### Documentation
- **Main Plan:** `plans/plan.md`
- **Architecture:** `docs/architecture/qwen-tiered-routing-2026-04-26.md`
- **Phase 8 (Ollama):** `docs/getting-started/ollama-model-setup-plan-2026-04-26.md`
- **Changelog:** `docs/changelog/ollama-model-auto-setup-2026-04-26.md`

---

## 🎓 Quick Start Checklist

### Before Starting Phase 9
- [ ] Phase 7C (Sidebar) complete
- [ ] Phase 7D (React Router) complete
- [ ] Phase 8 (Ollama Setup) Phase 1-2 complete
- [ ] SQLite database ready
- [ ] Docker environment ready

### Starting Phase 9 (T127)
1. Add Qwen3.5-1.5B to Ollama
2. Benchmark on 1050 Ti
3. Create docker-compose service
4. Verify health checks
5. Create Modelfiles
6. Test model loading

### Continuing Phase 9 (T133)
1. Extend `combo.py` routing
2. Implement tier classes
3. Add system prompts
4. Create response headers
5. Add error handling

### Testing Phase 9 (T146)
1. Write unit tests
2. Run A/B comparison
3. Create E2E tests
4. Run performance benchmarks
5. Document results

---

## 📞 Questions?

Refer to:
- `docs/architecture/qwen-tiered-routing-2026-04-26.md` — Comprehensive guide
- `plans/plan.md` (Line 706+) — Phase 9 details
- SQL database — todos, dependencies, status

---

**Created:** 2026-04-26  
**Phase:** Phase 9  
**Status:** Planning → Ready for Implementation  
**Next Todo:** T127 (Model Setup)
