# Agent Delegation Strategy — CyberSecSuite Phase 1

**Last Updated:** 2026-04-26  
**Status:** Phase 1 Documentation  
**Responsibility:** Team Orchestrator + Sub-Agents

---

## Overview

CyberSecSuite maintains a **multi-agent orchestration system** where specialized agents handle distinct functional domains. This document defines:

1. **Which agent handles which todos**
2. **Communication protocol** (how agents coordinate)
3. **Result validation** (how to verify deliverables)
4. **Merge strategy** (how to consolidate outputs)

---

## Agent Roster

### Primary Orchestrator

| Agent | Role | Model | Max Turns | Primary Tools |
|-------|------|-------|-----------|---------------|
| **cybersec-agent** | Central orchestrator for APT/rootkit investigations, threat hunts, IOC analysis, artifact signing | Claude Sonnet 4.6 | 60 | All (Orchestrator mode) |

### Specialist Sub-Agents

| Agent | Role | Model | Max Turns | Primary Tools | Specialization |
|-------|------|-------|-----------|---------------|-----------------|
| **python-developer** | Python code implementation, API endpoints, ORM models, crypto operations, test suites | Claude Sonnet 4.5 | 40 | Read, Write, Edit, Bash, Glob, Grep | Backend dev |
| **python-code-reviewer** | Python PR review, security/correctness audits, standards enforcement | Claude Sonnet 4.5 | 30 | Read, Bash, Glob, Grep, LS, TodoRead, TodoWrite | Quality gate |
| **frontend-design** | React components, UI/UX design, styling, web application layouts | Claude Sonnet 4.6 | 40 | Web tools, design tools | Frontend dev |
| **token-optimizer** | Context window management, prompt caching, compression strategies | Claude Sonnet 4.5 | 25 | Analysis tools | Performance |
| **watchdog** | Continuous monitoring, background checks, anomaly detection | Claude Sonnet 4.5 | 30 | Monitoring tools | Automation |
| **encoding-specialist** | Base64/hex/URL/Unicode analysis, obfuscation detection, polyglot payloads | Claude Haiku 4.5 | 20 | Grep, view, bash | Forensics |

### Supported Custom Agents (Project-Specific)

| Agent | Role | Model | Location |
|-------|------|-------|----------|
| **agent-factory** | Create perfect agents from blueprints, preserves rules/tools | Claude Sonnet 4.6 | `.claude/agents/` |

---

## Delegation Matrix

### Phase 1 — Documentation & Planning Todos

| Todo ID | Title | Primary Agent | Secondary | Reason |
|---------|-------|---------------|-----------|--------|
| **T369** | Agent Delegation Strategy Document | **Current (You)** | — | Orchestration doc; defines system |
| **T357** | DEPENDENCIES.md (if not covered) | **Current (You)** | python-developer | Existing doc; verify completeness |
| **T374** | Parallel Track 1 - Scope Foundation | **Current (You)** | — | Status marking; blocks parallel work |
| **plan-mode-prompt** | LLM Plan Mode System Prompt | **Current (You)** | token-optimizer | Prompt engineering + optimization |
| **sidebar-map-panels** | Sidebar ↔ Panel Inventory Map | **Current (You)** | frontend-design | Frontend knowledge required |

### Phase 2–9 — Implementation Todos (Future Assignment)

| Track | Todos | Primary Agent | Secondary | Rationale |
|-------|-------|---------------|-----------|-----------|
| **Backend Infrastructure** | T361–T368 (8 todos) | **python-developer** | python-code-reviewer | Async DB setup, ORM models, fixtures |
| **Frontend Migration** | React Redux→Context | **frontend-design** | python-developer (API) | UI state management refactor |
| **Security Hardening** | Crypto, signing, MCP | **python-developer** | cybersec-agent | Crypto implementation + audit |
| **Testing Suite** | Unit, integration, E2E | **python-developer** | — | pytest, Playwright frameworks |
| **Performance Tuning** | Context caching, optimization | **token-optimizer** | python-code-reviewer | Token efficiency + code review |
| **Forensics Features** | IOC analysis, threat hunts | **cybersec-agent** | python-developer | Domain expertise + implementation |

---

## Communication Protocol

### 1. Agent → Main Orchestrator

**When:** Sub-agent completes a todo or encounters a blocker  
**Format:** Structured report with:

