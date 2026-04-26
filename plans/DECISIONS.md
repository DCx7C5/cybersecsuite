# Architectural Decisions & Rationale

This document captures key decisions made during CyberSecSuite Infrastructure Modernization and their trade-offs.

---

## Decision 1: 6 MCPs Consolidation (Not 4, Not 10+)

**Decision:** Consolidate 87 monolithic tools into exactly 6 MCPs.

**Rationale:**
- **Too few (1-2 MCPs):** Would recreate monolithic problem; hard to maintain
- **Too many (15+):** Fragmentation; each MCP becomes thin wrapper
- **Sweet spot (6):** Each MCP has 1-22 modules, clear ownership, reusable

**MCPs:**
1. `csscore-mcp` (22 modules) — Foundation
2. `canvas-mcp` (6 modules) — Forensics visualization
3. `memory-mcp` (3 modules) — Vector memory
4. `template-mcp` (1 module) — Template rendering
5. `playwright-mcp` (13 modules) — Browser automation
6. `dystopian-crypto-mcp` (12 modules) — Cryptography

**Trade-off:**
- ✅ Each MCP independently maintainable
- ✅ Clear module grouping by function
- ❌ Requires inter-MCP communication (A2A protocol handles this)

**Status:** ✅ Implemented, proven in production

---

## Decision 2: csscore-mcp as Foundation (Not Separate microservices)

**Decision:** Make csscore-mcp the central hub, not break into separate services.

**Rationale:**
- Tight coupling between case management, findings, and intelligence (splitting breaks workflows)
- 22 modules still manageable in single MCP
- Reduces deployment complexity (fewer services = fewer failures)
- SDK mode allows external MCPs to call csscore via A2A

**Constraints Applied:**
- **File size:** ≤2 MB (strict, enforced in CI)
- **Test coverage:** 100% (prevents regressions in core)
- **Latency:** <100ms p95 (performance requirement)

**Trade-off:**
- ✅ Simpler deployment model
- ✅ Faster development iteration
- ✅ Clear ownership (csscore = the core)
- ❌ Single point of failure (mitigated by A2A fallback)

**Status:** ✅ Implemented, constraints enforced

---

## Decision 3: Skills Migration to Marketplace (Not Keep Locally)

**Decision:** Migrate 1,624 skills to ai-marketplace, remove from cybersecsuite.

**Rationale:**
- Skills are reusable across projects (not CSS-specific)
- Marketplace provides unified search/discovery
- Reduces CyberSecSuite repo size significantly
- Enables skill versioning independently

**Trade-off:**
- ✅ CyberSecSuite size: 1,624 → 0 skills (disk savings)
- ✅ Reusability: Skills usable by other AI agents
- ❌ Requires marketplace availability (fallback: local cache)

**Status:** ✅ Complete (Phase 9), 1,624 skills migrated

---

## Decision 4: SDK Mode Architecture (Not Embedded MCPs)

**Decision:** Externalize MCPs to separate processes/repos, use SDK mode.

**Rationale:**
- Allows independent scaling (each MCP can have own resource limit)
- Enables A2A protocol (agent-to-agent communication)
- Supports hot-reload of MCP without restarting CyberSecSuite
- Matches future serverless model (each MCP as Lambda)

**Implementation:**
- CyberSecSuite loads MCPs via `config/mcps.json` registry
- `scripts/deploy/install-mcp-core.sh` bootstraps setup
- Fallback to local if marketplace unavailable

**Trade-off:**
- ✅ Scalability: Independent processes
- ✅ Resilience: One MCP failure doesn't crash system
- ❌ Latency: Network overhead for inter-MCP calls

**Status:** ✅ Implemented in Phase 7

---

## Decision 5: 3-Tier CI/CD (PR/Main/Release) Not Monolithic

**Decision:** Split testing/deployment into 3 tiers with different rigor.

**Tiers:**
- **Tier 1 (PR):** ~9 min (fast linting, subset of tests)
- **Tier 2 (Main):** ~20 min (full tests, all browsers)
- **Tier 3 (Release):** ~35 min (coverage checks, performance baseline, security audit)

