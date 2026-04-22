# CyberSecSuite — Master Implementation Plan (v1.5.2 — COMPLETE + LLM-ORIENTED)

**Date:** 2026-04-22  
**Purpose:** The ONLY plan you will ever need — full context, all tasks, sub-steps, orientation info, and correct Docker names

---

## 0. Critical Rules for LLMs (Read First)

**Before ANY task:**
1. Run `ls <exact path> 2>/dev/null || echo "NOT FOUND"`
2. If already exists → mark **[DONE]** immediately
3. Never duplicate work

**Package Manager:** ONLY `uv`

**Docker Restart (CORRECT service names from your docker-compose.yml):**
- `docker compose restart cybersec-dashboard`
- `docker compose restart cybersec-postgres`
- `docker compose restart cybersec-redis`
- `docker compose restart cybersec-opensearch`
- `docker compose restart cybersec-openobserve` (only if using Wazuh profile)

**Done Todos:** Tracked in SQLite by JetBrains LLM plugin

**Real Paths (use exactly):**
- `src/ai_proxy/routing/combo.py`
- `src/csmcp/cybersec/tool_toggles.py`
- `src/dashboard/api/`
- `src/browser-plugin/`
- `src/db/models/`

---

## 1. Scope Model (5 Levels — Must Follow Exactly)

**Important:** 
- Global and App scopes exist after installation.
- **Project, Runtime, and Session scopes only exist after installation** and are always located in the **present working directory** (`.css/` folder in the current project root).

| Scope       | Path                                                         | Purpose                     | Current State |
|-------------|--------------------------------------------------------------|-----------------------------|---------------|
| **Global**  | `~/.claude/`                                                 | IDE config only             | Partial       |
| **App**     | `~/.cybersecsuite/`                                          | Vault + Obsidian memory     | Core done     |
| **Project** | `.css/` (in present working dir after install)               | Project-specific overrides  | Partial in DB |
| **Runtime** | `.css/<runtime-id>/` (in present working dir)                | Container/pod isolation     | Not yet       |
| **Session** | `.css/<runtime-id>/worktree-<SID>/` (in present working dir) | Ephemeral per-session state | Partial in DB |

**Rule:** Add `runtime_id`, `worktree_path`, `scope_level` to every `ScopedEntry` model.

---

## 2. Mission & What This Plan Delivers

This is the **single source of truth** for implementing:
- Backend-managed QoL Output Controls (File-Only, No Thinking, Minimal Mode, etc.)
- 5-level Scope Model with memory/cache
- Database optimization (OpenSearch migration + redundant table cleanup)
- Browser Plugin for controlling web LLMs
- Marketplace + Agent Factory integration

**Success Criteria:**
- All toggles work with < 60 tokens overhead
- 5-level scope enforced everywhere
- High-volume forensic data moved to OpenSearch
- Browser plugin can control Claude.ai, ChatGPT, Grok, etc.
- Marketplace lazy loading works with deterministic frontmatter

---

## 3. ALL TASKS (Complete Merged List with Sub-Steps)

### Phase 0: Bootstrap (T001)

**T001** — Verify current state + create aligned dir tree  
Sub-steps:
1. Run verification grep for existing QoL files
2. Create `src/ai_proxy/qol_controls/` if missing
3. Create `src/csmcp/cybersec/qol_tools.py` if missing
4. Update plan.md status

---

### Phase 1: Python QoL Core (T002–T015)

**T002** — Create models.py (QoLToggle + QoLSettings)  
**T003** — Create prompts.py (8 strong fragments)  
**T004** — Create manager.py (build_injection + inject_into_request)  
**T005** — Add injection hook in `src/ai_proxy/routing/combo.py`  
**T006** — Create 4 MCP tools in `src/csmcp/cybersec/qol_tools.py`  
**T007** — Extend `src/csmcp/cybersec/tool_toggles.py` for QoL scope  
**T008** — Add dashboard endpoints in `src/dashboard/api/qol.py`  
**T009** — Embed QoL panel as dashboard tab  
**T010** — Write pytest (≥10 tests)  
**T011** — Add Referenz blocks to all new files  
**T012** — Update mcp.json + .claude/settings.json  
**T013** — Update existing docs with QoL sections  
**T014** — Performance benchmark  
**T015** — Add observability & metrics

---

### Phase 2: Gap Analysis (T016–T022)

**T016** — Observability & Metrics (emit to OpenObserve)  
**T017** — A2A Propagation of QoL toggles  
**T018** — Per-Agent QoL Presets  
**T019** — Security Hook for dangerous combinations  
**T020** — Graceful Degradation on injection failure  
**T021** — Default Configuration + Env Vars  
**T022** — Update all existing docs with QoL sections

---

### Phase 3: Browser Plugin (T023–T032)

**T023** — Improve form detection (shadow DOM + scoring) in `content.js`  
**T024** — Implement idle detection (keystroke + mouse)  
**T025** — Multi-tab targeting (non-focused tabs)  
**T026** — Add `webllm: true` routing in combo.py  
**T027** — Response relay + QoL filtering pipeline  
**T028** — Dashboard `/api/proxy/memory-chat` endpoint for webllm  
**T029** — Optional Playwright MCP tool  
**T030** — Update docs for browser plugin

