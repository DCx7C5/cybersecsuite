# Tool Discovery Mechanism Design

## Problem Statement

### Current State
CyberSecSuite's `tool_seeds.py` currently imports tools from two internal MCPs:
- `csmcp.cybersec` (forensic tools)
- `csmcp.dystopian` (purple-team tools)

These are tightly coupled to the main codebase and deployed together.

### Future State
CyberSecSuite will depend on 12 independent external MCPs, deployed separately:
- forensic-mcp
- purple-team-mcp
- encoding-specialist-mcp
- (9 more specialized MCPs)

### The Gap
**The Problem:** `tool_seeds.py` has no mechanism to discover and load tools from external MCPs. Currently it directly imports from known packages. With 12 independent MCPs:
- MCPs may be installed in different environments
- MCPs may be installed in different order
- MCPs may be optionally installed (some users only want forensic tools)
- MCP versions evolve independently
- Discovery must handle missing MCPs gracefully

**Impact if not solved:** CyberSecSuite will be hardcoded to specific MCP implementations, defeating the purpose of externalization. Adding new MCPs requires code changes to CyberSecSuite.

---

## Solution Options

### Option 1: Manifest-Based Discovery

**Concept:** Each MCP provides a `tools.json` file describing its tools. CyberSecSuite reads these manifests to discover available tools.

**Advantages:**
- ✅ Simple, language-agnostic
- ✅ Tools discoverable without loading code
- ✅ Zero runtime cost if tools not used
- ✅ Can validate tool schemas without executing code
- ✅ Works offline (if manifests cached)

**Disadvantages:**
- ❌ Manifest must stay in sync with actual tools
- ❌ Requires manual maintenance when tools change
- ❌ Duplicates tool metadata (also in code)

**Example File Structure:**

```json
{
  "mcp_name": "forensic-mcp",
  "mcp_version": "0.1.0",
  "tools": [
    {
      "name": "analyze_artifact",
      "description": "Analyze forensic artifacts from disk",
      "input_schema": {
        "type": "object",
        "properties": {
          "artifact_path": {"type": "string"},
          "artifact_type": {"type": "string"}
        },
        "required": ["artifact_path"]
      }
    },
    {
      "name": "extract_iocs",
      "description": "Extract IOCs from analysis results",
      "input_schema": {
        "type": "object",
        "properties": {
          "analysis_result": {"type": "object"}
        },
        "required": ["analysis_result"]
      }
    }
  ]
}
```

**CyberSecSuite Integration (Manifest-based):**

```python
# tool_seeds.py - manifest discovery
import json
import os
from pathlib import Path

def discover_tools_from_manifests(search_paths: list[str]) -> dict:
    """
    Discover tools from tools.json manifests in search_paths.
    Returns: {"mcp_name": [tool_definitions]}
    """
    discovered_tools = {}
    
    for search_path in search_paths:
        path = Path(search_path)
        if not path.exists():
            continue
            
        for tools_json in path.glob("*/tools.json"):
            try:
                with open(tools_json) as f:
                    manifest = json.load(f)
                    mcp_name = manifest.get("mcp_name")
                    tools = manifest.get("tools", [])
                    discovered_tools[mcp_name] = tools
                    logger.info(f"Discovered {len(tools)} tools from {mcp_name}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse {tools_json}: {e}")
                
    return discovered_tools
```

---

### Option 2: Dynamic Import Discovery

**Concept:** Each MCP exports a `get_tools()` function that returns its tool definitions at runtime. CyberSecSuite dynamically imports and calls this function.

**Advantages:**
- ✅ Single source of truth (code defines tools)
- ✅ Automatic sync (no manifest to maintain)
- ✅ Can include dynamic tool generation
- ✅ Tools can have runtime dependencies
- ✅ Can validate before registration

**Disadvantages:**
- ❌ Must load MCP code (slower discovery)
- ❌ Requires all dependencies installed
- ❌ Must handle import errors gracefully
- ❌ Runtime cost even if tools not used

**Example Function Signature:**

```python
# In each MCP (e.g., forensic_mcp/__init__.py)
from typing import list
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict

def get_tools() -> list[ToolDefinition]:
    """Return list of tools provided by this MCP."""
    return [
        ToolDefinition(
            name="analyze_artifact",
            description="Analyze forensic artifacts from disk",
            input_schema={
                "type": "object",
                "properties": {
                    "artifact_path": {"type": "string"},
                    "artifact_type": {"type": "string"}
                },
                "required": ["artifact_path"]
            }
        ),
        ToolDefinition(
            name="extract_iocs",
            description="Extract IOCs from analysis results",
            input_schema={
                "type": "object",
                "properties": {
                    "analysis_result": {"type": "object"}
                },
                "required": ["analysis_result"]
            }
        ),
    ]
```

