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
    "db.models.api_service",
    "db.models.api_service_model",
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
    # Phase 0 — ApiService State Management
    "db.models.api_service_state",
    "db.models.api_service_events",
    "db.models.worker_context",
    # Phase 5C — Worker state machine (t366, t367, t368)
    "db.models.worker",
    # Phase 0.5 — Marketplace models
    "db.models.marketplace",
    # Plan management
    "db.models.plan",
]

from db.models.api_account import ApiAccount  # noqa: E402
from db.models.api_service import ApiService, ApiServiceAuthMethod  # noqa: E402
from db.models.api_service_model import ApiServiceModel, AccountModel  # noqa: E402
from db.models.tool_registry import ToolRegistry, ToolToggleState, ToolToggleRegistry, AccountToolAccess  # noqa: E402
from db.models.settings import ScopedEntry, GlobalSettings  # noqa: E402
from db.models.core import AuditLog  # noqa: E402
from db.models.llm_session import LlmSession  # noqa: E402
from db.models.intel_feed_source import IntelFeedSource  # noqa: E402
from db.models.prompt import Prompt  # noqa: E402
from db.models.api_service_state import ApiServiceState  # noqa: E402
from db.models.api_service_events import ApiServiceEvent  # noqa: E402
from db.models.worker_context import WorkerContext  # noqa: E402
from db.models.worker import (  # noqa: E402
    WorkerState,
    WorkerStateTransition,
    WorkerSession,
    WorkerAuditLog,
)
from db.models.marketplace import (  # noqa: E402
    MarketplaceAsset,
    MarketplaceMCP,
    Skill,
    Agent,
    Plugin,
    Workflow,
)
from db.models.plan import Plan, Task, Todo  # noqa: E402

__all__ = [
    "MODEL_MODULES",
    "ApiAccount",
    "ApiService",
    "ApiServiceAuthMethod",
    "ApiServiceModel",
    "AccountModel",
    "ToolRegistry",
    "ToolToggleState",
    "ToolToggleRegistry",
    "AccountToolAccess",
    "ScopedEntry",
    "GlobalSettings",
    "AuditLog",
    "LlmSession",
    "IntelFeedSource",
    "Prompt",
    "ApiServiceState",
    "ApiServiceEvent",
    "WorkerContext",
    "WorkerState",
    "WorkerStateTransition",
    "WorkerSession",
    "WorkerAuditLog",
    "MarketplaceAsset",
    "MarketplaceMCP",
    "Skill",
    "Agent",
    "Plugin",
    "Workflow",
    "Plan",
    "Task",
    "Todo",
]
