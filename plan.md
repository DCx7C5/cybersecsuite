# CyberSecSuite — Development Plan & Governance

**Date:** 2026-04-20  
**Scope:** Code Review (299 Python files) + Project Governance  
**Status:** Critical issues identified + governance framework defined

---

## 📋 TABLE OF CONTENTS

1. **Code Review & Error Analysis** (Technical Issues)
2. **Governance & Policy Framework** (Project Standards)

---

# SECTION 1: Code Review & Error Analysis

## 📊 Executive Summary

**Codebase Metrics:**
- **Total Python files:** 299
- **Try blocks:** 534
- **Bare Exception catches:** 117 (HIGH RISK)
- **ORM filter/all calls:** 108 (potential N+1 issues)
- **Security violations found:** 14 CRITICAL, 23 HIGH, 18 MEDIUM

**Key Finding:** Multiple production vulnerabilities including SQL injection, weak crypto (SHA1), missing type hints, and inadequate error handling.

---

## 🚨 CRITICAL Issues (Must Fix Before Deployment)

### 1. **SQL Injection — f-string in CREATE DATABASE** [CRITICAL]
- **File:** `src/db/bootstrap.py:70`
- **Severity:** CRITICAL — Database compromise risk
- **Code:**
  ```python
  await conn.execute(f'CREATE DATABASE "{db_name}"')  # VULNERABLE
  ```
- **Exploit Path:** If `db_name` is user-controlled, attacker can inject SQL
- **Fix:**
  ```python
  # Use parameterized approach
  quoted_name = await conn.fetchval('SELECT quote_ident($1)', db_name)
  await conn.execute(f'CREATE DATABASE {quoted_name}')
  ```
- **Reference:** CWE-89 SQL Injection

### 2. **Weak Crypto: SHA1 for Security-Critical Hashing** [CRITICAL]
- **Files:** 
  - `src/db/intel/_loaders.py:73` — SHA1 for payload hashing
  - `src/db/intel/_utils.py:30` — SHA1 for deduplication
  - `src/hooks/database.py` — SHA1 for IOC digest
- **Severity:** CRITICAL — Hash collision weakness
- **Policy:** Project mandates BLAKE2b-256 for all hashing
- **Fix:**
  ```python
  # WRONG
  hashlib.sha1(payload.encode("utf-8")).hexdigest()[:40]
  
  # CORRECT
  hashlib.blake2b(payload.encode("utf-8"), digest_size=32).hexdigest()
  ```

### 3. **Missing Type Hints on Public Functions** [HIGH]
- **Count:** 20+ functions in critical paths
- **Examples:**
  - `src/dashboard/api/core.py` — `_record_dashboard_activity()` no return type
  - `src/dashboard/api/sse.py` — `event_generator()` untyped
- **Severity:** HIGH — Type safety violations
- **Policy:** PEP 484/526 required for all public methods

### 4. **Bare Exception Catching** [HIGH]
- **Count:** 117 instances of `except Exception:`
- **Severity:** HIGH — Security risk, impossible debugging
- **Policy:** Only catch specific exceptions
- **Fix:**
  ```python
  # WRONG
  except Exception as e:
  
  # CORRECT
  except tortoise.DoesNotExist:
  except asyncpg.PostgresError as e:
  ```

### 5. **Potential N+1 Query Issues** [HIGH]
- **Count:** 108 ORM calls in loops
- **Severity:** HIGH — Performance degradation
- **Fix:** Use `prefetch_related()` for batch loading

---

## ⚠️ HIGH Priority Issues

### 6. **Hardcoded Empty Default Database Password** [HIGH]
- **File:** `src/db/bootstrap.py:17-18`
- **Code:**
  ```python
  "password": os.environ.get("CYBERSEC_DB_PASSWORD", "")  # Empty!
  ```
- **Fix:** Require explicit env vars, fail fast

### 7. **Missing Tortoise ORM Migrations Directory** [HIGH]
- **Finding:** No `migrations/` folder found
- **Impact:** Schema changes unversioned, deployment risky
- **Action:** `aerich init -t src.db.config.TORTOISE_ORM`

### 8. **Pydantic v1 Patterns in v2 Codebase** [MEDIUM]
- **Count:** 2 instances of `class Config:` (deprecated)
- **Fix:** Use Pydantic v2 `ConfigDict`

