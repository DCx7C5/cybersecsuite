# GitHub Actions CI/CD Tiered Workflow

This directory contains the three-tier CI/CD pipeline configuration for CyberSecSuite.

## Overview

The CI/CD pipeline is organized into three tiers with increasing thoroughness and time constraints:

| Tier | Trigger | Timeout | Purpose | Audience |
|------|---------|---------|---------|----------|
| **Tier 1** | Pull Request | <12 min | Fast feedback for PRs | Developers |
| **Tier 2** | Merge to main | <25 min | Full validation before merge | QA/Release |
| **Tier 3** | Release tag (v*) | <35 min | Complete release validation | Release Team |

---

## Tier 1: PR Checks (`qa-pr.yml`)

**Trigger:** `pull_request` on branches `main`, `develop`  
**Target Duration:** <12 minutes  
**Goal:** Fast feedback loop for developers

### Jobs

| Job | Duration | Tool | What it checks |
|-----|----------|------|----------------|
| **eslint** | 1 min | ESLint | TypeScript code style, unused imports, syntax errors |
| **ruff-lint** | 1 min | Ruff | Python code style, import sorting, complexity |
| **mypy** | 1 min | mypy | Python type safety and annotations |
| **pytest-unit** | 3 min | pytest | Unit tests (excludes integration tests) |
| **integration-core** | 2 min | pytest | Core MCP integration tests only |
| **playwright-brave-fast** | 2 min | Playwright | E2E tests on Brave only (fast path) |
| **pr-gate** | <1 min | GitHub Actions | Aggregates results; fails if any job fails |

### Success Criteria

- ✅ All TypeScript syntax and style checks pass
- ✅ All Python type hints are valid
- ✅ Unit tests have no failures
- ✅ Core MCP integration tests pass
- ✅ E2E tests pass on Brave browser
- ✅ PR can proceed to review

### Running Locally

```bash
# Run only Tier 1 checks (approximately 12 min total)
npm run lint                    # ESLint (TypeScript)
uv run ruff check src tests    # Ruff (Python)
uv run mypy src                # mypy (type checking)
uv run pytest tests -m "not integration"  # Unit tests
uv run pytest tests -m integration -k "mcp or core"  # Core integration tests
npx playwright test --project=brave  # E2E tests (Brave only)
```

---

## Tier 2: Main Branch Merge (`qa-main.yml`)

**Trigger:** `push` to `main` branch  
**Target Duration:** <25 minutes  
**Goal:** Full validation before merge, ensuring main is always stable

### Jobs

| Job | Duration | Tool | What it checks |
|-----|----------|------|----------------|
| **eslint** | 1 min | ESLint | TypeScript linting |
| **ruff-lint** | 1 min | Ruff | Python linting |
| **mypy** | 1 min | mypy | Python type checking |
| **pytest-unit** | 3 min | pytest | Full unit test suite |
| **integration-core** | 2 min | pytest | Core integration tests |
| **playwright-full** | 5 min | Playwright | E2E tests (Brave + Firefox) |
| **a11y-audit** | 1 min | Axe | Accessibility compliance (WCAG 2A) |
| **performance-check** | 1 min | npm/webpack | Build size validation (<5MB) |
| **coverage** | 2 min | pytest + codecov | Test coverage reporting |
| **main-gate** | <1 min | GitHub Actions | Aggregates results; blocks if any job fails |

### Success Criteria

- ✅ All Tier 1 checks pass
- ✅ E2E tests pass on both Brave and Firefox
- ✅ Accessibility audit completes (warnings non-blocking)
- ✅ Build size is under 5MB
- ✅ Code coverage is tracked (70%+ target)
- ✅ Main branch is stable and deployable

### Running Locally

```bash
# Run Tier 2 checks (approximately 25 min total)
npm run lint                                          # ESLint
uv run ruff check src tests                          # Ruff
uv run mypy src                                       # mypy
uv run pytest tests -m "not integration"             # Unit tests
uv run pytest tests -m integration -k "mcp or core"  # Core integration tests
npx playwright test --project=brave --project=firefox  # E2E (both browsers)
npm install -g @axe-core/cli && npx axe http://localhost:3000  # A11y audit
npm run build && du -sh dist/                        # Build size check
uv run pytest tests -m "not integration" --cov=src --cov-report=html  # Coverage
```

