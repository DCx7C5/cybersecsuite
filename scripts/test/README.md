# Testing & QA Tools

Benchmarking and performance measurement scripts.

## Scripts

### `benchmark_tiers.py`
Measure and benchmark LLM response times across tiered CI/CD stages.

**Usage:**
```bash
python scripts/test/benchmark_tiers.py [options]
```

**Options:**
- `--tier {1,2,3}` — Test specific CI/CD tier (1=PR, 2=Main, 3=Release)
- `--models <list>` — Comma-separated model names (e.g., gpt-5.2,claude-sonnet)
- `--iterations <n>` — Number of test iterations (default: 5)
- `--output <file>` — Save results to JSON file
- `--compare` — Compare results against baseline
- `--verbose` — Show detailed timing breakdown

**Output:**
- Per-model response times (min, max, avg, stddev)
- Comparison against target SLAs
- JSON report for CI/CD integration
- Performance trends over time

**Example:**
```bash
python scripts/test/benchmark_tiers.py --tier 1 --models gpt-5.2,claude-haiku --output /tmp/tier1-results.json

# Tier 1 (PR) Benchmarks:
# gpt-5.2: avg=245ms (target=500ms) ✓
# claude-haiku: avg=180ms (target=500ms) ✓
```

**Targets by Tier:**
- Tier 1 (PR): < 500ms per model
- Tier 2 (Main): < 400ms per model
- Tier 3 (Release): < 300ms per model

## When to Use

- PR performance validation
- Main branch performance tracking
- Release quality gates
- Performance regression detection
- SLA compliance verification

## Integration

Used in GitHub Actions workflows:
- `.github/workflows/qa-pr.yml` (Tier 1, ~9 min)
- `.github/workflows/qa-main.yml` (Tier 2, ~20 min)
- `.github/workflows/qa-release.yml` (Tier 3, ~30 min)

## See Also

- `scripts/deploy/` — Deployment tools
- `scripts/data/` — Data processing
- `scripts/dev/` — Developer tools