---

### Phase 4: Marketplace (T033–T039)

**T033** — Create `src/marketplace/` module  
**T034** — Add Dashboard marketplace browser endpoints  
**T035** — CLI commands (`manage.py marketplace list`, `install`)  
**T036** — Integrate marketplace with agent loader  
**T037** — Update docs + AGENT_FACTORY.md reference  
**T038** — Dashboard Agent Factory UI (umbrella keyword + teams)  
**T039** — Seed marketplace DB table with provider frontmatter standards

---

### LLM Metadata Standards Table (Frontmatter Headers by Provider)

| Provider / Tool                  | File Format                   | Required Fields                    | Common / Extended Fields                                                                                   | Notes                                   |
|----------------------------------|-------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| **Anthropic Claude Code**        | `SKILL.md` (YAML frontmatter) | `name`, `description`              | `model`, `tools[]`, `maxTurns`, `domain`, `subdomain`, `tags[]`, `mitre_attack[]`, `capec[]`, `nist_csf[]` | Progressive loading. Open standard.     |
| **GitHub Copilot**               | `.agent.md` or `.md`          | `name`, `description`              | `tools[]`, `handoffs[]`, `model`, `metadata{}`, `MCP servers`                                              | Supports agent chaining.                |
| **Cursor**                       | `.mdc` + `.cursorrules`       | `description`, `globs[]`           | `alwaysApply`, `name`                                                                                      | Rules triggered by globs.               |
| **OpenAI Codex / GPTs**          | `AGENTS.md`                   | `name`, `description`              | `instructions`, `tools[]`, `knowledge`                                                                     | Emerging cross-tool standard.           |
| **Google Gemini CLI**            | `AGENTS.md`                   | `name`, `description`              | `system_instruction`, `tools[]`                                                                            | Prefers `AGENTS.md`.                    |
| **xAI Grok**                     | Plain system prompt           | `name`, `description`              | (none standardized)                                                                                        | Best with clean `name` + `description`. |
| **Emerging Cross-Tool Standard** | `AGENTS.md` + `SKILL.md`      | `name`, `description` + extensible | (tool-specific extensions via AGENT_FACTORY)                                                               | Many tools converging on this format.   |

**Important:** Base files after stripping must contain **only** `name` + `description`. Provider-specific headers are generated on-demand during install.

---

### Phase 5: Database Optimization (T045–T050)

**T045** — Create `src/db/migration/scope_v2.py` (add scope columns)  
**T046** — Decide which Sessions table to keep + delete the other  
**T047** — Create OpenSearch index mappings + delete old Postgres tables  
**T048** — Remove duplicate enums + standardize soft-delete  
**T049** — Update `docs/database.md` with new schema  
**T050** — Verify everything works in Docker after changes

---

## 4. Shared Context for ALL Agents (Read Once)

- Storage must reuse `helpers.py` functions: `_get_current_scope()`, `get_project_dir()`, `get_session_dir()`, `SCOPE_LEVELS`.
- Injection hook lives in `src/ai_proxy/qol_controls/injection.py` and is called from `combo.py` right after `ResolvedTarget` is chosen.
- All new code must follow existing style: `from __future__ import annotations`, Pydantic v2, no new deps.
- QoL state lives in `~/.cybersecsuite/data/qol.json`.
- MCP tools use `@tool` from `csmcp._sdk_compat` + `sdk_result()` / `sdk_error()`.
- Dashboard tab reuses existing Jinja2 templates and Starlette routes.

**Parallelization note:** T002, T003, T005, T006, T011 can start immediately in parallel.

---

## 5. Key Decisions (Locked)

| Decision        | Choice                         | Rationale                    |
|-----------------|--------------------------------|------------------------------|
| Package Manager | `uv` only                      | User requirement             |
| Frontend        | Vanilla HTML + TS              | Zero build step              |
| Master switch   | Client UX + server re-validate | Instant feedback + security  |
| Token target    | < 60 tokens                    | Achievable with caching      |
| Docker services | cybersec-* names               | From your docker-compose.yml |

---

## 6. Token Optimization & Warnings

**Current measured:** ~78 tokens for all toggles enabled  
**Target:** ≤ 55 tokens

**Techniques:**
- Cache `build_injection` result keyed by frozenset of active toggles
- Shorten non-critical fragments after compliance testing
- Add `manager.estimate_tokens(injected)` and log warning if > 100 total prompt tokens

**Warning 1:** Never expose toggle state to user prompt. Always server-side only.  
**Warning 2:** For chat apps with 50+ turns, cache per-conversation QoLSettings hash.  
**Warning 3:** "no_output_except_file" fragment must contain the phrase "NOTHING ELSE MAY APPEAR".

---

## 7. How to Use This Plan (LLM Workflow)

1. Read this file at the start of every session.
2. Pick the next **undone** task with the lowest ID.
3. Follow the sub-steps exactly.
4. After finishing a task:
   - Mark it **[DONE]**
   - Write one line to `docs/changelog/T0XX-*.md`
   - Restart the affected Docker service using the **correct names above**
5. Move to the next task.

**This is the complete, rich, LLM-oriented plan with all orientation information.**