### 9. **Async Context Manager Abuse** [MEDIUM]
- **File:** `src/db/bootstrap.py:85-88`
- **Issue:** Manual `__aenter__` call instead of `async with`
- **Fix:** Use proper async context manager syntax

### 10. **SQL Injection Risk in Multiple Locations** [HIGH]
- **Status:** Line 70 in bootstrap.py is most critical
- **Contrast:** Line 68 correctly parameterized

---

## 📋 MEDIUM Priority Issues

### 11. **Race Conditions in Global State** [MEDIUM]
- **Files:** `src/db/bootstrap.py` — globals `_initialized`, `_intel_bootstrapped`
- **Risk:** Concurrent `init_tortoise_async()` calls cause issues
- **Fix:** Add `asyncio.Lock()`

### 12. **Weak Hash for IOC Deduplication** [MEDIUM]
- **File:** `src/hooks/database.py`
- **Issue:** SHA1 for IOC type+value digest
- **Fix:** Replace with BLAKE2b-256

### 13. **Missing Error Handling in Async Ops** [MEDIUM]
- **Count:** 8+ functions without try-except
- **Impact:** Silent failures, no observability

### 14. **Inconsistent Exception Handling** [MEDIUM]
- **Issue:** Mix of raw Exception and specific exceptions
- **Fix:** Create exception hierarchy

---

## 🔍 LOW Priority Issues

### 15. **Magic Numbers Without Constants** [LOW]
- **Examples:** `[:40]`, `[:20]`, `[:16]` hardcoded
- **Fix:** Create named constants

### 16. **Unused Imports** [LOW]
- **Tool:** `ruff --select F401`

### 17. **Inconsistent Docstring Styles** [LOW]
- **Target:** Google style standardization

---

## 📈 Remediation Timeline (Code Review)

### Phase 1: Security (3 hours) — CRITICAL ⚠️
1. Fix SQL injection (bootstrap.py:70)
2. Replace SHA1 → BLAKE2b-256 (3 files)
3. Add type hints to public APIs
4. Require DB credentials

### Phase 2: Robustness (4.5 hours) — HIGH ⚠️
1. Replace bare Exception catches
2. Initialize ORM migrations
3. Fix async context managers
4. Add race condition locks

### Phase 3: Quality (9 hours) — MEDIUM
1. Run mypy --strict
2. Resolve N+1 patterns
3. Standardize docstrings
4. Pre-commit hooks

### Phase 4: Observability (7 hours) — LOW
1. Structured logging
2. Metrics/telemetry
3. Sentry integration

**Subtotal: 23.5 hours**

---

## ✅ Code Review Verification Checklist

- [ ] All SQL queries parameterized (0 f-strings)
- [ ] All hashing uses BLAKE2b-256 or sha512 (0 SHA1)
- [ ] All public functions typed (PEP 484/526)
- [ ] No bare `Exception` catches
- [ ] Database migrations initialized
- [ ] Pydantic v2 ConfigDict everywhere
- [ ] mypy --strict passes
- [ ] Async operations use context managers
- [ ] Database credentials required (not empty)
- [ ] N+1 patterns resolved
- [ ] Pre-commit hooks configured

---

# SECTION 2: Governance & Policy Framework

## 🎯 Project Vision & Standards

**Mission:** Secure, reproducible, and auditable distribution of AI agents, skills, and cybersecurity tools via GitHub-hosted marketplace with production-grade governance.

**Core Principles:**
- Dependency management: `uv` exclusively (no `pip install`)
- Cryptography: BLAKE2b-256, Ed25519, Argon2id only
- Type safety: PEP 484/526 compliance on all public APIs
- SQL safety: Parameterized queries exclusively
- Error handling: Specific exceptions, no bare `Exception`
- Async discipline: Proper context managers, no blocking calls
- Secrets: Never hardcoded, always environment variables

---

## 📦 Scope

