from enum import Enum


class DocumentType(str, Enum):
    """Knowledge document source types."""
    CVE_FEED = "cve_feed"
    PLAYBOOK = "playbook"
    THREAT_REPORT = "threat_report"
    RUNBOOK = "runbook"
    INCIDENT_RETROSPECTIVE = "incident_retrospective"
    POLICY = "policy"
    TOOL_DOCUMENTATION = "tool_documentation"
    VENDOR_ADVISORY = "vendor_advisory"
    CUSTOM = "custom"


class DocumentStatus(str, Enum):
    """Document lifecycle status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
