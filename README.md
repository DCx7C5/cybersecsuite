# CyberSecSuite v0.1

A production-grade cybersecurity forensics suite with A2A agent orchestration, MCP server support, threat intelligence, and artifact signing capabilities.

**Status:** ✅ Phase 11 Complete (920+ tests, 95.3% passing) | 🚀 Phase 12 Planning Ready

---

## 🎯 Core Features

- **Forensic Analysis Framework** — 6 MCPs with 85 tools, unified interface
- **Multi-Provider AI Routing** — 13 strategies, cost optimization, provider fallback
- **Quality of Life (QoL) Controls** — 8 toggles + 5 presets for cost/compliance
- **Cryptographic Security** — Ed25519 signing, BLAKE2b hashing, Argon2id key derivation
- **A2A Agent Networking** — Agent-to-agent communication protocol
- **Marketplace Integration** — 1,064 skills + 38 agents (see `ai-marketplace`)

---

## 📦 Infrastructure Status

| Component | Status | Details |
|-----------|--------|---------|
| **Core MCPs** | ✅ 6/6 | csscore, canvas, memory, template, playwright, crypto |
| **Marketplace** | ✅ Production | 1,064 skills + 38 agents in separate repository |
| **Testing** | ✅ 920+ tests | 95.3% pass rate, Brave+Firefox browsers |
| **Documentation** | ✅ Complete | Setup guide in `docs/setup.md`, design docs in `docs/` |
| **Bootstrap** | ✅ <3.7s | Automated 6 MCP setup |

---

## 📋 Phase Status

- ✅ **Phases 0.5-11** — Complete (7,920 lines of code, 6 MCPs consolidated)
- 🚀 **Phase 12 Ready** — "Redundant File Cleanup" specification complete
- 📖 **[Documentation Hub](docs/)** — Complete API reference, architecture, setup guide

---

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** — Step-by-step setup walkthrough, env vars, troubleshooting
- **[Setup Guide](docs/setup.md)** — Step-by-step setup walkthrough, env vars, troubleshooting
- **[Documentation Hub](docs/)** — Complete API reference, architecture diagrams
- **[Architecture Overview](docs/architecture/architecture-overview.md)** — System design
- **[Full Docs](docs/README.md)** — Complete API reference, deployment guide
- **[QoL Guide](docs/features/qol.md)** — Output controls: toggles, presets, use cases

---

## 🚀 Installation

### Quick Start

```bash
# Clone and sync dependencies
git clone https://github.com/DCx7C5/cybersecsuite.git
cd cybersecsuite
uv sync

# Bootstrap MCPs (< 4 seconds)
uv run python scripts/dev/worktree-session-manager.py
```

### Development Setup

```bash
uv sync --group dev
```

### Get Skills & Agents

```bash
git clone https://github.com/DCx7C5/ai-marketplace.git ~/.ai-marketplace
cp -r ~/.ai-marketplace/agents/* .claude/agents/
cp -r ~/.ai-marketplace/skills/* .claude/skills/
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src

# Run specific suite (unit, integration, a11y, etc.)
uv run pytest tests/unit/
uv run pytest tests/integration/
```

### Test Coverage

- Unit: ✅ Passing
- Integration: ✅ Passing
- A11y (Brave+Firefox): ✅ 71% WCAG 2.1 AA (upgrading in Phase 12)
- Performance: ✅ Baseline established
- CI/CD: ✅ 3-tier pipeline (PR/main/release)

---

## 🏗️ Architecture

**7-Layer System Design:**
1. API Layer (FastAPI endpoints)
2. Routing Layer (13 strategies, provider selection)
3. Orchestration Layer (A2A protocol)
4. MCP Layer (6 model context protocols)
5. Business Logic (forensics, threat intel, signing)
6. Data Layer (SQLite, vector memory)
7. Storage Layer (artifacts, configurations)

See [`docs/architecture/overview.md`](docs/architecture/overview.md) for detailed architecture.

---

## 📂 Project Structure

```
cybersecsuite/
├── docs/                       # Complete documentation (setup, architecture, API reference)
│   ├── README.md              # Navigation hub
│   ├── plan.md                # Detailed phase specs
│   ├── ORCHESTRATOR_QUICK_REFERENCE.md
│   ├── PHASE_12_REDUNDANT_CLEANUP.md
│   └── DECISIONS.md           # Architectural decisions
├── src/
│   ├── backend/               # FastAPI application
│   ├── frontend/              # React dashboard
│   ├── agent/                 # A2A agent networking
│   └── forensics/             # Forensic analysis modules
├── scripts/                   # Category-based scripts
│   ├── dev/                   # Development tools
│   ├── deploy/                # Deployment automation
│   ├── test/                  # Testing utilities
│   └── data/                  # Data processing
├── config/                    # MCP configuration
├── docs/                      # Complete documentation
├── tests/                     # Comprehensive test suite
└── pyproject.toml            # UV dependency management
```

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

---

## 📄 License

Proprietary - CyberSecSuite