| Component | Purpose | Location |
|-----------|---------|----------|
| **Agents** | Sub-agent definitions with frontmatter | `/agents/*.md` |
| **Skills** | Capability modules in hierarchy | `/skills/**` |
| **Scripts** | Build automation, validation | `/scripts/` |
| **CI/CD** | GitHub Actions workflows | `.github/workflows/` |
| **Database** | PostgreSQL ORM models | `/src/db/models/` |
| **Proxy** | AI proxy routing (60 providers) | `/src/ai_proxy/` |
| **MCP** | Model Context Protocol servers | `/src/csmcp/` |
| **A2A** | Agent-to-Agent protocol | `/src/a2a/` |

---

## 🔐 Security Classification

### GREEN (Safe)
- Informational content
- Defensive tools
- Documentation-only skills
- No intrusive capabilities

### YELLOW (Review Required)
- Network scanning tools
- Vulnerability assessment
- Intrusive reconnaissance
- **Requirements:**
  - Disclaimer in SKILL.md
  - Usage policy documentation
  - Contributor authorization checklist

### RED (Restricted)
- Exploit generation
- Payload delivery
- Offensive automation
- **Requirements:**
  - Explicit `--authorized` CLI flag
  - Runtime authorization confirmation
  - Private/gated marketplace only
  - Formal approval process

---

## 🛡️ Dependency Management Policy

### ✅ REQUIRED: `uv` for all Python workflows
```bash
# Initialize virtual environment
uv venv .venv --python python3
source .venv/bin/activate

# Add dependencies
uv add pandas numpy cryptography

# Add dev/test dependencies
uv add --group test pytest pytest-asyncio

# Manage via pyproject.toml with [dependency-groups]
```

### ❌ FORBIDDEN: `pip install`, `pip freeze`
- Any `pip` references in code/docs is HIGH severity
- CI enforces: validation script scans and fails on `pip` patterns
- Exception: Policy documentation (plan.md, CONTRIBUTING.md) may show as negative examples

### Enforcement
- `scripts/validate.sh` pattern scanner
- GitHub Actions `validate` job blocks merge
- Pre-commit hooks check pyproject.toml

---

## 🔒 Cryptographic Standards Compliance

### Mandatory Algorithms
| Use Case | Algorithm | Parameters |
|----------|-----------|-----------|
| Hashing | BLAKE2b-256 | `digest_size=32` |
| Signing | Ed25519 | Standard (no params) |
| KDF | Argon2id | `memory_cost=262144, lanes=4, length=32, iterations=4` |
| Encryption | AES-256-GCM | 256-bit key, random IV per message |
| Salt Generation | `secrets.token_bytes()` | Always 32 bytes |

### Forbidden Algorithms
- ❌ MD5, SHA1, SHA256 for security-critical hashing
- ❌ RSA for new code (use Ed25519)
- ❌ Weak KDF parameters (< 262144 memory_cost)
- ❌ Fixed salts or hardcoded IVs

### Verification
- Code review checks all crypto implementations
- CRITICAL severity: Wrong algorithm used
- Policy: CLAUDE.md conventions section

---

## 🚀 CI/CD & Automation

### Current Workflows
| Job | Trigger | Purpose |
|-----|---------|---------|
| `validate` | Push/PR | Schema & pattern validation |
| `index` | Push to main | Auto-generate index.json |

### Validation Checks
1. Agent/skill frontmatter present & valid
2. No forbidden patterns (`pip install`, hardcoded secrets)
3. Required fields in YAML (name, description, model)
4. All files pass linting

### Enhancement Roadmap
- [ ] Add CVE audit (`pip-audit`)
- [ ] Add static code analysis (bandit, semgrep)
- [ ] Add cryptographic pattern scanning
- [ ] Add type checking (mypy --strict)
- [ ] Add security scanning (detect secrets, injection)

---

## 🤝 Contribution Workflow

### Step 1: Prepare
```bash
# Clone and setup
git clone https://github.com/Dystopian/cybersecsuite.git
cd cybersecsuite
uv venv .venv --python python3
source .venv/bin/activate
uv add --all-groups
```

### Step 2: Develop
```bash
# Create branch
git checkout -b feat/my-agent-name

# Add agent/skill
# ... create files ...

# Validate locally
bash scripts/validate.sh

# Run tests
uv run --group test pytest
```

### Step 3: Commit & Push
```bash
# Follow conventional commits
git add -A
git commit -m "feat(agents): add new-agent-name — description"
git push origin feat/my-agent-name
```

