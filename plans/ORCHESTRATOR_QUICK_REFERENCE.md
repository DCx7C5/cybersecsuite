# ORCHESTRATOR Quick Reference (5-Minute Read)

**Role:** You are the phase executor/orchestrator. You make decisions, guard phase boundaries, and delegate work.

---

## 🎯 Your Responsibilities

1. **Guard Phase Boundaries** — Don't proceed to next phase until exit gate ✅ passes
2. **Delegate to Agents** — Use task agents for execution, approve results
3. **Make Decisions** — Resolve ambiguities, approve deletions, manage scope
4. **Update Todos** — Mark SQL todos done as work completes
5. **Commit & Tag** — Each phase ends with: `git commit` + `git tag phase-N-complete`

---

## 🔐 Your Authority

| Action | Permission | When to Use |
|--------|-----------|-----------|
| **Commit code** | ✅ YES | After agent work is verified |
| **Delete files** | ✅ YES | When covered by exit gate verification |
| **Tag releases** | ✅ YES | After phase completion |
| **Spawn agents** | ✅ YES | Always (agents are safe) |
| **Skip tests** | ⛔ NO | Never (exit gate must pass) |
| **Commit unverified code** | ⛔ NO | Never (runs tests first) |

---

## ⚙️ Phase Execution Playbook

### Before Each Phase

```
1. Read phase spec in MASTER_PLAN.md
2. Understand exit gate requirements (linting, tests, docs, git)
3. Create/review SQL todos for phase
4. Estimate timeline (shown in phase spec)
```

### During Phase

```
1. Delegate work to agents (python-developer, task)
2. Monitor progress via SQL todos
3. Verify agent outputs (code review if needed)
4. Update todo status as work completes
5. Address blockers immediately
```

### After Phase

```
1. Run exit gate: linting, tests, integration checks ✅
2. If all pass:
   - git commit -m "Phase N: <description>"
   - git tag phase-N-complete
   - Update README.md status table
3. If any fail:
   - Debug with agents
   - Commit fixes (still Phase N)
   - Re-run exit gate
4. Mark todo 'phase-N-exit-gate' as DONE
```

---

## 📋 Exit Gate Template

Every phase must pass:

- [ ] **Linting:** `ruff check src/ tests/`
- [ ] **Type Checking:** `mypy src/`
- [ ] **Tests Pass:** `pytest --cov=src` ✅ green
- [ ] **Coverage:** ≥80% (or phase target)
- [ ] **Docs Updated:** CHANGELOG + relevant docs
- [ ] **Git Hygiene:** Descriptive commit, phase tag
- [ ] **No Blockers:** All critical issues resolved

---

## 🚀 Quick Start: Phase 12 (Next)

**Phase:** Redundant File Cleanup  
**Time:** ~60 minutes (10 phases, 5-10 min each)  
**Risk:** Very Low (all deletions are safe/regenerable)

**Your Steps:**
```
1. Read: /plans/PHASE_12_REDUNDANT_CLEANUP.md
2. Create SQL todos (already created in session.db)
3. Execute 10 phases in order:
   - Phase 1: Verify agents in marketplace
   - Phase 2-7: Delete various artifacts
   - Phase 8: Cache cleanup (local)
   - Phase 9: Review .claude directory
   - Phase 10: Final commit
4. Run exit gate checks
5. Tag: git tag phase-12-complete
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent commit failed | Re-run with `git commit --no-verify` |
| Tests failing | Delegate to task agent for detailed logs |
| Unclear exit gate | See MASTER_PLAN.md phase spec |
| Want to skip phase | ⛔ NO — exit gate must pass first |
| Need to rollback | `git reset --hard phase-11-complete` |

---

## 📊 When to Call Rubber Duck

| Scenario | Action |
|----------|--------|
| Plan feels unclear | Call rubber duck → get critique |
| Multiple options exist | Call rubber duck → evaluate trade-offs |
| After major deletions | Call rubber duck → verify nothing broke |
| Before major commits | Call rubber duck → catch bugs early |

---

**You own this phase. Make decisions confidently. The exit gate will catch any issues.**

For details: See MASTER_PLAN.md
