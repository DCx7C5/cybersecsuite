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


class SourceType(str, Enum):
    """Source type for knowledge documents."""
    URL = "url"
    INTERNAL_FILE = "internal_file"
    USER_UPLOADED = "user_uploaded"
    API_SYNC = "api_sync"


class SearchType(str, Enum):
    """Search method for knowledge base queries."""
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    TAG_FILTER = "tag_filter"


class RelevanceFeedback(str, Enum):
    """User feedback on search result relevance."""
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"
    PARTIALLY_RELEVANT = "partially_relevant"
    NONE = "none"


class TagCategory(str, Enum):
    """Knowledge tag category."""
    TECHNIQUE = "technique"
    TOOL = "tool"
    ACTOR = "actor"
    MALWARE = "malware"
    CVE = "cve"
    MITIGATION = "mitigation"
    DETECTION = "detection"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"