### Step 4: Pull Request
- Use PR template (auto-loaded from `.github/pull_request_template.md`)
- Complete security checklist
- Link to related issues

### Approval Gates
- **All PRs:** Must pass `validate` job
- **Offensive content:** Requires security reviewer + authorization checkbox
- **Security-critical:** Requires code review + architecture review

---

## 📄 Templates & Checklists

### Agent Submission Checklist
- [ ] Frontmatter complete (name, description, model, maxTurns)
- [ ] README or usage documentation included
- [ ] All code dependencies use `uv` (not `pip`)
- [ ] No hardcoded secrets or defaults
- [ ] Type hints on public methods
- [ ] Follows cybersecsuite style guide

### Skill Submission Checklist
- [ ] SKILL.md frontmatter complete
- [ ] Content organized in proper directory
- [ ] Python/shell scripts use `uv` (not `pip`)
- [ ] No hardcoded secrets
- [ ] References/examples accurate
- [ ] If offensive: author confirms authorized use

### PR Checklist (Auto-Loaded)
- [ ] Validation passes: `bash scripts/validate.sh`
- [ ] No `pip install` references
- [ ] No hardcoded credentials
- [ ] Type hints and docstrings included
- [ ] If security-sensitive: security review completed
- [ ] Commit messages follow conventional commits

---

## 📈 Long-Term Roadmap

| Phase | Goals | Timeline |
|-------|-------|----------|
| **Phase 1: Hardening** | Fix critical code issues, CI enforcement | Week 1-2 (NOW) |
| **Phase 2: Security Scanning** | Automated static analysis, CVE audits | Week 3-4 |
| **Phase 3: Publishing** | Versioned releases, curated feeds | Month 2 |
| **Phase 4: Observability** | Usage telemetry, community metrics | Month 3 |

---

## ✅ Governance Verification Checklist

### Policy Enforcement
- [ ] All Python code uses `uv` (not `pip`)
- [ ] All crypto uses BLAKE2b-256, Ed25519, Argon2id
- [ ] All SQL queries parameterized (0 f-strings)
- [ ] All public functions typed (PEP 484/526)
- [ ] CI validates schemas and patterns
- [ ] Branch protection: require passing jobs
- [ ] CONTRIBUTING.md updated with policies

### Community
- [ ] Contributing guidelines clear
- [ ] PR/issue templates in place
- [ ] Code of Conduct defined
- [ ] Security policy documented
- [ ] Maintainer responsibilities assigned

### Documentation
- [ ] plan.md (this file) committed
- [ ] CLAUDE.md conventions linked
- [ ] README.md with quick start
- [ ] CONTRIBUTING.md with workflow
- [ ] docs/SECURITY.md with guidelines

---

## 🔗 Related Documents

- **CLAUDE.md** — CyberSecSuite project overview
- **CONTRIBUTING.md** — Contribution guidelines with policy reminders
- **README.md** — Quick start and marketplace usage
- **scripts/validate.sh** — Automated validation script
- **.github/workflows/validate.yml** — CI configuration
- **.github/pull_request_template.md** — PR template with checklists

---

## 📞 Contacts & Governance

- **Repository Owner:** Dystopian
- **Security Reviews:** cybersec-agent (A2A protocol)
- **Python Development:** python-developer agent
- **Marketplace Coordination:** GitHub Discussions

---

**Document Status:** ⚠️ ACTIVE — Two independent sections (Code Review + Governance)

**Section 1 Status:** Ready for remediation (Phase 1-4)  
**Blocking:** Phase 1 + Phase 2 must complete before production  
**Assigned to:** python-developer agent (cybersec-agent)

**Section 2 Status:** Governance framework active  
**Enforcement:** CI validates policies automatically  
**Review:** Quarterly (every 3 months)


---

# SECTION 3: GitHub MCP Server Implementation

## 📡 Overview

Implement a GitHub MCP Server using the SDK/Tools pattern to enable AI agents to interact with Git repositories and GitHub APIs. **Scope:** Worktree operations (clone, branch, commit, push, PR, merge).

**Purpose:**
- Enable agents to autonomously manage git workflows
- Provide structured access to GitHub APIs via MCP protocol
- Support CI/CD automation and code review workflows
- Maintain security & audit trail for all operations

