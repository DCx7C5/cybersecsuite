# CyberSecSuite — Master Implementation Plan (v1.6.0 — COMPREHENSIVE REVIEW)

**Date:** 2026-04-26 (Updated with comprehensive analysis)  
**Purpose:** The ONLY plan you will ever need — full context, all tasks, sub-steps, orientation info, and correct Docker names

---

## [NEW 2026-04-26d] Slash & Mention Command Menus (Phase 7C+ Feature)

**Feature Request:** Press `/` or `@` in Send Message prompt to trigger popup menus with contextual actions.

**Use Cases:**
- `/` — Slash commands (quick actions, tools, templates)
  - `/analyze` → Analyze selected IOC
  - `/summarize` → Summarize log/report
  - `/extract` → Extract IOCs from text
  - `/search` → Search forensic data
  - `/create-case` → New investigation case
  - `/open-panel` → Quick panel switcher

- `@` — Mentions (context references)
  - `@case:*` → Link to case
  - `@report:*` → Reference report
  - `@ioc:*` → Reference IOC
  - `@file:*` → Attach file path

**New Todos:** T151–T165 (15 todos, 10–12 hours)

### T151–T155: Core Menu Components (3–4 hours)
- **T151** (1.5h): Create `CommandMenu.tsx` component
  - Triggered by `/` in input
  - Displays searchable command list with icons
  - Keyboard navigation (arrow keys, enter)
  - Escapes on blur or Escape key

- **T152** (1.5h): Create `MentionMenu.tsx` component
  - Triggered by `@` in input
  - Displays available references (cases, reports, IOCs)
  - Async search (query backend for matches)
  - Autocomplete with preview

- **T153** (1h): Create menu position & popup logic
  - Calculate popup position relative to cursor
  - Avoid viewport overflow (reposition if needed)
  - Z-index stacking
  - Animation (fade-in, scale)

- **T154** (1h): Integrate hooks for input tracking
  - Use `useList` hook to manage command history
  - Use `useEventListener` for keyboard events
  - Track cursor position in input
  - Debounce search queries (for `@` mentions)

- **T155** (30m): Create menu schemas & types
  - File: `types/commands.ts`
  - Interfaces: Command, Mention, MenuState
  - Export options for all commands

### T156–T160: Integration with SendMessagePrompt (4–5 hours)
- **T156** (1.5h): Extend SendMessagePrompt.tsx
  - Detect `/` and `@` characters
  - Show/hide menu based on input state
  - Replace menu trigger text with selected command/mention
  - Preserve input before/after replacement

- **T157** (1h): Implement command execution
  - `executeCommand(command: Command, input: string)` function
  - Expand templates (e.g., `/analyze` → "Analyze the following IOC:\n{selected}")
  - Inject context (case ID, IOC type, etc.)
  - Handle special commands (`/open-panel` → Switch tabs)

- **T158** (1h): Implement mention insertion
  - Insert `@case:123` or `@ioc:abc` into input
  - Format as markdown or custom syntax
  - Validate references (ensure they exist)
  - Syntax highlighting for mentions in input

- **T159** (1h): Add keyboard shortcuts
  - Ctrl+K / Cmd+K → Open command menu manually
  - Tab to select highlighted item
  - Shift+Enter → Select & submit
  - Arrow keys → Navigate options

- **T160** (30m): Handle state & cleanup
  - Close menu on selection
  - Preserve cursor position
  - Clear menu state on blur
  - Handle rapid input changes

### T161–T165: Testing, Docs & Polish (3–4 hours)
- **T161** (1.5h): Create Playwright tests for menus
  - Test command menu trigger & search
  - Test mention menu autocomplete
  - Test keyboard navigation
  - Test menu dismissal

- **T162** (1h): Create unit tests for command execution
  - Test template expansion
  - Test context injection
  - Test mention validation
  - Test edge cases (empty input, special chars)

- **T163** (1h): Create user documentation
  - File: `docs/features/slash-commands.md`
  - List all commands with descriptions
  - Examples & screenshots (if possible)
  - Keyboard shortcuts reference

- **T164** (30m): Create developer documentation
  - How to add new commands
  - How to add new mention types
  - Template syntax & variables
  - Extension points

- **T165** (30m): Polish & accessibility
  - Aria labels for screen readers
  - High contrast support for menus
  - Mobile keyboard support
  - Animation performance optimization

### Command & Mention Definitions

**Slash Commands (/)**

```
/analyze              Analyze selected IOC (type auto-detected)
/summarize            Summarize log/report text
/extract              Extract IOCs from input text
/search               Search forensic database
/create-case          Create new investigation case
/open-panel           Quick panel switcher (type panel name)
/tools                Show available analysis tools
/help                 Show command help
/shortcuts            Show keyboard shortcuts
/config               Show user settings/preferences
/template             Browse saved prompt templates
```

**Mentions (@)**

```
@case:{id}            Link to investigation case (e.g., @case:INC-2024-001)
@report:{id}          Reference report (e.g., @report:threat-assessment)
@ioc:{value}          Reference IOC (e.g., @ioc:192.168.1.1)
@file:{path}          Attach file path (e.g., @file:/logs/event.log)
@workspace:{name}     Switch workspace (e.g., @workspace:incident-response)
@user:{id}            Tag colleague/team member
```

### Architecture Diagram

```
SendMessagePrompt.tsx
  ├─ Input element
  │   ├─ On every keystroke → Check for `/` or `@`
  │   └─ If found → Calculate cursor position
  │
  ├─ CommandMenu.tsx (if `/` detected)
  │   ├─ Filter commands by input
  │   ├─ Show popup near cursor
  │   └─ On select → executeCommand()
  │
  ├─ MentionMenu.tsx (if `@` detected)
  │   ├─ Search backend for matches
  │   ├─ Show popup with results
  │   └─ On select → insertMention()
  │
  └─ Hidden state management
      ├─ menuOpen: boolean
      ├─ menuType: 'command' | 'mention'
      ├─ cursorPos: number
      └─ searchQuery: string
```

### File Structure