```
## [AGENT-NAME] — [TODO-ID] Report

**Status:** [DONE|BLOCKED|IN_PROGRESS|ESCALATION]

### Summary
[Brief 1–2 line summary]

### Deliverables
- [ ] File 1: `/path/to/file.ext`
- [ ] File 2: `/path/to/file.ext`
- [ ] Test suite: `pytest tests/...`
- [ ] Verification: `uv run ruff check ...`

### Metrics
- Lines of code: XXX
- Test coverage: XX%
- Execution time: XXs
- Blockers: [None | Description]

### Sign-Off
✓ Type hints complete (mypy clean)  
✓ Tests passing (60%+ coverage)  
✓ Linting passing (ruff clean)  
✓ Code review ready
```

### 2. Main Orchestrator → Sub-Agent

**Trigger:** New todo assignment  
**Format:** Clear task statement with:

```
## Todo Assignment: [TODO-ID] — [Title]

### Context
[Why this todo? What does it depend on?]

### Acceptance Criteria
- [ ] Specific deliverable 1
- [ ] Specific deliverable 2
- [ ] Testing requirement
- [ ] Documentation requirement

### Related Todos
- Depends on: T###
- Enables: T###

### Agent Notes
[Special requirements, architectural notes, security constraints]
```

### 3. Sub-Agent → Sub-Agent (Coordination)

**Scenario:** python-developer and python-code-reviewer need coordination  
**Protocol:**

1. **Developer** produces code + preliminary tests
2. **Reviewer** runs analysis (read-only)
3. **Reviewer** produces report with CRITICAL/HIGH/MEDIUM findings
4. **Developer** receives report, implements fixes (escalates CRITICAL issues to cybersec-agent)
5. **Reviewer** re-audits; signs off when clean

---

## Result Validation

### Code Deliverables (Acceptance Checklist)

**For all Python code submissions:**

```
✓ Type hints complete (no `Any` types)
✓ Docstrings present (Google style for public methods)
✓ Tests written (60%+ coverage minimum)
✓ Linting passes: `ruff check src/ --fix && ruff format src/`
✓ Async patterns correct (no blocking I/O, proper `await`)
✓ ORM usage exclusive (no raw SQL)
✓ Pydantic v2 validation on all inputs
✓ Crypto: BLAKE2b-256 hashing, Ed25519 signing, Argon2id KDF, AES-256-GCM
✓ No hardcoded secrets, credentials, or API keys
✓ Ed25519 signed artifact (if cryptographic)
✓ Git commit message includes todo ID (e.g., "T361: Implement User ORM model")
```

**For all Frontend code submissions:**

```
✓ React component proper structure
✓ TypeScript strict mode compliant
✓ Accessibility considerations (ARIA labels, keyboard nav)
✓ Responsive design (mobile, tablet, desktop)
✓ Props properly typed (no implicit `any`)
✓ Tests passing (Playwright E2E or Jest unit)
✓ No console errors/warnings in dev build
✓ Follows CyberSecSuite design system
```

**For all Documentation submissions:**

```
✓ Markdown formatting valid (no broken links)
✓ Code examples accurate and runnable
✓ Cross-references valid (internal links work)
✓ Tables properly formatted
✓ Headings hierarchical (no jumps: h1 → h3)
✓ External references include URLs with access dates
```

### Verification Commands

**Python:**
```bash
# Type checking
mypy src/ --strict --no-implicit-optional

# Linting + formatting
ruff check src/ --fix
ruff format src/

# Testing with coverage
pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=60

# Security audit
pip-audit

# Build verification
python -m py_compile src/**/*.py
```

**Frontend:**
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Testing
npm run test

# Build
npm run build
```

### Approval Workflow

1. **Agent submits:** Deliverable + validation report
2. **Main verifies:** Runs acceptance checklist
3. **Secondary reviews:** Code review for CRITICAL findings
4. **Approve:** Mark todo as `done` if all checks pass
5. **Block:** Return with specific gaps if validation fails

---

## Merge Strategy

### Sequential Phase Completion

**T361–T368 (Backend Infrastructure):**
1. python-developer codes models + fixtures
2. python-code-reviewer audits (read-only)
3. Developer implements HIGH/CRITICAL fixes
4. Reviewer re-audits and signs off
5. Merge to main branch

**React Migration (Frontend):**
1. frontend-design creates components
2. python-developer (API) ensures endpoints ready
3. E2E tests passing (Playwright)
4. Merge feature branch to main

**Performance Tuning (Later):**
1. token-optimizer produces caching strategy doc
2. python-developer implements caching
3. Benchmarks show token reduction
4. Merge optimization branch

### Merge Commit Format

```
git commit -m "Phase N: [Todo IDs] — [Feature Description]