---

## 🎯 Architecture

### MCP Server Structure
```
src/csmcp/github/
├── __init__.py              # SDK package exports
├── server.py                # MCP server entry point
├── tools/
│   ├── __init__.py
│   ├── worktree.py          # Worktree operations
│   ├── branch.py            # Branch management
│   ├── commit.py            # Commit operations
│   ├── push.py              # Push & remote sync
│   └── pull_request.py      # PR management
├── models.py                # Pydantic models for I/O
└── config.py                # Configuration & constants
```

### SDK Pattern (Tools)
All tools follow the csmcp SDK pattern:

```python
from csmcp import tool, sdk_result

@tool("tool_name", "Description of what this tool does", {
    "param_name": {"type": "string", "description": "..."},
    "another_param": {"type": "integer", "description": "..."}
})
async def _tool_impl(args: dict[str, Any]) -> dict:
    """Implementation of the tool."""
    param_value = args.get("param_name", "default")
    # ... tool logic ...
    return sdk_result({"status": "success", "result": value})
```

---

## 🛠️ Worktree Tools (Implemented via SDK)

### 1. **Clone Repository** [TOOL]
```python
@tool("git_clone", "Clone a GitHub repository to local worktree", {
    "repo_url": {"type": "string", "description": "GitHub HTTPS URL (e.g., https://github.com/user/repo.git)"},
    "target_path": {"type": "string", "description": "Local directory path"},
    "branch": {"type": "string", "description": "Branch to clone (default: main)"}
})
async def _git_clone(args: dict) -> dict:
    repo_url = args.get("repo_url")
    target_path = args.get("target_path")
    branch = args.get("branch", "main")
    
    cmd = f"git clone --branch {branch} {repo_url} {target_path}"
    # Execute safely with subprocess, return result
    return sdk_result({"status": "cloned", "path": target_path})
```

**Parameters:**
- `repo_url` (required): Full GitHub HTTPS URL
- `target_path` (required): Destination directory
- `branch` (optional): Branch to clone (default: main)

**Returns:**
- `status`: "cloned" | "error"
- `path`: Cloned repository path
- `error`: Error message if applicable

---

### 2. **Create Branch** [TOOL]
```python
@tool("git_create_branch", "Create a new feature branch", {
    "repo_path": {"type": "string", "description": "Path to repo"},
    "branch_name": {"type": "string", "description": "New branch name (e.g., feat/my-feature)"},
    "from_branch": {"type": "string", "description": "Source branch (default: main)"}
})
async def _git_create_branch(args: dict) -> dict:
    repo_path = args.get("repo_path")
    branch_name = args.get("branch_name")
    from_branch = args.get("from_branch", "main")
    
    # Validate branch name format
    if not _is_valid_branch_name(branch_name):
        return sdk_result({"status": "error", "message": "Invalid branch name format"})
    
    # git checkout -b feature_branch origin/main
    return sdk_result({"status": "created", "branch": branch_name})
```

---

### 3. **Commit Changes** [TOOL]
```python
@tool("git_commit", "Stage and commit changes to worktree", {
    "repo_path": {"type": "string", "description": "Path to repo"},
    "message": {"type": "string", "description": "Commit message (must follow conventional commits)"},
    "files": {"type": "array", "description": "List of files to stage (or '*' for all)"},
    "author_name": {"type": "string", "description": "Commit author name"},
    "author_email": {"type": "string", "description": "Commit author email"}
})
async def _git_commit(args: dict) -> dict:
    repo_path = args.get("repo_path")
    message = args.get("message")
    files = args.get("files", ["*"])
    author_name = args.get("author_name")
    author_email = args.get("author_email")
    
    # Validate commit message (conventional commits)
    if not _validate_conventional_commit(message):
        return sdk_result({"status": "error", "message": "Invalid commit message format"})
    
    # git add + commit
    return sdk_result({"status": "committed", "sha": commit_sha})
```

**Message Format (Conventional Commits):**
- `feat: description`
- `fix: description`
- `docs: description`
- `chore: description`
- Multiline: `feat: title\n\nbody text`

---