```
src/frontend/src/
├─ components/
│  ├─ ui/
│  │  ├─ CommandMenu.tsx (NEW)
│  │  ├─ MentionMenu.tsx (NEW)
│  │  └─ MenuPopup.tsx (NEW)
│  └─ layout/
│     └─ SendMessagePrompt.tsx (MODIFIED)
├─ types/
│  └─ commands.ts (NEW)
├─ hooks/
│  └─ useCommandMenu.ts (NEW — custom hook for menu logic)
├─ utils/
│  └─ commandExecutor.ts (NEW — execute commands)
└─ tests/
   └─ e2e/
      └─ slash-mentions.spec.ts (NEW)
```

### Integration with Existing Features

- **Sidebar** (Phase 7C): `/open-panel` command can switch panels like sidebar clicking
- **React Router** (Phase 7D): `/open-panel:chat` sets URL param
- **Zustand Store**: Persist command history in localStorage
- **Hooks**: Use `useList` for command suggestions, `useEventListener` for keyboard

### Performance Considerations

- **Debounce mention searches:** 300ms (avoid too many API calls)
- **Command list filtering:** Client-side only (fast)
- **Menu rendering:** Only show if `/` or `@` in input (avoid unnecessary renders)
- **Keyboard navigation:** Use `onKeyDown` not `onChange` (avoid re-renders on every key)

### Accessibility

- ✅ Keyboard-first navigation (all features accessible via keyboard)
- ✅ Aria labels on menu items
- ✅ Focus management (trap focus in menu while open)
- ✅ Screen reader support (announce filtered results)
- ✅ High contrast (visible in light/dark mode)

### Phase 7C+ Priority

**Integration Point:** Can add to SendMessagePrompt after T070 (core component created)