**CyberSecSuite Integration (Dynamic import):**

```python
# tool_seeds.py - dynamic discovery
import importlib
from typing import Protocol

class ToolProvider(Protocol):
    def get_tools(self) -> list:
        """Get tools provided by MCP."""
        ...

MCP_PACKAGES = [
    "forensic_mcp",
    "purple_team_mcp",
    "encoding_specialist_mcp",
    # ... 9 more
]

def discover_tools_dynamically() -> dict:
    """
    Discover tools by dynamically importing MCPs and calling get_tools().
    Returns: {"mcp_name": [tool_definitions]}
    """
    discovered_tools = {}
    
    for package_name in MCP_PACKAGES:
        try:
            module = importlib.import_module(package_name)
            if hasattr(module, "get_tools"):
                tools = module.get_tools()
                discovered_tools[package_name] = tools
                logger.info(f"Discovered {len(tools)} tools from {package_name}")
            else:
                logger.warning(f"{package_name} has no get_tools() function")
        except ImportError as e:
            logger.warning(f"MCP {package_name} not installed: {e}")
        except Exception as e:
            logger.error(f"Failed to discover tools from {package_name}: {e}")
            
    return discovered_tools
```

---

## Decision: Implement Both (Phased Approach)

**Why both?** Each option solves different problems:

- **Manifest-based** works in constrained environments (air-gapped, validation, CI/CD checks)
- **Dynamic import** stays synchronized automatically (no maintenance burden)

**Phased Implementation:**

| Phase | Step | Rationale |
|-------|------|-----------|
| 1 (Now) | Add `tools.json` manifest to all 12 MCPs | Defines contract, enables validation, creates baseline for CI/CD |
| 1 | Implement manifest discovery in CyberSecSuite | Works immediately with Phase 1 releases |
| 6 | Add `get_tools()` to all 12 MCPs | Reduces maintenance burden, full automation |
| 6 | Implement dynamic discovery in CyberSecSuite | Fallback to manifest if dynamic fails |

**CyberSecSuite Pseudocode (Full Hybrid Approach):**

```python
def discover_all_tools(dev_mode=False) -> dict:
    """
    Discover tools with automatic fallback:
    1. Try dynamic import (Phase 6+)
    2. Fall back to manifests (Phase 1+)
    """
    tools = {}
    
    if dev_mode:
        # Development: load from ../ai-marketplace/mcps/
        search_paths = [
            "../ai-marketplace/mcps",
        ]
    else:
        # Production: load from ~/.cybersecsuite/INSTALLED.json
        installed = load_installed_mcps()
        search_paths = [mcp["path"] for mcp in installed]
    
    # Try dynamic import first (Phase 6+)
    try:
        tools = discover_tools_dynamically()
        if tools:
            logger.info(f"Discovered {sum(len(t) for t in tools.values())} tools via dynamic import")
            return tools
    except Exception as e:
        logger.debug(f"Dynamic discovery failed: {e}, falling back to manifests")
    
    # Fall back to manifest-based discovery
    try:
        tools = discover_tools_from_manifests(search_paths)
        if tools:
            logger.info(f"Discovered {sum(len(t) for t in tools.values())} tools via manifests")
            return tools
    except Exception as e:
        logger.error(f"Manifest discovery failed: {e}")
    
    # Both failed
    logger.critical("Tool discovery failed - no MCPs available")
    raise RuntimeError("No MCP tools discovered")

def load_installed_mcps() -> list[dict]:
    """
    Load list of installed MCPs from ~/.cybersecsuite/INSTALLED.json
    Format:
    [
      {"name": "forensic-mcp", "path": "/usr/local/lib/forensic-mcp", "version": "0.1.0"},
      ...
    ]
    """
    installed_file = Path.home() / ".cybersecsuite" / "INSTALLED.json"
    if not installed_file.exists():
        return []
    
    with open(installed_file) as f:
        return json.load(f)
```

---

## Implementation Details

### Development Mode
```python
# .env or config
MCP_DISCOVERY_MODE=development
MCP_DISCOVERY_PATHS=../ai-marketplace/mcps/forensic-mcp:../ai-marketplace/mcps/purple-team-mcp

# tool_seeds.py
if os.getenv("MCP_DISCOVERY_MODE") == "development":
    paths = os.getenv("MCP_DISCOVERY_PATHS").split(":")
    tools = discover_tools_from_manifests(paths)
```