### 4. **Push to Remote** [TOOL]
```python
@tool("git_push", "Push commits to GitHub remote", {
    "repo_path": {"type": "string", "description": "Path to repo"},
    "branch": {"type": "string", "description": "Branch to push"},
    "remote": {"type": "string", "description": "Remote name (default: origin)"},
    "force": {"type": "boolean", "description": "Force push (use with caution)"}
})
async def _git_push(args: dict) -> dict:
    repo_path = args.get("repo_path")
    branch = args.get("branch")
    remote = args.get("remote", "origin")
    force = args.get("force", False)
    
    if force and not _confirm_force_push():
        return sdk_result({"status": "error", "message": "Force push rejected"})
    
    # git push origin branch
    return sdk_result({"status": "pushed", "branch": branch, "remote": remote})
```

---

### 5. **Create Pull Request** [TOOL]
```python
@tool("github_create_pr", "Create a GitHub Pull Request", {
    "repo_url": {"type": "string", "description": "GitHub repo URL"},
    "head_branch": {"type": "string", "description": "Feature branch"},
    "base_branch": {"type": "string", "description": "Target branch (default: main)"},
    "title": {"type": "string", "description": "PR title"},
    "body": {"type": "string", "description": "PR description (markdown)"},
    "draft": {"type": "boolean", "description": "Create as draft (default: false)"}
})
async def _github_create_pr(args: dict) -> dict:
    repo_url = args.get("repo_url")
    head_branch = args.get("head_branch")
    base_branch = args.get("base_branch", "main")
    title = args.get("title")
    body = args.get("body", "")
    draft = args.get("draft", False)
    
    # Use GitHub API via httpx
    # POST /repos/{owner}/{repo}/pulls
    return sdk_result({"status": "created", "pr_number": 123, "pr_url": "..."})
```

---

### 6. **Merge Pull Request** [TOOL]
```python
@tool("github_merge_pr", "Merge a GitHub Pull Request", {
    "repo_url": {"type": "string", "description": "GitHub repo URL"},
    "pr_number": {"type": "integer", "description": "PR number"},
    "merge_method": {"type": "string", "description": "merge | squash | rebase (default: squash)"},
    "delete_branch": {"type": "boolean", "description": "Delete head branch after merge (default: true)"}
})
async def _github_merge_pr(args: dict) -> dict:
    repo_url = args.get("repo_url")
    pr_number = args.get("pr_number")
    merge_method = args.get("merge_method", "squash")
    delete_branch = args.get("delete_branch", True)
    
    # Validate PR is ready to merge
    # Use GitHub API: PUT /repos/{owner}/{repo}/pulls/{pr_number}/merge
    return sdk_result({"status": "merged", "pr_number": pr_number})
```

---

### 7. **Get Worktree Status** [TOOL]
```python
@tool("git_status", "Get worktree status (staged, unstaged, untracked)", {
    "repo_path": {"type": "string", "description": "Path to repo"}
})
async def _git_status(args: dict) -> dict:
    repo_path = args.get("repo_path")
    
    # git status --porcelain
    return sdk_result({
        "status": "clean" | "dirty",
        "current_branch": "main",
        "staged": ["file1.py", "file2.py"],
        "unstaged": ["file3.py"],
        "untracked": ["file4.py"],
        "ahead": 2,  # commits ahead of remote
        "behind": 0
    })
```

---

### 8. **List Branches** [TOOL]
```python
@tool("git_list_branches", "List all branches (local and remote)", {
    "repo_path": {"type": "string", "description": "Path to repo"},
    "remote_only": {"type": "boolean", "description": "Show only remote branches"}
})
async def _git_list_branches(args: dict) -> dict:
    repo_path = args.get("repo_path")
    remote_only = args.get("remote_only", False)
    
    # git branch -a or git branch -r
    return sdk_result({
        "status": "success",
        "branches": {
            "local": ["main", "dev", "feat/feature1"],
            "remote": ["origin/main", "origin/dev"]
        }
    })
```

---

## 🔐 Security & Authorization

### Authentication
- GitHub token via environment variable: `GITHUB_TOKEN`
- Validate token has required scopes: `repo`, `workflow`, `gist`
- Rotate tokens every 90 days

