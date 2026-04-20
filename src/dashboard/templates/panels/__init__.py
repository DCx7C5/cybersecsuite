"""Dashboard panels module — organized by category."""
from .platform import _providers, _usage, _health, _telemetry
from .agents import _agents, _routing, _factory, _prompts, _agent_query
from .forensics import (
    _investigations,
    _findings,
    _iocs,
    _yara,
    _network,
    _intel,
    _audit,
    _compliance,
)
from .operations import _cases, _tasks, _pocs, _a2a
from .data import _dbcounts, _opensearch, _explorer, _templates
from .advanced import (
    _chat,
    _team_builder,
    _agent_crafter,
    _agent_factory,
    _workflows,
    _flowgraph,
)
from .settings import _settings, _settings_cybersecsuite, _crypto

__all__ = [
    # Platform
    "_providers",
    "_usage",
    "_health",
    "_telemetry",
    # Agents
    "_agents",
    "_routing",
    "_factory",
    "_prompts",
    "_agent_query",
    # Forensics
    "_investigations",
    "_findings",
    "_iocs",
    "_yara",
    "_network",
    "_intel",
    "_audit",
    "_compliance",
    # Operations
    "_cases",
    "_tasks",
    "_pocs",
    "_a2a",
    # Data
    "_dbcounts",
    "_opensearch",
    "_explorer",
    "_templates",
    # Advanced
    "_chat",
    "_team_builder",
    "_agent_crafter",
    "_agent_factory",
    "_workflows",
    "_flowgraph",
    # Settings
    "_settings",
    "_settings_cybersecsuite",
    "_crypto",
    "all_panels",
]


def all_panels() -> str:
    """Aggregate all panels into single HTML string."""
    return (
        _providers()
        + _usage()
        + _health()
        + _agents()
        + _routing()
        + _factory()
        + _prompts()
        + _crypto()
        + _a2a()
        + _investigations()
        + _findings()
        + _iocs()
        + _yara()
        + _network()
        + _intel()
        + _audit()
        + _compliance()
        + _dbcounts()
        + _opensearch()
        + _explorer()
        + _cases()
        + _tasks()
        + _pocs()
        + _agent_query()
        + _chat()
        + _team_builder()
        + _agent_crafter()
        + _agent_factory()
        + _workflows()
        + _settings()
        + _settings_cybersecsuite()
        + _telemetry()
        + _templates()
        + _flowgraph()
    )