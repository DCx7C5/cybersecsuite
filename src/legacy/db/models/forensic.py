"""
Forensic session & project models — extended scope for deep investigations.
"""
from css.core.db.models.base import BaseModel
from tortoise import fields
from css.core.db.fields import DescriptionField, PathField
from db.models.enums import (
    SeverityLevel, ConfidenceLevel, SessionPhase, SessionStatus,
)


class ForensicProject(BaseModel):
    """Extended project model with threat-intel and case-tracking metadata."""
    id = fields.BigIntField(primary_key=True)
    project_name = fields.CharField(max_length=255, db_index=True)
    description = DescriptionField(null=True)
    case_id = fields.CharField(max_length=100, unique=True, db_index=True, null=True)
    classification = fields.CharField(max_length=64, default="", description="TLP or custom classification.")
    lead_investigator = fields.CharField(max_length=255, default="")
    team_members = fields.JSONField(default=list, description="List of team member names/IDs.")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    closed_at = fields.DatetimeField(null=True)
    status = fields.CharEnumField(SessionStatus, default=SessionStatus.ACTIVE, db_index=True)
    threat_actor_profile = fields.TextField(null=True)
    attribution_confidence = fields.CharEnumField(ConfidenceLevel, default=ConfidenceLevel.LOW)
    session_count = fields.IntField(default=0)
    total_iocs = fields.IntField(default=0)
    total_findings = fields.IntField(default=0)
    severity_counts = fields.JSONField(default=dict)
    executive_summary = fields.TextField(default="", description="High-level summary for reporting.")
    scope_notes = fields.TextField(default="", description="What's in/out of scope.")
    tags = fields.JSONField(default=list)
    # Link to the core scope Project this forensic project extends
    scope_project = fields.ForeignKeyField(
        "models.Project",
        related_name="forensic_projects",
        null=True,
        on_delete=fields.SET_NULL,
        description="Core scope Project this forensic project is linked to.",
    )

    class Meta:
        table = "forensic_projects"
        ordering = ["-updated_at"]
        indexes = [
            ("status",),
            ("case_id",),
        ]

    def __str__(self):
        return f"ForensicProject({self.case_id}: {self.project_name})"


class ForensicSession(BaseModel):
    """Individual forensic investigation session with full system context."""
    id = fields.BigIntField(primary_key=True)
    session_id = fields.CharField(max_length=100, unique=True, db_index=True)
    project = fields.ForeignKeyField("models.ForensicProject", related_name="sessions", db_index=True)
    scope_session = fields.ForeignKeyField(
        "models.Session",
        related_name="forensic_sessions",
        null=True,
        on_delete=fields.SET_NULL,
        description="Core scope Session this forensic session maps to.",
    )
    start_time = fields.DatetimeField(auto_now_add=True, db_index=True)
    end_time = fields.DatetimeField(null=True)
    phase = fields.CharEnumField(SessionPhase, default=SessionPhase.RECONNAISSANCE, db_index=True)
    status = fields.CharEnumField(SessionStatus, default=SessionStatus.ACTIVE, db_index=True)
    investigator = fields.CharField(max_length=255, db_index=True, default="")
    agent = fields.CharField(max_length=100, db_index=True)
    mode = fields.CharField(max_length=32, default="blue", db_index=True)
    # System info
    hostname = fields.CharField(max_length=255, null=True)
    os_info = fields.CharField(max_length=255, null=True)
    distribution = fields.CharField(max_length=100, null=True)
    kernel_version = fields.CharField(max_length=100, null=True)
    architecture = fields.CharField(max_length=50, null=True)
    desktop_env = fields.CharField(max_length=100, null=True)
    gpu_info = fields.CharField(max_length=255, null=True)
    network_interface = fields.CharField(max_length=50, null=True)
    local_ip = fields.CharField(max_length=45, null=True)
    # Counters
    findings_count = fields.IntField(default=0)
    ioc_count = fields.IntField(default=0)
    new_ioc_count = fields.IntField(default=0)
    commands_executed = fields.IntField(default=0)
    severity_summary = fields.JSONField(default=dict)
    iocs_loaded = fields.IntField(default=0)
    watchlist_loaded = fields.IntField(default=0)
    cleared_loaded = fields.IntField(default=0)
    iocs_synced = fields.IntField(default=0)
    # Results
    verdict = fields.CharField(max_length=255, null=True)
    verdict_confidence = fields.CharEnumField(ConfidenceLevel, null=True)
    executive_summary = fields.TextField(default="")
    lessons_learned = fields.TextField(default="")
    storage_path = PathField(max_length=500, null=True)
    tags = fields.JSONField(default=list)

    class Meta:
        table = "forensic_sessions"
        ordering = ["-start_time"]
        indexes = [
            ("project_id", "status"),
            ("project_id", "phase"),
            ("investigator",),
            ("agent",),
        ]

    @property
    def duration_seconds(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        return f"ForensicSession({self.session_id} [{self.phase}])"


class ForensicFinding(BaseModel):
    """Extended finding with evidence, chain-of-custody, and cross-validation."""
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField("models.ForensicSession", related_name="forensic_findings", db_index=True)
    finding_id = fields.CharField(max_length=50, db_index=True)
    title = fields.CharField(max_length=255, db_index=True)
    severity = fields.CharEnumField(SeverityLevel, db_index=True)
    confidence = fields.CharEnumField(ConfidenceLevel, default=ConfidenceLevel.MEDIUM)
    status = fields.CharField(max_length=50, default="open", db_index=True)
    location = fields.CharField(max_length=500, null=True)
    description = DescriptionField()
    evidence = fields.TextField(null=True)
    command_output = fields.TextField(null=True)
    cross_validation = fields.TextField(null=True)
    cross_validation_result = fields.BooleanField(null=True, description="Whether cross-validation passed.")
    next_action = fields.CharField(max_length=500, null=True)
    analyst_notes = fields.TextField(default="")
    related_iocs = fields.ManyToManyField("models.IOCEntry", related_name="forensic_findings")
    related_artifacts = fields.ManyToManyField("models.ForensicArtifact", related_name="forensic_findings")
    evidence_hash = fields.CharField(max_length=128, null=True, description="SHA-256 for integrity.")
    chain_of_custody = fields.JSONField(default=dict)
    attack_techniques = fields.JSONField(default=list)
    mitre_techniques: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.ForensicMITRETechnique",
        related_name="forensic_findings",
        through="forensic_finding_techniques",
        description="MITRE ATT&CK techniques mapped to this finding.",
    )
    defense_evasion = fields.JSONField(default=list)
    forensic_countermeasures = fields.JSONField(default=list)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "forensic_findings"
        ordering = ["-created_at"]
        unique_together = ("session_id", "finding_id")
        indexes = [
            ("session_id", "severity"),
            ("session_id", "status"),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title}"
