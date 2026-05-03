# 📦 MODULES ARCHITECTURE (INDEX)

This directory contains documentation for all **22 CyberSecSuite modules**.

**Last Updated**: 2026-05-03 | **Source**: src/css/modules/ audited and synced

---

## All Modules (22 Total)

| Module | Doc | Files | Lines | Status | 5-File | Priority |
|--------|-----|-------|-------|--------|--------|----------|
| **@agents** | [agents.md](agents.md) | 4 | 69 | ❌ Stub | ⚠️ 2/5 | 🟡 Med |
| **@cache** | [cache.md](cache.md) | 3 | 47 | ❌ Stub | ⚠️ 1/5 | 🔴 HIGH |
| **@capabilities** | [capabilities.md](capabilities.md) | 1 | 188 | ⚠️ Minimal | ❌ 0/5 | 🟡 Med |
| **@chat** | [chat.md](chat.md) | 2 | 0 | ❌ Empty | ⚠️ 1/5 | 🟡 Med |
| **@css_a2a** | [css_a2a.md](css_a2a.md) | 1 | 0 | ❌ BLOCKED | ❌ 0/5 | 🔴 BLOCKED |
| **@events** | [events.md](events.md) | 1 | 0 | ❌ Empty | ❌ 0/5 | 🔴 HIGH |
| **@google_a2a** | [google_a2a.md](google_a2a.md) | 12 | 955 | ⚠️ Partial | ✅ 7/5 | 🟡 Med |
| **@llm_models** | [llm_models.md](llm_models.md) | 2 | 4 | ❌ Stub | ❌ 1/5 | 🟢 Low |
| **@marketplace** | [marketplace.md](marketplace.md) | 10 | 1150 | ✅ Functional | ✅ 5/5 | 🟡 Med |
| **@memory** | [memory.md](memory.md) | 1 | 1491 | ⚠️ Complex | ❌ 1/5 | 🔴 HIGH |
| **@orchestration** | [orchestration.md](orchestration.md) | 11 | 458 | ⚠️ Partial | ⚠️ 3/5 | 🔴 CRIT |
| **@permissions** | [permissions.md](permissions.md) | 1 | 0 | ❌ Empty | ❌ 0/5 | 🔴 CRIT |
| **@roles** | [roles.md](roles.md) | 2 | 173 | ⚠️ Partial | ⚠️ 2/5 | 🟡 High |
| **@scopes** | [scopes.md](scopes.md) | 2 | 77 | ⚠️ Minimal | ⚠️ 1/5 | 🟡 Med |
| **@skills** | [skills.md](skills.md) | 4 | 50 | ❌ Stub | ⚠️ 2/5 | 🟡 Med |
| **@streaming** | [streaming.md](streaming.md) | 8 | 841 | ⚠️ Partial | ⚠️ 2/5 | 🟡 Med |
| **@tags** | [tags.md](tags.md) | 4 | 111 | ⚠️ Partial | ✅ 4/5 | 🟢 Low |
| **@tasks** | [tasks.md](tasks.md) | 5 | 556 | ⚠️ Partial | ✅ 5/5 | 🔴 CRIT |
| **@teams** | [teams.md](teams.md) | 4 | 210 | ⚠️ Partial | ⚠️ 2/5 | 🔴 CRIT |
| **@tools** | [tools.md](tools.md) | 1 | 86 | ⚠️ Minimal | ❌ 1/5 | 🟡 Med |
| **@triage** | [triage.md](triage.md) | N/A | N/A | ❓ Unknown | ? | 🟡 Med |
| **@working_dir** | [working_dir.md](working_dir.md) | 1 | 0 | ❌ Empty | ❌ 0/5 | 🟡 Med |

---

## Summary by Status

| Status | Count | Examples |
|--------|-------|----------|
| **✅ Functional** | 1 | marketplace (1150 lines, full 5-file) |
| **⚠️ Partial** | 8 | google_a2a, orchestration, tasks, teams, streaming, roles, scopes, tags |
| **⚠️ Minimal** | 3 | capabilities, llm_models, tools |
| **⚠️ Complex** | 1 | memory (1491 lines, fragmented) |
| **❌ Stub** | 5 | agents, cache, chat, skills, llm_models |
| **❌ Empty** | 4 | css_a2a, events, permissions, working_dir |
| **❓ Unknown** | 1 | triage (not audited yet) |

---

## Key Issues

### 🔴 CRITICAL BLOCKERS