**Rationale:**
- Tier 1 provides fast feedback (devs don't wait 35+ min)
- Tier 2 catches issues before merge
- Tier 3 ensures release quality

**Trade-off:**
- ✅ Fast PR feedback (not blocked by full suite)
- ✅ Release confidence (comprehensive checks)
- ❌ Some bugs slip into main (Tier 2 will catch, Tier 3 blocks release)

**Status:** ✅ Implemented in Phase 11.7

---

## Decision 6: Marketplace Index Not Real-Time

**Decision:** Generate index.json during Phase 10, update manually.

**Rationale:**
- Real-time indexing would require background job (adds complexity)
- Manual updates sufficient for current volume (1,064 items)
- Can upgrade to real-time later if needed

**Trade-off:**
- ✅ Simpler implementation
- ✅ Predictable performance
- ❌ Index lag (new skills not visible until manual index)

**Status:** ✅ Index generated, 1,064 items searchable

---

## Decision 7: Browser Testing on Brave+Firefox (Not All Browsers)

**Decision:** Limit a11y/e2e testing to Brave and Firefox (per user guidance).

**Rationale:**
- User explicitly requested Brave+Firefox only
- Reduces test runtime significantly
- Covers both Chromium-based and independent engines

**Trade-off:**
- ✅ Faster tests
- ✅ Smaller CI matrix
- ❌ No Safari/Mobile coverage (accepted trade-off)

**Status:** ✅ Implemented in Phase 11.5

---

## Decision 8: Phase 12: Post-Modernization Cleanup

**Decision:** Add Phase 12 to cleanup redundant files and consolidate documentation.

**Rationale:**
- Phases 6-11 left behind test artifacts (htmlcov: 19 MB, coverage.json: 1.3 MB)
- Documentation scattered (50+ redundant items)
- Clean slate needed for future phases
- Scripts reorganization complete, should be archived

**Scope (10 phases):**
1. Verify marketplace migrations
2. Delete coverage artifacts (1.4 MB freed)
3. Delete backups/duplicates
4. Delete archived phase docs
5. Delete obsolete pre-consolidation docs
6. Delete build/test artifacts (20 MB freed)
7. Clean cache directories
8. Review .claude directory (1.9 MB optional)
9. Delete duplicate agents
10. Final commit

**Trade-off:**
- ✅ Cleaner repository
- ✅ 23-25 MB freed
- ❌ Irreversible (git history kept, but working copy clean)

**Status:** ⏳ Planned, ready for execution

---

## Decision 9: Planning Consolidation

**Decision:** Move all planning docs to `/plans/` as single source of truth.

**Rationale:**
- Session workspace is ephemeral (plans lost between sessions)
- Project repo is canonical (persists, versioned with git)
- Single location reduces confusion

**Structure:**
```
/plans/
├── README.md (navigation + governance)
├── plan.md (detailed execution specs)
├── ORCHESTRATOR_QUICK_REFERENCE.md (5-min overview)
├── PHASE_12_REDUNDANT_CLEANUP.md (cleanup spec)
├── PHASE_COMPLETED_SCRIPTS_REORGANIZATION.md (historical)
└── DECISIONS.md (this file)
```

**Trade-off:**
- ✅ Single source of truth
- ✅ Versioned with git
- ✅ Accessible to future phases
- ❌ Session workspace plans no longer used

**Status:** ✅ Complete (this phase)

---

## Impact Summary

| Decision | Risk | Benefit | Status |
|----------|------|---------|--------|
| 6 MCPs | Medium | High (maintainability) | ✅ Proven |
| csscore foundation | Medium | High (simplicity) | ✅ Proven |
| Skills to marketplace | Low | High (reusability) | ✅ Complete |
| SDK mode | Low | High (scalability) | ✅ Implemented |
| 3-tier CI/CD | Low | High (feedback speed) | ✅ Implemented |
| Manual indexing | Low | Medium (acceptable lag) | ✅ Acceptable |
| Brave+Firefox only | None | Medium (faster tests) | ✅ Per user request |
| Phase 12 cleanup | Very Low | Medium (cleanliness) | ⏳ Planned |
| Planning consolidation | Very Low | High (clarity) | ✅ Complete |

---

## Future Decisions (For Phase 13+)

If the project continues:

1. **Real-time indexing?** — When marketplace scales beyond 5,000 items
2. **Serverless MCPs?** — When deployment to AWS/GCP needed
3. **Multi-region?** — When geographic redundancy required
4. **A2A protocol v2?** — If agent-agent communication bottlenecks appear

---

**Last Updated:** 2026-04-27  
**Next Review:** After Phase 12 completion
