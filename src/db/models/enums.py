"""All enums for cybersecsuite database models."""
from enum import Enum


class RedBlueMode(str, Enum):
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    START = "start"
    STOP = "stop"
    MODE_SWITCH = "mode_switch"
    READ = "read"
    SCHEMA_CREATE = "schema_create"
    SCHEMA_DROP = "schema_drop"
    SEED = "seed"
    HEALTH_CHECK = "health_check"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"


class FindingStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    WONT_FIX = "wont_fix"
    INVESTIGATING = "investigating"


class IOCStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLEARED = "cleared"


class ForensicIOCStatus(str, Enum):
    ACTIVE = "active"
    WATCHING = "watching"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class IOCType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH_MD5 = "hash_md5"
    HASH_SHA1 = "hash_sha1"
    HASH_SHA256 = "hash_sha256"
    EMAIL = "email"
    FILE_PATH = "file_path"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    CERTIFICATE = "certificate"
    OTHER = "other"


class WatchlistPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaselineDomain(str, Enum):
    NETWORK = "network"
    FILESYSTEM = "filesystem"
    PROCESS = "process"
    REGISTRY = "registry"
    USER = "user"
    SERVICE = "service"
    KERNEL = "kernel"
    APPLICATION = "application"


class VulnerabilityStatus(str, Enum):
    OPEN = "open"
    PATCHED = "patched"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


class ModuleStatus(str, Enum):
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"
    LOADING = "loading"


class TagColor(str, Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    GRAY = "gray"
    BLACK = "black"


class ThreatActorSophistication(str, Enum):
    UNKNOWN = "unknown"
    MINIMAL = "minimal"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    INNOVATOR = "innovator"
    STRATEGIC = "strategic"


class MITRETactic(str, Enum):
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_DEVELOPMENT = "resource-development"
    INITIAL_ACCESS = "initial-access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    DEFENSE_EVASION = "defense-evasion"
    CREDENTIAL_ACCESS = "credential-access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral-movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command-and-control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"


class SessionPhase(str, Enum):
    RECONNAISSANCE = "reconnaissance"
    SCANNING = "scanning"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    REPORTING = "reporting"
    REMEDIATION = "remediation"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class YaraRuleStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"
    TESTED = "tested"


class YaraRuleSource(str, Enum):
    MANUAL = "manual"
    GENERATED = "generated"
    IMPORTED = "imported"
    COMMUNITY = "community"


class RuleChain(str, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    SEQUENCE = "sequence"


class RuleAction(str, Enum):
    ALERT = "alert"
    BLOCK = "block"
    LOG = "log"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


class SuggestionCategory(str, Enum):
    CONTEXT = "context"
    ACTION = "action"
    TOOL = "tool"
    INVESTIGATION = "investigation"
    REMEDIATION = "remediation"


class ProviderEnum(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    OTHER = "other"


class MachineType(str, Enum):
    WORKSTATION = "workstation"
    SERVER = "server"
    LAPTOP = "laptop"
    VM = "vm"
    CONTAINER = "container"
    IOT = "iot"
    OTHER = "other"


class DriveType(str, Enum):
    HDD = "hdd"
    SSD = "ssd"
    NVME = "nvme"
    USB = "usb"
    NETWORK = "network"
    OTHER = "other"


class DriveHealth(str, Enum):
    UNKNOWN = "unknown"
    GOOD = "good"
    WARNING = "warning"
    FAILING = "failing"
    FAILED = "failed"


class MemoryType(str, Enum):
    DDR3 = "ddr3"
    DDR4 = "ddr4"
    DDR5 = "ddr5"
    LPDDR4 = "lpddr4"
    LPDDR5 = "lpddr5"
    OTHER = "other"


class InterfaceType(str, Enum):
    ETHERNET = "ethernet"
    WIFI = "wifi"
    LOOPBACK = "loopback"
    BRIDGE = "bridge"
    VPN = "vpn"
    OTHER = "other"


class PocStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    WEAPONIZED = "weaponized"
    PATCHED = "patched"
    DISPUTED = "disputed"


# ── Provider model / tool registry enums ─────────────────────────────────────

class ModelTier(str, Enum):
    """Access tier required to use a model."""
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ModelStatus(str, Enum):
    """Live status of a model as reported by the provider."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    PREVIEW = "preview"
    DISABLED = "disabled"


class ToolType(str, Enum):
    """Source / category of a tool entry in the unified tool registry."""
    MCP_CYBERSEC = "mcp_cybersec"       # Own MCP tools — cybersec server
    MCP_DYSTOPIAN = "mcp_dystopian"     # Own MCP tools — dystopian server
    SDK_BUILTIN = "sdk_builtin"         # Anthropic builtin tools (computer_use, web_search, …)
    SDK_BETA = "sdk_beta"               # Anthropic beta tools (memory_20250818, skills, …)
    AGENT_SDK = "agent_sdk"             # Agent-SDK registered tools (from agent definitions)
    EXTERNAL = "external"               # Third-party MCP servers


class ToggleScopeType(str, Enum):
    """Scope level for a tool toggle state."""
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"


