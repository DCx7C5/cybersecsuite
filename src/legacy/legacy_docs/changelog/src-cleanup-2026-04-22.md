# src/ Cleanup & Architecture Flowchart

**Date:** 2026-04-22  
**Type:** refactor / housekeeping  
**Scope:** file moves, renames, dead code removal, documentation

---

## Summary

Audit of `src/` identified misplaced files, stale/dead code, a misleadingly named module, and documentation living inside Python packages. All issues resolved. Full 19-layer Mermaid architecture flowchart created.

---

## Changes

### Scripts moved to `scripts/`

- `fix_skills.py` → `scripts/fix_skills.py`
- `worktree-session-manager.py` → `scripts/worktree-session-manager.py`

Updated references:
- `tests/test_worktree_manager.py` (lines 28, 553) — path adjusted
- `tests/test_llm_orchestrator.py` (line 428) — path adjusted
- `scripts/gwt-aliases.sh` — echo path adjusted
- `src/llm/db.py` — comment updated

### Module renamed

- `src/dashboard/api/opensearch_stats.py` → `openobserve_stats.py`
  - File served OpenObserve stream stats, not OpenSearch
  - `src/dashboard/api/__init__.py` import updated

### Hook documentation moved

6 `.md` files moved from `src/hooks/` (inside a Python package) to `docs/hooks/`:
- `RootCommandExecuted.md`
- `SessionEnd.md`
- `SessionStart.md`
- `YaraRuleGeneration.md`
- `YaraRuleOptimization.md`
- `YaraRuleTesting.md`

### Dead code removed

| File | Reason |
|------|--------|
| `src/dashboard/templates/_panels.py.bak` | Stale backup file |
| `src/llm/db.py` — `persist_call()` function | Unused since OpenObserve migration — `llm_calls` table dropped |
| `src/llm/schema.sql` | References dropped `llm_calls` table; ORM manages schema |
| `src/db/opensearch/` | Wazuh-only per architecture; `sync_audit_log` referenced dropped `audit_logs` table; never imported by live code |
| `src/a2a/checks/` | Exact duplicate of `src/checks/`; only difference was import namespace (`a2a.checks.*` vs `checks.*`) |

`src/manage/_commands.py` import updated: `from a2a.checks.integrity` → `from checks.integrity`

### Architecture flowchart created

- `docs/architecture/flowchart.md` — full Mermaid diagram covering all 19 layers:
  - Layer 0: External clients (browser plugin, Claude Code, TS agent)
  - Layer 1: ASGI entry (proxy/asgi.py :8000)
  - Layer 2: AI proxy (13 strategies, 60 providers, format translation, 5 executors)
  - Layer 3: A2A protocol
  - Layer 4: claude_agent_sdk (external) + 33 agent definitions
  - Layer 5: Agent runner (SSE, session linking, client pool)
  - Layer 6: MCP server (56 cybersec + 5 dystopian crypto tools)
  - Layer 7: Hooks (Python, TypeScript, IPC bridge)
  - Layer 8: Dashboard (REST, SSE, React SPA, Node ts_api)
  - Layer 9: CyberSecSuiteSDK (4-scope context, Jinja2, session I/O)
  - Layer 10: LLM client (Anthropic SDK, pricing, OTEL)
  - Layer 11: Cryptography (RSA-2048, key vault, artifact signing)
  - Layer 12: Memory (Obsidian, Canvas, hot cache)
  - Layer 13: Telemetry (ring buffer, p50/p95/p99, middleware)
  - Layer 14: Database (41 ORM models, intel seeding, OO write path)
  - Layer 15: Accounts
  - Layer 16: Marketplace
  - Layer 17: Startup
  - Layer 18: Infrastructure (PostgreSQL, Redis, OpenObserve, OpenSearch)
  - Layer 19: Scripts & tooling

---

## Files not changed (intentional)

| File | Reason |
|------|--------|
| `src/manage.py` | Documented CLI shim; widely referenced in docs and Makefile |
| `src/db/intel_loader.py` | Backwards-compatibility shim (`from db.intel import ...`) |
| `src/db/models/artifact.py` + `artifacts.py` | Different classes: `Artifact`/`ArtifactSignatureLog` vs `ForensicArtifact` |
| `src/db/models/cve.py` + `cve_entry.py` | Different classes: `CVEIntel` vs `CVEIntelligenceEntry` |
| `src/db/models/ioc.py` + `ioc_entry.py` | Different classes: `IOCEntry` vs `IOCDatabaseEntry` |