---

## Tier 3: Release Candidate (`qa-release.yml`)

**Trigger:** `push` with tags matching `v*` or `release/*`  
**Target Duration:** <35 minutes  
**Goal:** Complete release validation with manual approval

### Jobs

| Job | Duration | Tool | What it checks |
|-----|----------|------|----------------|
| **eslint** | 1 min | ESLint | TypeScript linting |
| **ruff-lint** | 1 min | Ruff | Python linting |
| **mypy** | 1 min | mypy | Python type checking |
| **pytest-full** | 4 min | pytest | Full test suite (all markers) |
| **playwright-full** | 5 min | Playwright | E2E tests (Brave + Firefox) |
| **a11y-audit** | 1 min | Axe | Accessibility compliance |
| **security-scan** | 2 min | Trivy | Vulnerability scanning (SARIF report) |
| **dependency-audit** | 1 min | pip audit + npm audit | Dependency vulnerabilities |
| **load-test** | 2 min | Apache Bench | Load testing (100 req, 10 concurrent) |
| **coverage** | 2 min | pytest | Final coverage report |
| **build-artifacts** | 2 min | npm/pip | Build release artifacts |
| **approval** | N/A | Manual approval | Requires environment approval (release) |
| **release-gate** | <1 min | GitHub Actions | Final gate; creates GitHub Release |

### Success Criteria

- ✅ All Tier 2 checks pass
- ✅ Full test suite passes (including all integration tests)
- ✅ Security scanning shows no critical vulnerabilities
- ✅ Dependency audit shows no known vulnerabilities
- ✅ Load test completes successfully
- ✅ Manual approval granted by release team
- ✅ Release artifacts built and ready for deployment
- ✅ GitHub Release created with release notes

### Running Locally

```bash
# Run Tier 3 checks (approximately 35 min total)
npm run lint                                  # ESLint
uv run ruff check src tests                  # Ruff
uv run mypy src                               # mypy
uv run pytest tests                           # Full test suite
npx playwright test --project=brave --project=firefox  # E2E (both browsers)
npm install -g @axe-core/cli && npx axe http://localhost:3000  # A11y
uv pip audit                                  # Dependency audit (Python)
npm audit --production                        # Dependency audit (Node)
npm run build && npm run start &              # Start server for load test
sleep 5
sudo apt-get install apache2-utils
ab -n 100 -c 10 http://localhost:3000        # Load test
uv run pytest tests --cov=src --cov-report=term-missing  # Coverage
uv build && npm run build                    # Build artifacts
```

---

## Job Matrix & Reusability

The workflows are structured to minimize duplication:

- **Tier 1** defines base checks (lint, type, unit tests)
- **Tier 2** inherits Tier 1 jobs and adds browser/accessibility/performance checks
- **Tier 3** runs all checks + security scanning and load testing

Each job is independent and can fail without blocking others (except the `*-gate` job).

---

## Failure Troubleshooting

### ESLint Failures
```bash
# Auto-fix linting issues
npm run lint --fix
```

**Common causes:**
- Unused imports
- Inconsistent formatting
- Missing semicolons (if configured)

### Ruff Failures
```bash
# Auto-fix Python style issues
uv run ruff check src tests --fix
```

**Common causes:**
- Import sorting issues
- Line length violations
- Unused imports

### mypy Failures
```bash
# Check type errors in detail
uv run mypy src --show-error-context
```

**Common causes:**
- Missing type annotations
- Type mismatches
- Missing library stubs

### pytest Failures
```bash
# Run specific test with verbose output
uv run pytest tests/test_example.py::test_function -vv
```

**Common causes:**
- Assertion errors
- Missing fixtures
- Service/database connection issues

### Playwright Failures
```bash
# Run tests with debug mode
PWDEBUG=1 npx playwright test --project=brave
```

**Common causes:**
- Timing/race conditions
- Element not found
- Navigation failures

### Load Test Failures
```bash
# Check server is running
curl http://localhost:3000
# Check for slow responses
ab -n 10 -v http://localhost:3000 | grep time
```