1. **CSS A2A Code Location** (HIGHEST PRIORITY)
   - A2A code lives in `google_a2a/` (a2a_comms.py, dispatcher.py, int_comms.py)
   - Should live in `css_a2a/` (currently empty)
   - **Action**: Move files + update imports in google_a2a/__init__.py
   - **Blocking**: A2A communication, orchestrator delegation

2. **Permissions Module Empty** (SECURITY CRITICAL)
   - 0% implemented (src/css/modules/permissions/__init__.py is empty)
   - Documented in .plan/permissions.md but no code
   - **Action**: Implement decorators, middleware, scope enforcement
   - **Blocking**: RBAC, role enforcement, scope isolation

3. **Events Module Empty** (HIGH PRIORITY)
   - 0% implemented (src/css/modules/events/__init__.py is empty)
   - Marked HIGH priority in documentation
   - **Action**: Create EventBus, @on_event decorator, event types
   - **Blocking**: Agent notifications, marketplace events, task events

### 🟠 HIGH PRIORITY

4. **Memory Module Complex** (1491 lines, fragmented)
   - All code in single __init__.py file
   - Needs 5-file pattern: types.py, models.py, exceptions.py, enums.py
   - **Action**: Consolidate to 5-file pattern

5. **Cache Module Incomplete** (95% gap)
   - Only has base.py + exceptions.py (47 lines total)
   - Documented L1-L4 architecture completely missing
   - **Action**: Implement async cache backends (Redis, PostgreSQL, SQLite)

---

## 5-File Pattern Compliance

**Fully Compliant (5/5)**:
- ✅ marketplace
- ✅ tasks
- ✅ tags (4/5, nearly complete)

**Partial Compliance (2-4/5)**:
- google_a2a (7 files - overcomplicated)
- orchestration (3/5)
- teams (2/5)
- roles (2/5)
- streaming (2/5)
- skills (2/5)
- agents (2/5)
- scopes (1/5)
- capabilities (0/5 - utility only)

**Non-Compliant (0-1/5)**:
- ❌ css_a2a, events, permissions, working_dir (empty)
- ❌ chat, llm_models, tools, memory (minimal)

---

## Docker Integration

All modules run inside **cybersec-proxy** (FastAPI, port 8765):

- **@cache** → Accessed by all modules (Redis, PostgreSQL, Disk)
- **@capabilities** → Called during startup (registry discovery)
- **@chat** → Exposes `/chat` endpoints
- **@css_a2a** → Runs inside orchestrator processes (blocked by location issue)
- **@google_a2a** → Exposes `/a2a/*` endpoints
- **@events** → Event bus (emits to UniversalSDK, currently missing)
- **@llm_models** → Loaded at startup (in-memory registry)
- **@marketplace** → Exposes `/marketplace/*` endpoints (installs packages)
- **@memory** → Working memory management (1491 lines, needs consolidation)
- **@orchestration** → Multi-orchestrator coordination
- **@permissions** → RBAC enforcement (currently missing)
- **@roles** → Role definitions & assignment
- **@scopes** → Scope hierarchy management
- **@skills** → Skill definitions & execution
- **@streaming** → SSE and streaming support
- **@tags** → Tag management & categorization
- **@tasks** → Task lifecycle & execution
- **@teams** → Team management & isolation
- **@tools** → Tool registry & execution
- **@triage** → ❓ Unknown
- **@working_dir** → Working directory management (currently missing)

---

## Next Steps (Priority Order)

### IMMEDIATE (This Session)
1. ✅ Move CSS A2A code to css_a2a/ folder
2. ✅ Fix imports in google_a2a/__init__.py
3. ✅ Update this INDEX.md with actual status

### WEEK 1 (Blockers)
4. Implement permissions module (RBAC critical)
5. Create events module (event bus)
6. Fix cache L1-L4 backends
7. Consolidate memory to 5-file pattern

### WEEK 2 (Gaps)
8. Complete orchestration (remove tasks import)
9. Implement agents module (models.py, endpoints.py)
10. Implement skills module (models.py, endpoints.py)
11. Implement tools module (full registry + execution)

### WEEK 3+ (Polish)
12. Complete working_dir implementation
13. Verify all modules follow 5-file pattern
14. Add logger initialization to all __init__.py files
15. Cross-module dependency validation

---

**Status**: 📊 1/22 fully functional | ⚠️ 8 partial | ❌ 4 empty | 📈 67% implementation gap

**Last Updated**: 2026-05-03  
**Audit Source**: /home/daen/Projects/cybersecsuite/src/css/modules/ direct scan