**Blocking:** None (independent feature, doesn't block sidebar)

**Recommended:** After T073 (CollapsibleSection + state persistence proven), before T076 (advanced features)

**Effort in 7C context:** 10–12 hours total, can be split:
- 3–4h: Components + core logic (parallel with T073–T075)
- 3–4h: Integration + state management (parallel with T076–T080)
- 3–4h: Testing + polish (part of T081–T090 verification)

**Alternative:** Defer to Phase 7D (after React Router, could leverage URL params for commands)

---

## [UPDATE 2026-04-26c] AHS Admin Panel Frontend Reuse (NEW PHASE 7C+ ENHANCEMENTS)

**Analysis:** Reviewed 62 source files from AHS admin panel frontend. Identified 8 high-value components/hooks for reuse.

**New Todos:** T111–T118 (8 todos, 12–16 hours)

### Tier 1 Additions (Phase 7C Integration — 5 hours)
- **T111:** Copy encoding utilities (ab2hex, base64Encode, base64Decode) → `utils/encoding.ts`
- **T112:** Implement useHideElement hook → `hooks/useHideElement.ts` (for Send Message toggle, dropdowns)
- **T113:** Create Breadcrumb component → `components/ui/Breadcrumb.tsx` (for T079 workspace context)
- **T114:** Integrate DataProvider context pattern (OPTIONAL, if useful for auth state)

### Tier 2 Additions (Phase 7D Integration — 3 hours)
- **T115:** Copy AuthProtectedRoutes component (route guard for React Router, T102)
- **T116:** Evaluate TabNavigation component (decide: replace activeTab locally or keep Zustand?)
- **T117:** Document component patterns from AHS

### Tier 3 (Phase 1 Dependent — 1–2 hours)
- **T118:** Use encoding utilities in QoL injection (BLOCKED on T002 design)

**All 5 hooks already added to hooks/ directory** (useBreakPoint, useEventListener, useLocalStorage, useIntersectionObserver, useList)

---

## [UPDATE 2026-04-26b] React Router & Latest React Requirements

**React Version:** ^19.2.5 (strict, latest)

**New Requirement:** Implement React Router v7 for frontend navigation (currently using activeTab state).

### React Router Migration (NEW PHASE 7D — T101–T110)

**T101** — Install React Router v7 + update package.json  
**T102** — Create router configuration (RootLayout, nested routes)  
**T103** — Convert activeTab state → URL params (?tab=chat)  
**T104** — Update Sidebar navigation to use Link components  
**T105** — Update topbar breadcrumb with useLocation hook  
**T106** — Implement lazy route loading for panels  
**T107** — Add browser back/forward button support  
**T108** — Handle deep linking (preserve state on page reload)  
**T109** — Update E2E tests for router-based navigation  
**T110** — Document React Router setup in frontend.md

**Rationale:**
- URL-driven navigation enables deep linking (share links to specific panel)
- Browser back/forward buttons work intuitively
- SEO-friendly URLs for documentation
- Aligns with React 19 + TanStack best practices
- Reduces Zustand state complexity (router is source of truth)

**Phase 7D Effort:** 4–5 hours (router setup ~1h, migration ~2h, tests ~1h, docs ~30m)

**Strict React 19 Practices:**
- Use `use()` hook for promise unwrapping (React 19)
- Use React Compiler (if enabled) with `'use memo'` granularly
- Avoid deprecated `ReactDOM.render()` (use `createRoot`)
- Use `startTransition` for non-blocking updates
- Leverage React 19 actions for form handling
- Server Components not applicable (SPA only)

---

## [REVIEW] Critical Improvements & Fixes (2026-04-26)

### Phase Accuracy & Completion Status

| Phase                              | Status        | Assessment                                                  | Changes                                                        |
|------------------------------------|---------------|-------------------------------------------------------------|----------------------------------------------------------------|
| **0: Bootstrap**                   | ✅ DONE        | Verified and working                                        | None needed                                                    |
| **1: QoL Core (T002–T015)**        | ⏳ PENDING     | Ready to start, all prerequisites met                       | Recommend: start with T002–T004 in parallel                    |
| **2: Gap Analysis (T016–T022)**    | ⏳ PENDING     | Depends on Phase 1 completion                               | Keep as-is, will unblock after T015                            |
| **3: Browser Plugin (T023–T032)**  | ⏳ PENDING     | Feasible but low priority (requires webllm setup)           | Defer to Phase 5+ or parallel with Phase 4                     |
| **4: Marketplace (T033–T039)**     | ⏳ PENDING     | Clear scope, implementable after Phase 1                    | Recommend: start T033 after T015 done                          |
| **5: DB Optimization (T045–T050)** | ⚠️ CRITICAL   | PostgreSQL schema changes are invasive. Recommend LAST.     | **MOVE to Phase 6+ (after React stable)**                      |
| **6: React Migration**             | ✅ COMPLETE    | SPA stable, 33 panels, 66kB gzip, zero lint violations      | Verified with Playwright (13/13 tests passing)                 |
| **7: Sidebar UX (T070–T100)**      | ⏳ IN PROGRESS | Design complete, tests scaffolded, ready for implementation | **Start NOW with T070–T075 core, then T091–T100 verification** |

### Prioritization Recommendation

### ⏱️ Updated Phase Sequence (With React Router + AHS Reuse)

**Current Recommended Sequence (UPDATED 2026-04-26c):**
1. ✅ Phase 6 (React) — DONE
2. ✅ Phase 7B (State validation) — DONE
3. **→ Phase 7C (Sidebar UX) — IN PROGRESS (T070–T100 + T111–T114, 13–15h total)**
4. **→ Phase 7D (React Router) — NEXT (T101–T110 + T115–T116, 6–7h total)** 
5. **→ Phase 1 (QoL Core) — PARALLEL (T002–T015, 8–10h)**
6. Phase 2 (Gap Analysis) — depends on Phase 1
7. Phase 4 (Marketplace) — standalone, ~4h
8. Phase 3 (Browser Plugin) — optional, lowest priority
9. **Phase 5 (DB Optimization) — DEFER to Phase 9+ (LAST, high risk)**

**Rationale for AHS Reuse Integration:**
- Sidebar UX components (T070–T075) ready for useHideElement, Breadcrumb adoption
- React Router phase (T101–T110) can use AuthProtectedRoutes pattern
- Encoding utilities useful for token budget optimization (T118, Phase 1)
- All 5 hooks already copied + verified (useBreakPoint, useEventListener, useLocalStorage, useIntersectionObserver, useList)

---

## Test Coverage Requirements (ADDED)

**ALL Phase 7C features MUST be verified with Playwright before marking DONE.**

**New Test Todos Added (T091–T100):**
- T091: Send Message prompt routing
- T092: Collapsible section toggle/persist
- T093: 33 items accessible via hierarchy
- T094: Dropdown independence
- T095: Message → Chat routing
- T096: Lucide icons render correctly
- T097: Responsive sidebar (mobile/desktop)
- T098: ⌘K search functionality
- T099: Live SSE badge counts
- T100: Favorites/pinning system

**Enforcement:** No TODO can be marked DONE without corresponding Playwright test passing.

---

## Phase 1 (QoL Core) Clarifications

### Dependency Review
- T002–T004 can start immediately (no dependencies)
- T005 depends on T004 (manager.py injection)
- T006–T007 depend on T003–T004 (prompts + manager)
- T008–T009 depend on T006–T007 (tools + MCP tools)
- T010–T015 can be parallelized after T004

**Recommendation:** Start T002, T003, T004 in parallel day 1.

### Token Budget Clarification
- Current: 78 tokens (with all toggles enabled)
- Target: ≤55 tokens
- **Action:** Add automated token counting to T014 (benchmark)
- **Warning:** If any toggle exceeds 5 tokens overhead, optimize or remove

---

## Phase 5 (DB Optimization) — RISKS FLAGGED

**⚠️ HIGH RISK:** Schema changes to PostgreSQL are invasive. Current recommendation:

1. **Do NOT run during active backend operations**
2. **Requires:**
   - Full database backup before T045
   - Dev/staging test run first (T045 on dev DB)
   - Zero-downtime migration strategy (if going to production)
3. **Blocker resolution:** If T046 asks "which Sessions table", decision matrix needed:
   - Option A: Keep `sessions` (current), delete `user_sessions`
   - Option B: Keep `user_sessions`, delete `sessions`
   - Recommendation: **DELETE `sessions`, KEEP `user_sessions` (more recent)**

**Moved Status:** Defer Phase 5 until Phase 7C + Phase 1 proven stable (estimate: 2026-04-29+)

---

## Scope Model Clarification (Section 1)

Current statement is correct but could be clearer:
- **Global (~/.claude/):** IDE/Agent definitions only. Unchanged.
- **App (~/.cybersecsuite/):** Vault (Obsidian), memory cache, QoL state.
- **Project (.css/):** Overrides for specific project (created at install time).
- **Runtime (.css/<id>/):** Container isolation (for multi-pod deployments).
- **Session (.css/<id>/worktree-<SID>/):** Ephemeral per-session state.

**Action:** Add diagram showing scope inheritance hierarchy.

---

## Section 4 (Shared Context) — Additions

Add to "Shared Context for ALL Agents":
- **Test requirement:** All Phase 7+ tasks require Playwright verification
- **Docker health check:** Run `docker compose ps` before starting work to verify all services healthy
- **Browser cache:** Clear between test runs: `rm -rf src/frontend/test-results/ .playwright/`
- **Lock file:** Use `uv.lock` exclusively; never `pip install` or `npm install`

---

## Decisions & Trade-offs

### Decision Review

| Decision                      | Status        | Risk   | Action                 |
|-------------------------------|---------------|--------|------------------------|
| Master switch client + server | ✅ LOCKED      | Low    | Keep; proven safe      |
| Token target ≤60 tokens       | ⚠️ TIGHT      | Medium | Add monitoring in T014 |
| Defer Phase 5 to Phase 8+     | ✅ RECOMMENDED | Medium | Lock as new guideline  |
| Phase 7C → highest priority   | ✅ NEW         | Low    | Lock as next milestone |
| Marketplace before Plugin     | ✅ RECOMMENDED | Low    | Phase 4 before Phase 3 |

---



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

### Phase 6: React Migration Hardening (T051–T065) — COMPLETE ✅

**STATUS:** React SPA migration 100% complete (2026-04-26). ESLint 0 violations, Playwright scaffolded, bundle verified, legacy Jinja deleted.

---

### Phase 7: React Sidebar UX Restructure (T070–T075) — DESIGN COMPLETE

**STATUS:** 3-level sidebar hierarchy designed. Ready for implementation and state validation.

---

### Phase 7B: State Validation & E2E Testing (T081–T090) — COMPLETE ✅

**STATUS:** All 13 Playwright state validation tests passing (10.4s total).

**Tests Passing:**
- localStorage persists after first action (initialize on interaction) ✓
- activeTab persists: default is chat (after first interaction) ✓
- clicking nav items updates activeTab ✓
- activeTab persists across page reload ✓
- sidebar toggle updates sidebarCollapsed ✓
- sidebarCollapsed persists across reload ✓
- theme switching updates state ✓
- theme persists across reload ✓
- rapid tab switches don't corrupt state ✓
- sidebar collapse + tab switch maintains state ✓
- settings dropdown toggle doesn't affect main state ✓
- all 33 nav items are clickable ✓
- complex workflow: collapse → theme → tab → reload ✓

**Key Findings:**
- Zustand `persist` middleware working correctly with `partialize` option
- localStorage key: `cybersecsuite-ui`
- Store hydrates on first interaction (not on page load — expected behavior)
- State shape: `{ state: { activeTab, sidebarCollapsed, theme }, version: N }`
- No race conditions detected in rapid state mutations
- CSS theme tokens applying correctly

---

### Phase 7C: Sidebar UX Restructure - Implementation Ready (T070–T075, T076–T080)

**REQUIREMENT: All features MUST be verified with Playwright tests before marking done.**

**Core Features (T070–T075):**
- T070: Send Message prompt component (top, non-dropdown)
- T071: CyberSecSuite App dropdown (collapsed by default)
- T072: Backend & Infrastructure dropdown (collapsed by default)
- T073: CollapsibleSection component with state persistence
- T074: Update nav.ts with 3-level hierarchy + lucide icons
- T075: Full sidebar UX test suite (message routing, collapse/expand, all 33 items)

**Advanced Features (T076–T080) — After core:**
- T076: Favorites/pinning system
- T077: Live badge counts (SSE-fed from /sse/tasks, /sse/cases)
- T078: ⌘K search for sidebar items
- T079: Investigation context breadcrumb
- T080: A2A task status indicator

**Playwright Test Coverage (T081–T090):**
- Message prompt routing to Chat panel ✓
- Collapsible section toggle state persistence ✓
- Send Message input submits correctly ✓
- All dropdowns collapse/expand independently ✓
- All 33 items accessible via new hierarchy ✓
- Breadcrumb context switching (if implemented) ✓
- Live badge updates on SSE events (if implemented) ✓
- Search ⌘K functionality (if implemented) ✓
- Responsive collapse on mobile (if implemented) ✓
- State survives page reload ✓

**Phase 7C Effort:** ~6–8 hours (components ~2h, tests ~2h, advanced features ~2–3h, debug/refinement ~1h).

**T081** — Write Playwright tests for activeTab state persistence  
**T082** — Test sidebarCollapsed state across page reload  
**T083** — Verify theme state (light/dark) persists in localStorage  
**T084** — Test all 33 nav items are accessible and clickable  
**T085** — Verify uiStore state mutations don't cause race conditions  
**T086** — Test SSE/API data binding (live badges, case counts)  
**T087** — Debug and fix any state synchronization issues  
**T088** — Test responsive sidebar (mobile collapse behavior)  
**T089** — Verify settings dropdown state isolation  
**T090** — Final E2E coverage report + state machine documentation

**State Coverage Checklist:**
```
✓ uiStore (Zustand)
  - activeTab (nav selection)
  - sidebarCollapsed (toggle state)
  - theme (light/dark)
  - localStorage persistence
  
✓ localStorage durability
  - State survives F5 reload
  - Cross-tab sync (optional)
  
✓ API/SSE state binding
  - Task counts update on /sse/tasks
  - Case counts update on /sse/cases
  - Health status updates on /sse/health
  
✓ Navigation state
  - Active tab highlights correctly
  - Panel switching doesn't lose state
  - Back button behavior
  
✓ Race conditions
  - Rapid tab switches
  - Sidebar collapse + panel navigation
  - Theme toggle + sidebar toggle
```

**T070** — Create Send Message prompt component (top of sidebar, non-dropdown)  
**T071** — Create CyberSecSuite App Specific dropdown (collapsed by default)  
**T072** — Create Backend & Infrastructure dropdown (collapsed by default)  
**T073** — Implement CollapsibleSection component with state persistence  
**T074** — Update nav.ts with 3-level hierarchy + lucide icons  
**T075** — Test sidebar UX: message routing, collapse/expand, state persistence

**New Sidebar Hierarchy:**
```
┌──────────────────────────────────────┐
│  💬 Send Message                     │  ← Always visible
│     [Text input + Send button]       │
├──────────────────────────────────────┤
│                                      │
│  🔍 CYBERSEC APP FUNCTIONS  ▼        │  ← Dropdown (collapsed)
│                                      │
│  ├ 🔎 Investigations (sub-collapse)  │
│  │  ├ Cases / Tasks / Findings       │
│  │  ├ IOCs / YARA / Intel Feed       │
│  │  ├ Audit Log / Compliance         │
│  │                                   │
│  ├ 🤖 Agents & Orchestration         │
│  │  ├ Chat (⭐ FAVORITE)             │
│  │  ├ Agent Factory / Crafter        │
│  │  ├ Team Builder / Workflows       │
│  │  ├ Flowgraph / Prompts            │
│  │  ├ SDK Lab / Marketplace          │
│  │                                   │
│  ├ ⚙️ AI Proxy                       │
│  │  ├ Routing / QoL Controls         │
│  │                                   │
│  ├ ⚡ Operations                     │
│     ├ PoCs / A2A Proto / Tasks       │
│                                      │
├──────────────────────────────────────┤
│                                      │
│  ⚙️ BACKEND & INFRASTRUCTURE  ▼      │  ← Dropdown (collapsed)
│                                      │
│  ├ 📊 Platform Health                │
│  │  ├ Health Dashboard               │
│  │  ├ Usage & Cost                   │
│  │  ├ Telemetry                      │
│  │  ├ Provider Hub                   │
│  │                                   │
│  ├ 📈 Data & Storage                 │
│     ├ OpenObserve / Explorer         │
│     ├ Templates                      │
│                                      │
├──────────────────────────────────────┤
│  ⚙️ SETTINGS                         │  ← Always visible
│     ├ Claude SDK                     │
│     └ CyberSecSuite                  │
└──────────────────────────────────────┘
```

**CONSTRUCTIVE ADDITIONS (from docs):**

1. **Favorites/Pinning** — Mark frequently-used items (e.g., Chat, Cases). Appear at top of CyberSecSuite section. Configurable in Settings.

2. **Sub-collapsibles** — Investigations sub-section collapses independently. Allows deep nesting without overwhelming users (7-item Investigations group becomes compact).

3. **Search Bar** — Optional: Quick-search sidebar items (⌘K shortcut). Reduces scrolling for power users across 33 items.

4. **Badge Counts** — Show live counts (e.g., "Cases (5 active)", "Tasks (2 running)"). SSE-fed from `/sse/tasks` and `/sse/cases` endpoints already in backend.

5. **Icon Migration** — Replace Unicode with lucide-react (Heart, Activity, Zap, Database, Code, Shield, etc.). Better visual consistency + accessibility.

6. **Workspace Context** — Add breadcrumb at top showing current investigation/case (e.g., "Case #42: APT-28"). Bound to activeCase state (adds context switching).

7. **A2A Task Status Bubble** — Small dot on Operations > A2A Proto: green (idle) / yellow (running) / red (error). Real-time from A2A socket.

8. **Rationale from arch docs:**
   - **7-layer architecture** → sidebar mirrors: frontend (Send Message) → app logic (CyberSecSuite) → backend (Infrastructure)
   - **33 agents + 18 active agents** → needs tight organization; sub-collapsibles prevent bloat
   - **SSE endpoints** → dashboard already streams cases/tasks/health → integrate live badges
   - **Multi-team support** (blue/red/purple) → context switcher in settings dropdown

**Phase 7 Effort:** 2–3 hours (CollapsibleSection component ~30 min, nav migration ~20 min, favorites/badges ~45 min, search ~45 min, icons ~30 min, testing ~30 min).


---

**T051** — Install ESLint + React plugins in `src/frontend/`  
**T052** — Fix all ESLint violations (target: 0 violations across 56 files)  
**T053** — Add pre-commit hooks for lint checks  
**T054** — Set up Playwright E2E test framework  
**T055** — Write E2E tests: app bootstrap, lazy panel loading  
**T056** — Write E2E tests: Chat panel SSE streaming, token parsing  
**T057** — Write E2E tests: data tables (sort, filter, pagination)  
**T058** — Write E2E tests: theme switching (3 modes, localStorage persistence)  
**T059** — Write E2E tests: error boundaries, malformed API responses  
**T060** — Verify bundle size (gzip < 100 kB; monitor with `vite-bundle-visualizer`)  
**T061** — Profile performance (CLS, LCP, FID with Chrome DevTools)  
**T062** — Document testing strategy in `docs/development/testing.md`  
**T063** — Integrate tests into CI (`github/workflows/`)  
**T064** — Create deprecation notice for legacy Jinja templates (`src/dashboard/templates/README.md`)  
**T065** — Write completion changelog: `docs/changelog/react-migration-complete.md`

**Key artifacts:**
- Frontend source: `src/frontend/` (33 panels, 13 UI components, 56 files)
- Build output: `src/dashboard/static/react/` (vite build, ~66 kB gzip main)
- Fallback: `src/dashboard/api/page.py` checks for React build; serves legacy Jinja if absent
- Docs: `docs/development/frontend.md` (already complete)
- Changelog: `docs/changelog/react-migration-2026-04-22.md` (existing)

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

---

## 8. Implementation Roadmap (Updated 2026-04-26b)

### ✅ Completed Milestones

| Milestone                    | Date       | Status                                              |
|------------------------------|------------|-----------------------------------------------------|
| Phase 0: Bootstrap           | ✅          | Verified working                                    |
| Phase 6: React SPA Migration | 2026-04-26 | ✅ COMPLETE (56 files, 33 panels, 0 lint violations) |
| Phase 7B: State Validation   | 2026-04-26 | ✅ COMPLETE (13/13 Playwright tests passing)         |

### 📋 Current Priorities (Next 72 hours)

**NOW → Phase 7C (Sidebar UX):** T070–T100  
- Core components: T070–T075 (6–8 hours)
- Playwright verification: T091–T100 (2–3 hours)
- **Start immediately**

**NEXT → Phase 7D (React Router):** T101–T110  
- Router integration: T101–T108 (3–4 hours)
- E2E tests: T109 (1 hour)
- Docs: T110 (30 min)
- **Prerequisite for deep linking + browser buttons**

**PARALLEL → Phase 1 (QoL Core):** T002–T015  
- Can start as soon as T070 scaffolding begins
- Estimated: 8–10 hours
- **No blocking dependencies**

### 🚀 Medium-term (1 week)

| Phase                    | Tasks     | Effort  | Status              | Notes               |
|--------------------------|-----------|---------|---------------------|---------------------|
| Phase 2: Gap Analysis    | T016–T022 | 4 hours | Blocked on Phase 1  | Unblocks after T015 |
| Phase 4: Marketplace     | T033–T039 | 4 hours | Ready after Phase 1 | Independent module  |
| Phase 3: Browser Plugin  | T023–T032 | 6 hours | Optional            | Defer to Phase 5+   |
| Phase 5: DB Optimization | T045–T050 | 6 hours | **DEFER**           | Run LAST, high risk |

### ⚠️ Critical Path (UPDATED)

```
Phase 0 (Done)
    ↓
Phase 6 (Done)
    ↓
Phase 7B (Done)
    ↓
Phase 7C (Sidebar) ← NOW (8–10 hours)
    ↓
Phase 7D (Router) ← NEXT (4–5 hours) [NEW]
    ↓
Phase 1 (QoL) ← PARALLEL or NEXT (8–10 hours)
    ↓
Phase 2 (Gap) ← Depends on Phase 1
    ↓
Phase 4 (Marketplace) ← Independent
    ↓
Phase 3 (Plugin) ← Optional
    ↓
Phase 5 (DB) ← LAST, HIGH RISK
```

**Total Estimated Time:**
- Phase 7C: 8–10 hours
- Phase 7D: 4–5 hours (NEW)
- Phase 1: 8–10 hours
- **Combined: 20–25 hours for all critical path items**

---

## Phase 8: Ollama Model Auto-Setup (T122–T126) — NEW

**Objective:** Automated CyberSecSuite model setup during `docker compose up` (development only).

**Status:** Planning → Implementation Phase 1-2 Complete

**Todos:**
- **T122** ✅ DONE: Create entrypoint script (`.docker/ollama/entrypoint.sh`)
- **T123** ✅ DONE: Update docker-compose.yml with entrypoint + volumes
- **T124** ⏳ PENDING: Create documentation (`docs/getting-started/ollama-setup.md`)
- **T125** ⏳ PENDING: Test manual verification + model creation
- **T126** ⏳ PENDING: Update deployment guide (`docs/deployment/production.md`)

**Effort:** 2–3 hours total (1.5h docs/testing, 0.5h verification, 1h deployment notes)

**Current State:**
- Modelfile: `.docker/ollama/Modelfile` (Qwen 3.5 0.8B, existing)
- Docker Compose: Updated with entrypoint + volume mounts
- Entrypoint Script: Created & executable (1.9 KB)
- Auto-setup: Enabled on first `docker compose up` (25s overhead, cached on restart)

**Behavior:**
```
T+0s    Container starts
T+5s    Ollama daemon healthy
T+7s    Model check
→ First run: Create from Modelfile (20s)
→ Subsequent: Skip creation (1s)
T+30s   Ready
```

**Integration:**
- AI Proxy routes to `cybersec-suite` model
- Endpoint: `http://localhost:11434` (local) / `http://cybersec-ollama:11434` (container)
- API: OpenAI-compatible + native Ollama API

**Performance:**
- Disk: +700 MB (model + Ollama)
- Memory: +50 MB daemon + 800 MB model (with GPU)
- First startup: +25s; subsequent: +5s
- Bundle added: 2 KB (negligible)

**Next Steps:**
1. T124: Write setup documentation
2. T125: Manual testing (docker compose down/up cycle)
3. T126: Deployment guide updates
4. Future: Model switching via env var, auto-pull base model

---

## Phase 9: AI Model Tiering & Qwen3.5 Integration (T127–T150) — NEW

**Objective:** Implement production-grade tiered routing architecture with Qwen3.5 models for classification, local inference, and API escalation. Optimize for GTX 1050 Ti (4GB VRAM, 16GB RAM).

**Status:** Planning (phased rollout)

### Architecture Overview

**Tier 0 – Triage Router** (Qwen3.5-0.8B, local via Ollama)
- Purpose: Fast classification, routing decision, pre-processing
- Latency: <500ms
- VRAM: ~800 MB (quantized)
- Decision output: JSON (`{"route":"chat|forensics|ioc|escalate","confidence":0.95}`)
- Use cases: Intent classification, IOC extraction, request validation

**Tier 1 – Local Execution** (Qwen3.5-1.5B, local via Ollama)
- Purpose: Mid-tier reasoning, structured analysis, token-efficient tasks
- Latency: 1-3s
- VRAM: ~1.2 GB (quantized)
- Use cases: Summary generation, forensic pattern matching, JSON extraction
- Escalate if: Confidence <0.7, reasoning complexity high, fallback on timeout

**Tier 2 – High Quality** (Claude Haiku/Sonnet, API)
- Purpose: Complex reasoning, security analysis, edge cases
- Latency: 2-5s (API)
- Cost: $0.80/$3.00 per 1M input tokens (Haiku/Sonnet)
- Use cases: Threat assessment, multi-step analysis, final decisions
- Trigger: Tier 1 escalation, user-requested, complexity threshold exceeded

### Phase 9 Todos (20–25 hours, multi-part rollout)

#### Part A: Model Setup & Optimization (T127–T132, 6–8 hours)
- **T127** (4h): Add Qwen3.5-1.5B to Ollama
  - Create Modelfile with optimal quantization (Q4_K_M)
  - Benchmark on GTX 1050 Ti (latency, VRAM, tokens/sec)
  - Update docker-compose.yml with second model service
  - Health checks for both 0.8B and 1.5B

- **T128** (1h): Optimize Ollama parameters for 1050 Ti
  - GPU offloading strategy (both models can't be in VRAM simultaneously)
  - Context window tuning per model (8192 vs 4096)
  - Batch size optimization
  - Document OLLAMA_NUM_GPU environment variable usage

- **T129** (1h): Create system prompts for Tier 0 & 1
  - Tier 0 (0.8B router): 150-200 tokens, classification focus
  - Tier 1 (1.5B executor): 200-300 tokens, task-specific patterns
  - Prompt templates for forensics, IOC extraction, intent classification
  - Include examples of JSON output expectations

- **T130** (1h): Implement Modelfiles for both Qwen models
  - Create .docker/ollama/Modelfile-qwen-0.8b (existing, update if needed)
  - Create .docker/ollama/Modelfile-qwen-1.5b (new)
  - Document model parameters, context lengths, GPU layers

- **T131** (30m): Add model metadata & capability matrix
  - File: `docs/architecture/model-capabilities.md`
  - Matrix: Model × Use Case × Latency/Cost/Accuracy
  - Decide when to escalate (confidence threshold, complexity score)

- **T132** (30m): Verify GPU memory management
  - Test loading both models simultaneously
  - Verify eviction strategy (Ollama will swap to CPU if needed)
  - Document worst-case memory usage and fallback plan

#### Part B: AI Proxy Integration (T133–T140, 8–10 hours)
- **T133** (2h): Extend `src/ai_proxy/routing/combo.py` for tiered dispatch
  - Add tier selection logic based on request metadata
  - Route function: `route_with_tiers(request, user_preference="auto")`
  - Confidence thresholds for escalation
  - Logging of routing decisions (tier, model, reason)

- **T134** (2h): Implement Tier 0 router class
  - `QwenTriageRouter` in `src/ai_proxy/models/qwen_routers.py` (new file)
  - Classify request: Extract intent, IOC types, complexity score
  - Output: JSON with `{"route":"chat|forensics|ioc","confidence":0.85,"tier":1}`
  - Timeout handling: Fallback to Tier 2 if >1s

- **T135** (2h): Implement Tier 1 executor class
  - `QwenExecutor` in `src/ai_proxy/models/qwen_routers.py`
  - Task-specific execution: summarize, extract, analyze
  - Structured output: JSON schema validation
  - Confidence scoring + escalation decision

- **T136** (1h): Update routing decision matrix
  - Add Qwen models to `smart_route()` decision logic
  - Priority matrix: `[user_pref, tier0_confidence, tier1_capable, cost_budget]`
  - Fallback chain: `Tier0 → Tier1 → Tier2 (Haiku) → Tier2 (Sonnet)`

- **T137** (1h): Implement fallback & error handling
  - Tier timeout: 500ms for T0, 3s for T1, 5s for T2
  - Retry logic: Exponential backoff on Ollama timeout
  - Error logging: Track tier failures for analysis
  - Circuit breaker: Disable Tier 0/1 if >5 consecutive failures

- **T138** (30m): Add request/response logging
  - Log routing decision, latency, tokens used, tier selection
  - File: `src/ai_proxy/logging/tier_decisions.py`
  - Format: JSON for analytics (request_id, tier, model, latency_ms, tokens, cost)

- **T139** (1h): Implement cost estimator
  - Estimate tokens before request (based on history)
  - Cost calculation: `tokens × tier_rate` (free for Tier 0/1, $$ for Tier 2)
  - Add cost to response headers: `X-Tier-Cost: $0.02`

- **T140** (30m): Add API endpoint for routing diagnostics
  - `GET /admin/diagnostics/routing` → Show current tier health, latency, model status
  - Useful for debugging tier selection
  - Include: Ollama model list, health checks, memory usage

#### Part C: Prompt Engineering & Token Optimization (T141–T145, 4–5 hours)
- **T141** (1.5h): Create prompt templates library
  - File: `src/ai_proxy/prompts/tier_templates.py`
  - Tier 0: Classification prompts (IOC extraction, intent, complexity)
  - Tier 1: Task-specific prompts (summary, analysis, structured JSON)
  - Tier 2: Complex reasoning prompts (multi-step, edge cases)
  - All prompts < 300 tokens (to stay within model constraints)

- **T142** (1h): Implement JSON schema validation for structured output
  - Use Pydantic for output schema validation
  - File: `src/ai_proxy/schemas/tier_outputs.py`
  - Tier 0 output: `TriageDecision` (route, confidence, complexity_score)
  - Tier 1 output: Task-specific (ForensicAnalysis, IOCExtraction, etc.)
  - Add retry logic if JSON parsing fails

- **T143** (30m): Optimize prompt token count
  - Analyze current prompts with token counter (tiktoken)
  - Target: Tier 0 <150 tokens, Tier 1 <250 tokens, Tier 2 <500 tokens
  - Use compression techniques (abbreviations, examples over explanations)

- **T144** (1h): Create few-shot examples for Tier 0/1
  - Tier 0: 3-5 examples of intent classification, IOC extraction
  - Tier 1: 2-3 examples of forensic analysis, summary generation
  - Store in YAML for easy updates: `docs/architecture/prompt-examples.yaml`

- **T145** (30m): Document prompt engineering best practices
  - File: `docs/development/prompt-engineering.md`
  - Tips for Qwen models: Chain-of-thought, structured output, temperature
  - Comparison to Claude: Qwen is more literal, needs explicit JSON format
  - Testing guidelines: Evaluate consistency, accuracy, speed

#### Part D: Testing & Validation (T146–T150, 4–5 hours)
- **T146** (2h): Create routing decision test suite
  - File: `tests/unit/test_tier_routing.py`
  - Test cases: intent classification, escalation logic, tier selection
  - Mock Tier 0/1 responses, test fallback to Tier 2
  - Verify confidence thresholds trigger escalation correctly

- **T147** (1h): Implement A/B testing framework
  - File: `src/ai_proxy/testing/ab_test.py`
  - Compare: Tier 0 vs Tier 2, Tier 1 vs Tier 2 on accuracy
  - Sample 5-10% of requests for comparison
  - Track: Latency, cost, user satisfaction (if available)

- **T148** (1h): Create E2E Playwright tests for routing
  - Send IOC analysis request → Verify Tier 0 classification → Check Tier 1 execution
  - Test fallback: Simulate Tier 0 timeout → Verify escalation to Tier 2
  - Verify response headers (X-Tier-Cost, X-Tier-Model)
  - Test JSON schema validation of outputs

- **T149** (30m): Create performance benchmark suite
  - File: `scripts/benchmark_tiers.py`
  - Measure: Latency per tier, tokens/sec, memory usage, cost per 100 requests
  - Run on GTX 1050 Ti to get real-world metrics
  - Document baseline (for future optimization)

- **T150** (30m): Document routing metrics & dashboards
  - File: `docs/deployment/routing-monitoring.md`
  - Metrics to track: Tier selection rate, escalation rate, latency percentiles
  - Example dashboard queries (for future OpenObserve integration)
  - Alerting rules: If escalation_rate > 50%, investigate Tier 0/1

### Integration Points

**With existing systems:**
- AI Proxy: `src/ai_proxy/routing/combo.py` (extends smart_route)
- Ollama: Uses existing docker service (adding 1.5B model)
- OpenObserve: Optional logging integration (tier decisions)
- Frontend: Dashboard shows routing stats, tier health

**With planned phases:**
- Phase 1 (QoL): Can use Tier 0 for intent classification in injections
- Phase 4 (Marketplace): Marketplace items can specify preferred tier
- Future: Red team tooling can analyze tier selection accuracy

### Decision Criteria Matrix

| Scenario                | Tier 0 (0.8B) | Tier 1 (1.5B) | Tier 2 (API) |
|-------------------------|---------------|---------------|--------------|
| IOC extraction (simple) | ✅ Primary     | —             | Fallback     |
| Forensic pattern match  | —             | ✅ Primary     | Fallback     |
| Threat assessment       | —             | —             | ✅ Required   |
| User prefers cost       | ✅ 1st choice  | ✅ 2nd         | Fallback     |
| User prefers accuracy   | —             | ✅ 1st choice  | ✅ 2nd        |
| Under time pressure     | ✅ 1st choice  | —             | —            |
| Complex reasoning       | —             | Escalate      | ✅ Required   |
| Confidence < 0.7        | Escalate      | Escalate      | ✅ Required   |

### Strengths of Qwen3.5 (Why These Models?)

**Tier 0 (0.8B) as Triage Router:**
- ✅ **Optimal speed-to-intelligence ratio**: Classification at <500ms on 1050 Ti
- ✅ **Excellent instruction following**: Reliable JSON output, routing decisions
- ✅ **Quantization resilience**: Q4_K_M maintains accuracy better than competitors
- ✅ **Token efficiency**: 8K context ideal for routing metadata
- ✅ **Minimal VRAM**: ~800 MB leaves room for Tier 2 fallback preparation

**Tier 1 (1.5B) as Local Executor:**
- ✅ **Sweet spot for reasoning**: Handles multi-step analysis without API latency
- ✅ **Structured output**: Excels at JSON generation, schema compliance
- ✅ **GPU efficient**: Q4_K_M = 1.2 GB, allows CPU swapping of Tier 0 when needed
- ✅ **Comparable to Phi-4-mini**: Faster inference, better multilingual support
- ✅ **Community support**: Qwen ecosystem is mature, well-documented

**vs Phi-4-mini:**
- Qwen: Faster on small tokens (routing, extraction)
- Phi: Better on longer reasoning (use if Tier 1 needs upgrade)

### Risks & Mitigations

| Risk                           | Mitigation                                                  |
|--------------------------------|-------------------------------------------------------------|
| OOM on 1050 Ti                 | Dynamic model loading, CPU swapping, queue management       |
| Tier 0 misclassifies           | Confidence thresholds, escalate if <0.7, A/B test accuracy  |
| Tier 1 timeout on complex task | Timeout < 3s, escalate to Tier 2 automatically              |
| JSON parsing fails             | Retry with clearer prompt, fallback to string parsing       |
| Cost spike on API usage        | Track cost, alert if >10% of budget, prioritize local tiers |
| Model hallucinations           | Few-shot examples, schema validation, user feedback loop    |

### Performance Targets

| Metric        | Tier 0   | Tier 1  | Tier 2            |
|---------------|----------|---------|-------------------|
| Latency (p50) | <300ms   | <1.5s   | <3s               |
| Latency (p95) | <500ms   | <3s     | <5s               |
| VRAM          | 800 MB   | 1.2 GB  | —                 |
| Cost          | Free     | Free    | ~$0.001–$0.01/req |
| Accuracy      | 85%+     | 90%+    | 95%+              |
| Throughput    | 10 req/s | 2 req/s | Limited by API    |

### Phase 9 Effort Estimate

| Part                             | Hours           | Status    |
|----------------------------------|-----------------|-----------|
| **Part A: Model Setup**          | 6–8             | ⏳ Pending |
| **Part B: AI Proxy Integration** | 8–10            | ⏳ Pending |
| **Part C: Prompt Engineering**   | 4–5             | ⏳ Pending |
| **Part D: Testing & Validation** | 4–5             | ⏳ Pending |
| **Total**                        | **22–28 hours** | ⏳ Pending |

### Critical Path for Phase 9

```
T127 (Model Setup) [4h]
    ↓
T133–T135 (Routing Core) [4h] ← Parallel: T141 (Prompts)
    ↓
T146–T148 (Testing) [4h]
    ↓
T150 (Monitoring) [1h]
```

**Sequential tasks:** T127 → T133 (need model running)  
**Parallel:** T141 (prompts) can start immediately after T129  
**Estimated parallel execution: 12–14 hours wall time**

### Decision: When to Start Phase 9?

**Recommended:** After Phase 7C (Sidebar) + Phase 7D (Router) are stable  
**Rationale:** Need stable frontend before routing changes propagate to API  
**Alternative:** Start T127–T132 (model setup) in parallel with Phase 7D (no frontend impact)

### Future Enhancements (Phase 9+)

- [ ] Dynamic model loading (swap 0.8B/1.5B based on queue)
- [ ] Phi-4-mini as alternative Tier 1 (comparison)
- [ ] Fine-tune Qwen on CyberSecSuite-specific tasks
- [ ] Cost optimization dashboard
- [ ] Multi-tier caching (cache Tier 0 decisions, reuse for similar requests)

---

---

## 9. Known Constraints & Workarounds

### Constraint 1: Zustand Store Hydration
**Issue:** `persist` middleware doesn't hydrate until first interaction  
**Workaround:** Tests must wait for first action before checking localStorage  
**File:** `src/frontend/src/store/uiStore.ts` (use `partialize` for cleaner state shape)

### Constraint 2: Docker Volume Mounts
**Issue:** React build not accessible from dashboard container  
**Workaround:** Add volume mount in docker-compose.yml:
```yaml
volumes:
  - ./src/dashboard/static/react:/app/src/dashboard/static/react:ro
```
**File:** `docker-compose.yml` line ~52 (dashboard service)

### Constraint 3: Token Budget Pressure
**Issue:** Injected QoL fragments add ~78 tokens, target is ≤55  
**Workaround:** Implement token counting in manager.py + cache toggle combinations  
**File:** `src/ai_proxy/qol_controls/manager.py` (T014)

### Constraint 4: Database Schema Risk
**Issue:** Phase 5 (T045–T050) requires schema migration on production DB  
**Workaround:** **DEFER Phase 5 until Phase 7C + Phase 1 stable**, then plan zero-downtime cutover  
**Timeline:** Earliest 2026-04-29 (after 3 days of stability testing)

---

## 10. Verification Checklist (Before Each Deploy)

- [ ] All Playwright tests passing in phase (e.g., T091–T100 for Phase 7C)
- [ ] ESLint score 0 violations (or < 5 with explained suppressions)
- [ ] Bundle size within targets (Frontend: 66 kB gzip main)
- [ ] Docker services healthy: `docker compose ps` (all "Up (healthy)")
- [ ] No new dependencies added (check `uv.lock` unchanged)
- [ ] Changelog entry written: `docs/changelog/TXXXX-*.md`
- [ ] Tests verified against backend: `npm run test:e2e` (or equivalent)

---