**Common causes:**
- Server not started
- Memory leaks
- Slow database queries

---

## Environment Variables

### For All Workflows
```
REDIS_URL=redis://localhost:6379  # Redis connection for tests
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1  # Use system-installed browsers
```

### For Playwright
```
BROWSER=brave   # or firefox, chromium
HEADLESS=true   # Run without UI
DEBUG=pw:api    # Enable debug logs
```

### For Security Scanning
```
TRIVY_SKIP_UPDATE=true  # Skip Trivy DB update
TRIVY_SEVERITY=HIGH,CRITICAL  # Only report critical/high
```

---

## Performance Benchmarks

Target execution times per tier:

### Tier 1 Breakdown
| Job | Target | Actual* |
|-----|--------|---------|
| ESLint | 1 min | ~40 sec |
| Ruff | 1 min | ~30 sec |
| mypy | 1 min | ~45 sec |
| pytest-unit | 3 min | ~2:15 |
| integration-core | 2 min | ~1:45 |
| playwright-brave-fast | 2 min | ~1:30 |
| **Tier 1 Total** | **<12 min** | **~9 min** |

### Tier 2 Additional Jobs
| Job | Target | Actual* |
|-----|--------|---------|
| playwright-full | 5 min | ~4:30 |
| a11y-audit | 1 min | ~45 sec |
| performance-check | 1 min | ~30 sec |
| coverage | 2 min | ~1:45 |
| **Tier 2 Total** | **<25 min** | **~20 min** |

### Tier 3 Additional Jobs
| Job | Target | Actual* |
|-----|--------|---------|
| security-scan | 2 min | ~1:30 |
| dependency-audit | 1 min | ~45 sec |
| load-test | 2 min | ~1:30 |
| build-artifacts | 2 min | ~1:45 |
| approval | N/A | Manual |
| **Tier 3 Total** | **<35 min** | **~30 min** |

*Actual times are estimates and may vary based on system load, dependencies, and cache state.

---

## Browser Support

**Tier 1 & 2:** Brave + Firefox (per user directive)  
**Tier 3:** Brave + Firefox  

No Chromium/Chrome tests are run. Brave is the primary browser for all tiers.

---

## Continuous Integration Strategy

### Pull Request Flow
1. Developer opens PR
2. Tier 1 runs automatically (12 min)
3. Developer reviews results
4. Addresses any failures
5. Once PR is approved by human reviewers, it can be merged

### Main Branch Flow
1. PR merged to main
2. Tier 2 runs automatically (25 min)
3. If Tier 2 fails, main is blocked until fixed
4. Coverage trends are tracked

### Release Flow
1. Tag with `v*` pattern is pushed (e.g., `git tag v1.0.0`)
2. Tier 3 runs automatically (35 min)
3. Release team reviews security/load test reports
4. Manual approval required (GitHub environment)
5. GitHub Release is created automatically

---

## Accessing Results

### GitHub Actions UI
- View workflows: `.github/workflows/` → Click workflow name
- View runs: **Actions** tab → Click run
- View logs: Click job name → Expand step logs

### Artifacts
- Playwright reports: **Artifacts** → `playwright-report`
- Coverage reports: **Artifacts** → `coverage-report`
- Build artifacts (Tier 3): **Artifacts** → `release-artifacts`

### External Services
- **Codecov**: Coverage trends and PR comments
- **GitHub Security**: Trivy SARIF results in **Security** tab
- **GitHub Releases**: Release notes and artifacts

---

## Configuration

### Adjusting Timeouts
Edit `timeout-minutes` in workflow files if needed.

### Adjusting Job Matrix
Add/remove browser projects in `playwright test --project=...` commands.

### Adjusting Coverage Threshold
Edit coverage check in `performance-check` job (default: 5MB limit).

### Adjusting Security Severity
Edit `TRIVY_SEVERITY` environment variable in Trivy step.

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Playwright Documentation](https://playwright.dev)
- [Trivy Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
- [Axe Accessibility Tool](https://www.deque.com/axe/devtools/)

---

**Last Updated:** 2024-04-27  
**Workflow Version:** 1.0  
**Created by:** Phase 11.7: Tiered CI/CD Setup
