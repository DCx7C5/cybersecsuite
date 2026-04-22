"""Model registry — all Tortoise ORM model modules."""

MODEL_MODULES: list[str] = [
    # Scope + core shared entry store
    "db.models.scope",
    "db.models.core",
    "db.models.settings",
    # Enums (no models, but included for Tortoise enum registration)
    # Intelligence
    "db.models.cve",
    "db.models.poc",
    "db.models.cve_entry",
    "db.models.cwe",
    "db.models.capec",
    "db.models.mitre_technique",
    "db.models.mitre_actor",
    "db.models.mitre_software",
    "db.models.references",
    "db.models.feed_snapshot",
    "db.models.ioc",
    "db.models.ioc_entry",
    "db.models.misp",
    "db.models.opencti",
    "db.models.threat_intel",
    # Accounts + API keys
    "db.models.api_account",
    "db.models.provider",
    "db.models.provider_model",
    "db.models.tool_registry",
    # Tool seeds is not a model module — loaded separately
    # Investigation + forensic
    "db.models.investigation",
    "db.models.forensic",
    "db.models.baselines",
    "db.models.network",
    "db.models.kernel",
    "db.models.machine",
    "db.models.yara_rule",
    "db.models.threat_profile_entry",
    # Compliance + audit
    "db.models.compliance",
    "db.models.nist_csf",
    "db.models.nist_ai_rmf",
    "db.models.vulnerability",
    "db.models.defense",
    "db.models.layers",
    "db.models.tag",
    # Artifacts + crypto
    "db.models.artifact",
    "db.models.artifacts",
    # A2A
    "db.models.a2a_task",
    # Phase 0 — Case Intake
    "db.models.case_intake",
    # API / system
    "db.models.user_guidance",
    # LLM orchestration layer
    "db.models.llm_session",
    # Intelligence feed sources
    "db.models.intel_feed_source",
    # Prompts
    "db.models.prompt",
    # Phase 0 — AI Provider State Management
    "db.models.ai_provider_state",
    "db.models.ai_provider_events",
    "db.models.worker_context",
]

from db.models.api_account import ApiAccount  # noqa: E402
from db.models.provider import Provider, ProviderAuthMethod  # noqa: E402
from db.models.provider_model import ProviderModel, AccountModel  # noqa: E402
from db.models.tool_registry import ToolRegistry, ToolToggleState, ToolToggleRegistry, AccountToolAccess  # noqa: E402
from db.models.settings import ScopedEntry, GlobalSettings  # noqa: E402
from db.models.llm_session import LlmSession  # noqa: E402
from db.models.intel_feed_source import IntelFeedSource  # noqa: E402
from db.models.prompt import Prompt  # noqa: E402
from db.models.ai_provider_state import AIProviderState  # noqa: E402
from db.models.ai_provider_events import AIProviderEvent  # noqa: E402
from db.models.worker_context import WorkerContext  # noqa: E402

__all__ = [
    "MODEL_MODULES",
    "ApiAccount",
    "Provider",
    "ProviderAuthMethod",
    "ProviderModel",
    "AccountModel",
    "ToolRegistry",
    "ToolToggleState",
    "ToolToggleRegistry",
    "AccountToolAccess",
    "ScopedEntry",
    "GlobalSettings",
    "LlmSession",
    "IntelFeedSource",
    "Prompt",
    "AIProviderState",
    "AIProviderEvent",
    "WorkerContext",
]
