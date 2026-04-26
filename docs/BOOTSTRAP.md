# CyberSecSuite Bootstrap Installation Guide

This guide explains how to bootstrap CyberSecSuite with all 7 core MCPs and configure SDK mode.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Automated Installation](#automated-installation)
4. [SDK Mode Configuration](#sdk-mode-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Performance Tuning](#performance-tuning)

## Quick Start

The fastest way to get CyberSecSuite with all MCPs installed:

```bash
# 1. Run the bootstrap installer
bash scripts/install-mcp-core.sh

# 2. Verify installation
bash scripts/install-mcp-core.sh --verify-only

# 3. Start CyberSecSuite with external MCPs
export SDK_MODE=hybrid
docker compose up -d
sleep 10
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "mcps_loaded": 7,
  "mode": "hybrid",
  "version": "0.1.0"
}
```

## Prerequisites

### System Requirements

- **OS:** Linux (Ubuntu 20.04+, Debian 12+) or macOS
- **Python:** 3.11 or higher
- **uv:** Latest version (recommended package manager)
- **Disk Space:** Minimum 2GB for all MCPs
- **RAM:** Minimum 4GB available

### Verify Prerequisites

```bash
# Check Python version
python3 --version  # Must be 3.11+

# Check uv installation
uv --version  # Must be available

# Check disk space
df -h /home/daen  # Ensure 2GB+ available
```

### Installation Commands

If prerequisites missing:

```bash
# Install Python 3.11+ (Ubuntu/Debian)
sudo apt update && sudo apt install python3.11 python3.11-venv

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env  # Reload shell

# Verify installation
uv --version && python3 --version
```

## Automated Installation

### Overview

The `install-mcp-core.sh` script automates installation of 7 MCPs:

1. **csscore-mcp** — Core database and case management
2. **canvas-mcp** — Forensic visualization and attack graphs
3. **memory-mcp** — Vector memory storage for AI
4. **template-mcp** — Template rendering engine
5. **playwright-mcp** — Browser automation
6. **dystopian-crypto-mcp** — Cryptographic operations
7. **custom-mcp** — External MCP bridge and SDK adapter

### Installation Steps

```bash
# Navigate to CyberSecSuite root
cd /home/daen/Projects/cybersecsuite

# Run installer with progress display
bash scripts/install-mcp-core.sh

# Or run in verbose mode for debugging
bash scripts/install-mcp-core.sh --verbose

# Or run in offline mode (uses local sources only)
bash scripts/install-mcp-core.sh --offline
```

### Installation Modes

#### Standard Mode (Default)
```bash
bash scripts/install-mcp-core.sh
```
- Tries local sources first (from `/home/daen/Projects/ai-marketplace`)
- Falls back to PyPI if local not found
- Completes in <120 seconds
- Shows progress for each MCP

#### Offline Mode
```bash
bash scripts/install-mcp-core.sh --offline
```
- Uses only local sources
- Fails if any local source unavailable
- Useful for networks without internet access

#### Verbose Mode
```bash
bash scripts/install-mcp-core.sh --verbose
```
- Shows full output from pip/uv
- Logs to `/tmp/mcp_install.log`
- Useful for debugging installation failures

#### Verification Only
```bash
bash scripts/install-mcp-core.sh --verify-only
```
- Checks if MCPs are already installed
- Does not attempt installation
- Useful for CI/CD pipelines

### Installation Output

Successful installation shows:

```
[ℹ] 2026-04-27 14:30:00 ═══════════════════════════════════════════════════════════
[ℹ] 2026-04-27 14:30:00 CyberSecSuite MCP Core Bootstrap Installer v1.0
[ℹ] 2026-04-27 14:30:00 ═══════════════════════════════════════════════════════════
[ℹ] 2026-04-27 14:30:01 Running preflight checks...
[ℹ] 2026-04-27 14:30:01 Found uv 0.1.25
[✓] 2026-04-27 14:30:01 Python 3.11.2 ✓
[ℹ] 2026-04-27 14:30:02 Preflight checks complete (timeout: 120s)
[ℹ] 2026-04-27 14:30:02 ═══════════════════════════════════════════════════════════
[ℹ] 2026-04-27 14:30:02 Installation Phase
[ℹ] 2026-04-27 14:30:02 ═══════════════════════════════════════════════════════════
[ℹ] 2026-04-27 14:30:03 Installing csscore-mcp from source: /home/daen/Projects/ai-marketplace/mcps/csscore-mcp
[✓] 2026-04-27 14:30:15 Installed: csscore-mcp
[BLUE]14%[NC] 1/7 MCPs installed
... (more installations)
[✓] 2026-04-27 14:31:28 ═══════════════════════════════════════════════════════════
[✓] 2026-04-27 14:31:28 Bootstrap installation successful! All MCPs ready.
[✓] 2026-04-27 14:31:28 ═══════════════════════════════════════════════════════════
```

## SDK Mode Configuration

CyberSecSuite SDK Mode enables loading externalized MCPs as isolated services while maintaining local fallbacks.

### SDK Mode Options

#### 1. Hybrid Mode (Recommended)

```bash
export SDK_MODE=hybrid
export EXTERNAL_MCPS_ENABLED=true

# Start CyberSecSuite
docker compose up -d
```

**Behavior:**
- Loads built-in cybersec MCP (local)
- Loads all external MCPs (isolated)
- Graceful fallback if external MCP unavailable
- Best for production deployments

**Configuration:**
```python
# In your application
from csmcp import all_servers, allowed_tools, get_sdk_mode

mode = get_sdk_mode()  # Returns "hybrid"
servers = all_servers()  # Returns: {"cybersec": ..., "csscore_mcp": ..., ...}
tools = allowed_tools()  # Returns all available tools
```

#### 2. Local Mode

```bash
export SDK_MODE=local
export EXTERNAL_MCPS_ENABLED=false

# Start CyberSecSuite
docker compose up -d
```

**Behavior:**
- Uses only built-in cybersec MCP
- Ignores external MCPs
- Highest performance, lowest overhead
- Best for isolated deployments

#### 3. External Mode

```bash
export SDK_MODE=external
export EXTERNAL_MCPS_ENABLED=true

# Start CyberSecSuite
docker compose up -d
```

**Behavior:**
- Loads only external MCPs
- Fails if external MCPs unavailable
- Best for testing external MCP stability

### Configuration via Environment

Add to `.env` or `docker-compose.yml`:

```yaml
# docker-compose.yml
environment:
  SDK_MODE: hybrid
  EXTERNAL_MCPS_ENABLED: "true"
```

Or in `.env`:

```bash
# .env
SDK_MODE=hybrid
EXTERNAL_MCPS_ENABLED=true
```

### Programmatic Configuration

```python
from csmcp import (
    all_servers,
    allowed_tools,
    get_sdk_mode,
    get_external_mcps_status,
    load_external_mcps,
)

# Get current configuration
mode = get_sdk_mode()  # Returns SDK_MODE from environment
status = get_external_mcps_status()  # Check which MCPs loaded

# Load MCPs manually
external = load_external_mcps()
print(f"Loaded MCPs: {list(external.keys())}")

# Get all servers for Agent SDK
servers = all_servers()
tools = allowed_tools()

options = ClaudeAgentOptions(
    mcp_servers=servers,
    allowed_tools=tools
)
```

## Verification

### Quick Health Check

```bash
# Check CyberSecSuite health endpoint
curl http://localhost:8000/health

# Expected output:
{
  "status": "healthy",
  "version": "0.1.0",
  "mcps_loaded": 7,
  "mode": "hybrid",
  "timestamp": "2026-04-27T14:35:00Z"
}
```

### Verify Each MCP

```bash
# Check if MCP modules are installed
python3 -c "import csscore_mcp; print('✓ csscore_mcp')"
python3 -c "import canvas_mcp; print('✓ canvas_mcp')"
python3 -c "import memory_mcp; print('✓ memory_mcp')"
python3 -c "import template_mcp; print('✓ template_mcp')"
python3 -c "import playwright_mcp; print('✓ playwright_mcp')"
python3 -c "import dystopian_crypto_mcp; print('✓ dystopian_crypto_mcp')"
python3 -c "import custom_mcp; print('✓ custom_mcp')"
```

### Run Integration Tests

```bash
cd /home/daen/Projects/cybersecsuite

# Run bootstrap integration tests
uv run pytest tests/integration/test_mcp_bootstrap.py -v

# Run with coverage report
uv run pytest tests/integration/test_mcp_bootstrap.py -v --cov=src --cov-report=term-missing
```

### View Bootstrap Report

After installation, check the report:

```bash
cat /tmp/mcp_bootstrap_report.txt

# Example output:
# MCP Bootstrap Installation Report
# Generated: 2026-04-27T14:35:00Z
# Marketplace: /home/daen/Projects/ai-marketplace
# CyberSecSuite: /home/daen/Projects/cybersecsuite
#
# Installation Results:
#   Installed: 7 / 7
#   Verified: 7 / 7
#   Duration: 85s
#
# MCPs:
#   ✓ csscore-mcp
#   ✓ canvas-mcp
#   ✓ memory-mcp
#   ✓ template-mcp
#   ✓ playwright-mcp
#   ✓ dystopian-crypto-mcp
#   ✓ custom-mcp
```

## Troubleshooting

### Issue: "uv not found"

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Verify
uv --version
```

### Issue: "Python 3.11+ required"

**Solution:**
```bash
# Check Python version
python3 --version

# If too old, install newer version
sudo apt update
sudo apt install python3.11 python3.11-venv

# Create venv with newer Python
python3.11 -m venv venv
source venv/bin/activate
```

### Issue: Installation timeout (>120s)

**Causes:**
- Slow internet connection
- Network issues
- Large package downloads

**Solutions:**
```bash
# 1. Run offline mode (uses local sources)
bash scripts/install-mcp-core.sh --offline

# 2. Run verbose to diagnose
bash scripts/install-mcp-core.sh --verbose

# 3. Check network
ping 8.8.8.8
curl -I https://pypi.org

# 4. Manually install problematic MCP
cd /home/daen/Projects/ai-marketplace/mcps/csscore-mcp
uv pip install -e .
```

### Issue: "ModuleNotFoundError: No module named 'csscore_mcp'"

**Solution:**
```bash
# Reinstall the specific MCP
cd /home/daen/Projects/ai-marketplace/mcps/csscore-mcp
uv pip install -e .

# Verify installation
python3 -c "import csscore_mcp; print(csscore_mcp.__version__)"
```

### Issue: External MCPs not loading in hybrid mode

**Diagnosis:**
```bash
# Check SDK mode
python3 -c "from csmcp import get_sdk_mode; print(get_sdk_mode())"

# Check external MCP status
python3 -c "from csmcp import get_external_mcps_status; import json; print(json.dumps(get_external_mcps_status(), indent=2))"

# Check environment
echo $SDK_MODE
echo $EXTERNAL_MCPS_ENABLED
```

**Solution:**
```bash
# Ensure MCPs are installed
bash scripts/install-mcp-core.sh --verify-only

# Check for import errors
python3 -c "import csscore_mcp; print('✓')" || echo "Import failed"

# Restart CyberSecSuite
docker compose restart cybersecsuite
```

## Advanced Configuration

### Custom MCP Locations

If MCPs installed in non-standard location:

```bash
# Set PYTHONPATH to include custom location
export PYTHONPATH="/custom/mcp/path:$PYTHONPATH"

# Start CyberSecSuite
docker compose up -d
```

### MCP Resource Limits

Control resource usage per MCP:

```yaml
# docker-compose.yml
services:
  csscore-mcp:
    cpus: "0.5"
    mem_limit: 512m

  canvas-mcp:
    cpus: "0.3"
    mem_limit: 256m
```

### Logging Configuration

Enable detailed logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG
export SDK_MODE_DEBUG=true

# Start CyberSecSuite
docker compose up -d

# View logs
docker compose logs -f cybersecsuite
```

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed MCP status
curl http://localhost:8000/api/v1/mcps/status

# Tool inventory
curl http://localhost:8000/api/v1/tools/list
```

## Performance Tuning

### Optimize Installation Speed

```bash
# Use parallel installation (uv default)
export UV_PYTHON_DOWNLOADS=never
bash scripts/install-mcp-core.sh

# Install specific MCPs only
cd /home/daen/Projects/ai-marketplace/mcps/csscore-mcp
uv pip install -e .
```

### Optimize Runtime Performance

```bash
# Use uvloop for faster async
export PYTHONOPTIMIZE=2
export USE_UVLOOP=1

# Start CyberSecSuite
docker compose up -d
```

### Monitor Performance

```bash
# Check MCP load times
docker compose logs | grep "loaded in"

# Monitor resource usage
docker compose exec cybersecsuite \
  python3 -c "import psutil; print(psutil.Process().memory_info())"
```

## Maintenance

### Updating MCPs

```bash
# Update all MCPs to latest version
cd /home/daen/Projects/ai-marketplace

for mcp in csscore-mcp canvas-mcp memory-mcp template-mcp playwright-mcp dystopian-crypto-mcp; do
  cd mcps/$mcp
  uv pip install --upgrade -e .
  cd /home/daen/Projects/ai-marketplace
done
```

### Uninstalling MCPs

```bash
# Uninstall individual MCP
uv pip uninstall csscore-mcp

# Uninstall all MCPs
uv pip uninstall csscore-mcp canvas-mcp memory-mcp template-mcp playwright-mcp dystopian-crypto-mcp custom-mcp
```

### Checking Installed Versions

```bash
# Check all MCP versions
uv pip show csscore-mcp | grep Version
uv pip show canvas-mcp | grep Version
uv pip show memory-mcp | grep Version
uv pip show template-mcp | grep Version
uv pip show playwright-mcp | grep Version
uv pip show dystopian-crypto-mcp | grep Version
uv pip show custom-mcp | grep Version
```

## Next Steps

1. **Configure API Access** — Set up API keys and rate limiting
2. **Enable SSL/TLS** — Configure HTTPS for production
3. **Set Up Monitoring** — Enable OpenTelemetry and observability
4. **Configure Logging** — Set up centralized log aggregation
5. **Run Integration Tests** — Verify end-to-end functionality

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review MCP-specific documentation in `/home/daen/Projects/ai-marketplace/mcps/<mcp-name>`
3. Check logs: `docker compose logs -f cybersecsuite`
4. View bootstrap report: `cat /tmp/mcp_bootstrap_report.txt`

---

**Version:** 1.0  
**Last Updated:** 2026-04-27  
**Marketplace:** https://ai-marketplace.cybersecsuite.local