### Production Mode
```python
# User installs MCPs via package manager
# $ pip install forensic-mcp purple-team-mcp ...

# CyberSecSuite reads ~/.cybersecsuite/INSTALLED.json
# Maintained by install/uninstall scripts

# tool_seeds.py
installed = load_installed_mcps()
mcp_paths = [mcp["path"] for mcp in installed]
tools = discover_tools_from_manifests(mcp_paths)
```

### Error Handling Strategies

| Error                | Handling         | Recovery                             |
|----------------------|------------------|--------------------------------------|
| MCP not installed    | Log warning      | Continue with remaining MCPs         |
| Invalid `tools.json` | Log error        | Skip MCP, continue                   |
| MCP import fails     | Log error        | Skip MCP, continue                   |
| No MCPs discovered   | Log critical     | Raise RuntimeError (system unusable) |
| Tool name collision  | Namespace by MCP | `{mcp_name}::{tool_name}`            |

---

## Validation Strategy

### Tool Count Verification
```python
def validate_tool_discovery():
    """Verify discovered tools == source tools."""
    
    # Read expected tool counts from each MCP's pyproject.toml or manifest
    expected = load_expected_tool_counts()
    
    discovered = discover_all_tools()
    actual = {name: len(tools) for name, tools in discovered.items()}
    
    for mcp_name, expected_count in expected.items():
        actual_count = actual.get(mcp_name, 0)
        if actual_count != expected_count:
            raise AssertionError(
                f"{mcp_name}: expected {expected_count} tools, got {actual_count}"
            )
    
    logger.info("Tool discovery validation passed")
```

### CI/CD Checks
```yaml
# .github/workflows/test-discovery.yml
- name: Validate Tool Discovery
  run: |
    python -m pytest tests/test_tool_discovery.py -v
    
- name: Check Tool Schema
  run: |
    python scripts/validate_tool_schemas.py
    # Ensures all tools.json files match JSON schema
    
- name: Verify Tool Counts
  run: |
    python -m cybersecsuite.tool_discovery validate
```

### Fallback Strategy
```python
def get_tools_with_fallback(tool_name: str) -> Tool:
    """
    Get tool with multiple lookup strategies:
    1. Exact match
    2. Namespaced match (mcp::tool)
    3. Best guess (if only one MCP provides similar tool)
    """
    # Try exact match first
    if tool_name in ALL_TOOLS:
        return ALL_TOOLS[tool_name]
    
    # Try namespaced lookup
    for mcp_name, tools in discovered_tools.items():
        namespaced = f"{mcp_name}::{tool_name}"
        if namespaced in ALL_TOOLS:
            return ALL_TOOLS[namespaced]
    
    # Best guess if unique
    candidates = fuzzy_match(tool_name)
    if len(candidates) == 1:
        logger.warning(f"Tool '{tool_name}' not found, using '{candidates[0]}'")
        return ALL_TOOLS[candidates[0]]
    
    raise ToolNotFoundError(f"Tool '{tool_name}' not found")
```

---

## Integration with Other Blockers

### Blocker #3: Tool Name Mapping
- **How used:** Tool names discovered via manifests must be consistent with Agent registry
- **Integration point:** `discover_all_tools()` returns dict keyed by standardized tool names
- **Dependency:** Requires tool naming convention to be finalized before Phase 1

### Blocker #4: MCP Dependencies
- **How related:** Some MCPs depend on others (e.g., encoding-specialist-mcp may depend on core-mcp)
- **Integration point:** `load_installed_mcps()` must respect dependency ordering
- **Implementation:** `INSTALLED.json` includes dependency graph, discovery respects order
- **Example:**
  ```json
  [
    {"name": "cybersecsuite-mcp-core", "version": "0.1.0"},
    {"name": "forensic-mcp", "depends_on": ["cybersecsuite-mcp-core"]},
    {"name": "encoding-specialist-mcp", "depends_on": ["cybersecsuite-mcp-core"]}
  ]
  ```

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Phase 1** | Manifest-based discovery via `tools.json` |
| **Phase 6** | Add dynamic discovery via `get_tools()` as optimization |
| **Dev Mode** | Load from `../ai-marketplace/mcps/` (git checkout) |
| **Prod Mode** | Load from `~/.cybersecsuite/INSTALLED.json` + package paths |
| **Fallback** | Gracefully skip missing MCPs, require at least one |
| **Validation** | CI/CD checks tool counts and schemas |
| **Tool Names** | Namespace collision handling via `{mcp}::{tool}` |

This phased approach delivers working externalization in Phase 1 while setting up Phase 6 optimization automatically.
