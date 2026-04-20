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
    "db.models.audit",
    "db.models.vulnerability",
    "db.models.defense",
    "db.models.layers",
    "db.models.tag",
    # Artifacts + crypto
    "db.models.artifact",
    "db.models.artifacts",
    # A2A
    "db.models.a2a_task",
    # Browser forensics
    "db.models.browser_forensic",
    # Phase 0 — Case Intake
    "db.models.case_intake",
    # API / system
    "db.models.api_usage_log",
    "db.models.update_log_entry",
    "db.models.user_guidance",
]

from db.models.api_account import ApiAccount
from db.models.browser_forensic import BrowserForensicFinding
from db.models.provider import Provider, ProviderAuthMethod
from db.models.settings import ScopedEntry, GlobalSettings

__all__ = [
    "MODEL_MODULES",
    "ApiAccount",
    "BrowserForensicFinding",
    "Provider",
    "ProviderAuthMethod",
    "ScopedEntry",
    "GlobalSettings",
]
