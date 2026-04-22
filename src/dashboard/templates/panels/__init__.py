"""Dashboard panels module — organized by category."""
from .platform import _providers, _usage, _health, _telemetry, _providers_hub
from .agents import _agents, _routing, _factory, _prompts, _agent_query
from .forensics import (
    _investigations,
    _findings,
    _iocs,
    _yara,
    _intel,
    _audit,
    _compliance,
)
from .operations import _cases, _tasks, _pocs, _a2a
from .data import _opensearch, _explorer, _templates
from .advanced import (
    _chat,
    _team_builder,
    _agent_crafter,
    _agent_factory,
    _workflows,
    _flowgraph,
    _sdk_lab,
)
from .settings import _settings, _settings_cybersecsuite, _crypto, _qol_controls
from .agent_factory import _marketplace_agent_factory
from .marketplace import _marketplace

__all__ = [
    # Platform
    "_providers",
    "_usage",
    "_health",
    "_telemetry",
    "_providers_hub",
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
    "_intel",
    "_audit",
    "_compliance",
    # Operations
    "_cases",
    "_tasks",
    "_pocs",
    "_a2a",
    # Data
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
    "_sdk_lab",
    # Settings
    "_settings",
    "_settings_cybersecsuite",
    "_crypto",
    "_qol_controls",
    "_marketplace_agent_factory",
    "_marketplace",
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
        + _intel()
        + _audit()
        + _compliance()
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
        + _qol_controls()
        + _telemetry()
        + _providers_hub()
        + _templates()
        + _flowgraph()
        + _sdk_lab()
        + _marketplace()
        + _marketplace_agent_factory()
    )