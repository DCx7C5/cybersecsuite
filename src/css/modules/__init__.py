"""CSS Modules package — auto-discovered module registry and public API exports.

Auto-discovery loads all sub-modules and re-exports their public APIs.
Modules are discovered dynamically; missing dependencies are warned but don't fail.

Available modules (auto-discovered):
- agents: Agent definitions and registry
- cache: Caching backends (Redis, in-memory)
- capabilities: Capability definitions and registry
- chat: Chat message types and handlers
- google_a2a: Google A2A protocol and endpoints
- llm_proxy: LLM proxy and routing
- orchestration: Multi-orchestrator coordination (TeamLeader, TeamMember, OrchestratorProcess)
- permissions: Permission system and checks
- roles: Orchestration-specific roles (Orchestrator, TeamLeader, TeamMember)
- scopes: Scope context and isolation
- skills: Skill definitions and registry
- streaming: Query streaming and session management
- tags: Tag system and models
- tasks: Task lifecycle and state machine
- teams: Team scope isolation and orchestrator pool
- tools: Tool definitions and registry
- working_dir: Working directory management
"""

import sys
from pathlib import Path
from typing import Any

from css.core.logger import getLogger
logger = getLogger("modules")

# Track imported modules
_MODULES: dict[str, Any] = {}
_IMPORT_ERRORS: dict[str, Exception] = {}


def _discover_modules() -> None:
    """Discover and import all sub-modules (auto-discovery)."""
    modules_dir = Path(__file__).parent

    # Exclude these directories from auto-discovery
    EXCLUDED = {"__pycache__", "__init__.py", "base", "legacy"}

    for item in sorted(modules_dir.iterdir()):
        # Skip non-directories and excluded items
        if not item.is_dir() or item.name in EXCLUDED:
            continue

        module_name = item.name
        full_module_name = f"css.modules.{module_name}"

        try:
            # Dynamically import the module
            module = __import__(full_module_name, fromlist=[module_name])
            _MODULES[module_name] = module
            logger.debug(f"Auto-discovered module: {module_name}")
        except ImportError as e:
            # Log warning but don't fail — some modules may have optional dependencies
            _IMPORT_ERRORS[module_name] = e
            logger.warning(f"Failed to import module {module_name}: {e}")
        except Exception as e:
            # Log other errors
            _IMPORT_ERRORS[module_name] = e
            logger.error(f"Error loading module {module_name}: {e}")


def get_module(module_name: str) -> Any | None:
    """Get a discovered module by name.

    Args:
        module_name: Name of the module (e.g., "orchestration", "tasks")

    Returns:
        Module object, or None if not found/failed to import
    """
    if not _MODULES and not _IMPORT_ERRORS:
        _discover_modules()

    return _MODULES.get(module_name)


def list_modules() -> list[str]:
    """List all successfully discovered modules."""
    if not _MODULES and not _IMPORT_ERRORS:
        _discover_modules()
    return sorted(_MODULES.keys())


def list_failed_modules() -> dict[str, Exception]:
    """List modules that failed to import and their errors."""
    if not _MODULES and not _IMPORT_ERRORS:
        _discover_modules()
    return _IMPORT_ERRORS.copy()


# Perform auto-discovery on import
_discover_modules()

# Selective re-exports of commonly used modules
# (Keep this minimal to avoid circular imports)
__all__ = [
    # Core orchestration
    "getLogger",
    "get_module",
    "list_modules",
    "list_failed_modules",
    # Module shortcuts (optional — users can do "from modules.X import Y" directly)
]

# Make discovered modules accessible as attributes
# e.g., modules.orchestration, modules.tasks, modules.teams
sys.modules[__name__].__dict__.update(
    {name: module for name, module in _MODULES.items()}
)

logger.info(
    f"Modules auto-discovery complete: {len(_MODULES)} loaded, "
    f"{len(_IMPORT_ERRORS)} failed"
)
