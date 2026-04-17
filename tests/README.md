# CyberSecSuite Test Suite

Comprehensive test coverage for finished features.

## Test Files

| Module               | File                       | Tests | Coverage                                      |
|----------------------|----------------------------|-------|-----------------------------------------------|
| **Crypto**           | `test_crypto.py`           | 11    | Ed25519, Argon2id, AES-256-GCM                |
| **MCP Server**       | `test_mcp_server.py`       | 8     | Tool registry, cybersec + dystopian           |
| **Agent SDK**        | `test_agent_sdk.py`        | 12    | AgentRunner, SessionManager, hooks            |
| **AI Proxy**         | `test_ai_proxy.py`         | 13    | Routing, combo strategies, rate limiting      |
| **A2A Protocol**     | `test_a2a.py`              | 15    | Task orchestration, agent registry            |
| **Integrity Checks** | `test_integrity_checks.py` | 9     | Model FK, fixture coverage, config validation |
| **Telemetry**        | `test_telemetry.py`        | 10    | Metrics store, middleware, aggregation        |
| **PoC Model**        | `test_poc_model.py`        | 21    | ProofOfConcept model, seeding                 |

**Total: 67 tests**

## Running Tests

### All tests
```bash
uv run pytest tests/ -v
```

### By marker
```bash
uv run pytest tests/ -m crypto       # Crypto tests only
uv run pytest tests/ -m asyncio      # Async tests only
uv run pytest tests/ -m integration  # Integration tests
```

### Single file
```bash
uv run pytest tests/test_integrity_checks.py -v
```

### With coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

## Test Structure

Each test module follows the pattern:
1. **Fixtures** — Setup/teardown (temp dirs, configs, mocks)
2. **Unit Tests** — Core functionality of each module
3. **Integration Tests** — Cross-module interactions (marked with `@pytest.mark.integration`)
4. **Async Tests** — Async functions (auto-detected by pytest-asyncio)

## Skipped Tests

Tests for incomplete modules are marked with `@pytest.mark.skip`:
- `test_crypto.py` — Awaiting crypto implementation finalization
- `test_mcp_server.py` — Sub-module tool imports not yet finalized
- `test_ai_proxy.py` — Provider registry API in progress
- `test_agent_sdk.py` — Agent model classes not yet available

These can be run once the modules are complete.

## Fixtures

### Session-scoped
- `event_loop` — Async event loop for all tests

### Function-scoped
- `temp_key_dir` — Temporary key storage
- `temp_vault_dir` — Temporary vault storage
- `temp_config_dir` — Temporary config directory
- `temp_data_dir` — Temporary data directory
- `project_root` — Project root path
- `test_env` — Test environment variables
- `runner` — AgentRunner instance
- `session_manager` — SessionManager instance
- `store` — TaskStore instance
- `registry` — AgentRegistry instance
- `limiter` — RateLimiter instance
- `tracker` — UsageTracker instance

## CI/CD Integration

Tests run automatically on:
- PR creation/update
- Pre-commit hook (local)
- GitHub Actions (CI pipeline)

Minimum passing rate: **100%** (no failures in CI)

Coverage gates (when enabled):
- Statements: 85%
- Lines: 80%
- Functions: 85%
- Branches: 100%

