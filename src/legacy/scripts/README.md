# Scripts Directory

Organized automation tools for CyberSecSuite development, testing, and deployment.

## Organization

Scripts are organized by function in four categories:

```
scripts/
├── dev/                    Developer tools (worktree, aliases)
├── deploy/                 Deployment automation (MCP bootstrap)
├── test/                   Testing & QA (benchmarking)
└── data/                   Data processing (skill validation)

dev/hooks/                  Git hooks (pre-commit, post-merge, etc.)
```

## Quick Start

### Installation

**Deploy MCPs:**
```bash
bash scripts/deploy/install-mcp-core.sh
```

**Verify Installation:**
```bash
bash scripts/deploy/install-mcp-core.sh --verify
```

**Enable Developer Tools:**
```bash
source scripts/dev/gwt-aliases.sh
```

**Benchmark Performance:**
```bash
python scripts/test/benchmark_tiers.py --tier 1
```

**Validate Skills Data:**
```bash
python scripts/data/fix_skills.py --dir templates/skills/ --validate
```

## By Category

### [Developer Tools](dev/README.md) — `scripts/dev/`
- `worktree-session-manager.py` — Git worktree sessions
- `gwt-aliases.sh` — Git worktree shell aliases

**Use Case:** Multi-branch development, interactive debugging

### [Deployment](deploy/README.md) — `scripts/deploy/`
- `install-mcp-core.sh` — MCP bootstrap and installation

**Use Case:** Fresh setup, infrastructure verification, production deployment

### [Testing & QA](test/README.md) — `scripts/test/`
- `benchmark_tiers.py` — LLM performance benchmarking

**Use Case:** Performance validation, SLA verification, CI/CD gating

### [Data Processing](data/README.md) — `scripts/data/`
- `fix_skills.py` — Skill file validation and normalization

**Use Case:** Data quality, bulk migrations, consistency checks

### [Git Hooks](../dev/hooks/README.md) — `dev/hooks/`
- `pre-commit.tpl` — Code quality checks before commit
- `pre-push.tpl` — Tests before push
- `post-merge.tpl` — Workflow after merge
- `commit-msg.tpl` — Commit message validation
- `post-checkout.tpl` — Branch change workflows

**Use Case:** Automated quality gates, workflow automation

## Configuration Files

- `pyproject.toml` — Python tool configuration (pytest, ruff, mypy)
- `.pre-commit-config.yaml` — Pre-commit hook rules
- `Makefile` — Common development commands
- `.git/config` — Git configuration

## Usage Examples

**Multi-branch feature development:**
```bash
source scripts/dev/gwt-aliases.sh
gwt-create feature/new-api
```

**Fresh deployment:**
```bash
bash scripts/deploy/install-mcp-core.sh --verify
```

**Performance testing:**
```bash
python scripts/test/benchmark_tiers.py --tier 2 --output results.json
```

**Data validation:**
```bash
python scripts/data/fix_skills.py --dir templates/skills/ --fix --report report.json
```

## Execution Paths

All scripts can be executed from the repository root:

```bash
bash scripts/deploy/install-mcp-core.sh    # From any directory
python scripts/test/benchmark_tiers.py     # From any directory
source scripts/dev/gwt-aliases.sh          # From any directory
```

Or relative to current location:

```bash
cd scripts/deploy && bash install-mcp-core.sh
cd scripts/test && python benchmark_tiers.py
```

## Maintenance

See individual category READMEs for:
- Detailed usage documentation
- All available options
- Integration points
- When to use each tool

## See Also

- [Makefile](../Makefile) — Common commands
- [pyproject.toml](../pyproject.toml) — Tool configuration
- [.pre-commit-config.yaml](../.pre-commit-config.yaml) — Hook setup