Closes T###, T###, T###

Agent Roles:
- python-developer: Core implementation
- python-code-reviewer: Security & pattern audit
- frontend-design: UI components

Metrics:
- Files: N changed, +XXX−YYY lines
- Coverage: XX% → XX%
- Performance: Xms → Yms
- Sign-offs: developer ✓, reviewer ✓

Verification:
- Tests: N passed, 0 failed
- Linting: ruff ✓, mypy ✓
- Crypto: BLAKE2b-256 ✓, Ed25519 ✓
"
```

---

## Escalation Paths

| Scenario | Escalate To | Reason |
|----------|-------------|--------|
| Cryptographic misuse detected | cybersec-agent | Security domain expertise |
| SQL injection risk | cybersec-agent | Security risk |
| Async race condition | python-developer | Concurrency expertise |
| Token budget exceeded | token-optimizer | Context management |
| Type system uncertainty | python-developer | Type safety architect |
| Design system violation | frontend-design | UX/design standards |
| Architecture decision needed | cybersec-agent | Strategic decisions |

---

## Tool & Environment Constraints

### Python Development

```
Python Version: >=3.14
Package Manager: uv (NEVER pip)
ORM: Tortoise ORM (MANDATORY for all DB access)
Validation: Pydantic v2 (MANDATORY for all input validation)
Crypto: cryptography library only (Ed25519, BLAKE2b, Argon2id, AES-256-GCM)
Testing: pytest + pytest-asyncio + pytest-cov (60%+ minimum)
Linting: ruff (format + check)
Async: asyncio + uvloop (Linux only)
```

### Frontend Development

```
Framework: React 19+ (with Context API, not Redux)
Language: TypeScript (strict mode)
Build: Vite
Testing: Playwright (E2E) + Jest (unit)
Styling: Tailwind CSS + custom components
Package Manager: npm (use package.json)
Node Version: >=18.0.0
```

### Database

```
Engine: PostgreSQL >=15
Client: asyncpg (async driver)
ORM: Tortoise ORM (async ORM)
Migrations: Aerich (with Tortoise)
No raw SQL in application code
```

---

## Metrics & Reporting

### Per-Todo Metrics

| Metric | Target | Threshold |
|--------|--------|-----------|
| Test Coverage | 70%+ | 60% minimum |
| Type Hint Completion | 100% | 95% minimum |
| Lint Errors | 0 | 5 maximum (warning level) |
| Documentation Completeness | 100% | 80% minimum |
| Build Time | <2min | <5min |
| Test Execution Time | <30s | <60s |

### Phase-Level Metrics

| Phase | Todos | Estimated Hours | Target Date | Agent Lead |
|-------|-------|-----------------|-------------|-----------|
| Phase 1 (Planning) | T357, T369, T374, plan-mode, sidebar-map | 8–10 | 2026-04-26 | Main |
| Phase 2 (Backend) | T361–T368 | 16–20 | 2026-05-03 | python-developer |
| Phase 3 (Frontend) | T### | 12–16 | 2026-05-10 | frontend-design |

---

## Sign-Off & Version Control

### Commit Message Requirements

Every commit must include:

```
[PHASE-N] [TODO-ID] — [Feature]

Description of changes.

Agent: [AGENT-NAME]
Review: [REVIEWER-AGENT] ✓ (or PENDING)
Tests: N passed
Coverage: XX%
Security: [Ed25519 ✓|Pending]
```

### Pull Request Template

```
## Todo: [TODO-ID]

### Changes
- Item 1
- Item 2

### Acceptance Criteria
- [x] Criterion 1
- [x] Criterion 2

### Agent Sign-Offs
- [ ] Developer: Production-ready code
- [ ] Reviewer: Security & patterns audit
- [ ] Tests: 60%+ coverage
- [ ] Linting: ruff + mypy clean

### Verification
`uv run pytest tests/ -v --cov=src --cov-fail-under=60`
```

---

## References

- **Agents:** `.claude/agents/sub_agents/*.md`
- **Plans:** `plans/plan.md`
- **CI/CD:** `.github/workflows/`
- **Python Standards:** `DEPENDENCIES.md`
- **Code Style:** `ruff.lint`, `.ruff.toml`

---

**Next Steps:** Assign Phase 2 todos to python-developer; await completion reports.