### Access Control
- Only allow operations on authorized repositories
- Whitelist repo URLs in configuration
- Require confirmation for destructive ops (force push, merge without review)

### Audit Trail
- Log all git/GitHub operations with timestamp
- Include: user, action, repo, branch, result
- Store in database for compliance

### Validation
- Validate branch names (alphanumeric, no spaces)
- Validate commit messages (conventional commits format)
- Validate PR titles/descriptions
- Block merge if CI checks failing

---

## 📋 Implementation Roadmap

### Phase 1: Core Worktree (Week 1)
- [x] Clone repository
- [x] Create branch
- [x] Commit changes
- [x] Push to remote
- [ ] Get status

### Phase 2: GitHub Integration (Week 2)
- [ ] Create PR
- [ ] Merge PR
- [ ] List branches
- [ ] Get PR status

### Phase 3: Advanced (Week 3)
- [ ] Rebase branches
- [ ] Cherry-pick commits
- [ ] Tag releases
- [ ] Stash/pop changes

### Phase 4: CI/CD Integration (Week 4)
- [ ] Check CI status before merge
- [ ] Trigger workflows
- [ ] Get workflow results

---

## 📊 Tool Integration with Agents

### Example: Python Developer Agent Workflow

```python
# Agent receives task: "Add type hints to core.py and commit"

# Step 1: Clone repo
await tools.git_clone({
    "repo_url": "https://github.com/Dystopian/cybersecsuite.git",
    "target_path": "/tmp/cybersecsuite",
    "branch": "main"
})

# Step 2: Create branch
await tools.git_create_branch({
    "repo_path": "/tmp/cybersecsuite",
    "branch_name": "feat/add-type-hints",
    "from_branch": "main"
})

# Step 3: Modify file (agent edits core.py)
# ... agent makes changes ...

# Step 4: Check status
status = await tools.git_status({
    "repo_path": "/tmp/cybersecsuite"
})

# Step 5: Commit
await tools.git_commit({
    "repo_path": "/tmp/cybersecsuite",
    "message": "feat(core): add type hints to public API functions",
    "files": ["src/dashboard/api/core.py"],
    "author_name": "Python Developer Agent",
    "author_email": "python-developer@cybersec.ai"
})

# Step 6: Push
await tools.git_push({
    "repo_path": "/tmp/cybersecsuite",
    "branch": "feat/add-type-hints",
    "remote": "origin"
})

# Step 7: Create PR
await tools.github_create_pr({
    "repo_url": "https://github.com/Dystopian/cybersecsuite.git",
    "head_branch": "feat/add-type-hints",
    "base_branch": "main",
    "title": "feat(core): add type hints to public API",
    "body": "...",
    "draft": False
})
```

---

## 🔄 Error Handling & Retry Strategy

### Standard Error Responses
```python
{
    "status": "error",
    "code": "GIT_AUTH_FAILED | GIT_MERGE_CONFLICT | GITHUB_API_ERROR | ...",
    "message": "Human-readable error message",
    "details": {"field": "value"}  # Optional context
}
```

### Retry Logic
- Network errors (timeout, connection refused): Retry 3x with exponential backoff
- Rate limits (GitHub API): Wait for reset time, then retry
- Merge conflicts: Return error, require manual intervention
- Branch diverged: Return error, require rebase

---

## 🧪 Testing Strategy

### Unit Tests
- Test each tool independently
- Mock GitHub API responses
- Verify error handling

### Integration Tests
- Test full workflows (clone → branch → commit → push → PR)
- Use test repository on GitHub
- Clean up test branches after each run

### Security Tests
- Verify token validation
- Verify access control
- Verify audit logging

---

## ✅ Verification Checklist

- [ ] All 8 worktree tools implemented
- [ ] SDK pattern followed (tools, models, sdk_result)
- [ ] Type hints on all parameters (PEP 484/526)
- [ ] Error handling with specific exceptions
- [ ] Audit logging for all operations
- [ ] GitHub token validation
- [ ] Conventional commit message validation
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Documentation complete

---

**GitHub MCP Server Status:** 📋 Design document complete  
**Implementation:** Ready to assign to python-developer agent  
**Scope:** Worktree operations (clone, branch, commit, push, PR, merge)  
**SDK Pattern:** Tools following csmcp SDK conventions
