"""
Core investigation models — Finding, IOC, Risk, MITRETechnique, Baseline, WatchlistItem, SharedEntry.

All models inherit ScopedEntry for automatic workspace/project/session scoping.
Soft-delete pattern added (is_active + deleted_at).
"""
from tortoise import fields

from db.models.enums import (
    Severity, FindingStatus, IOCStatus, Confidence,
    WatchlistPriority, BaselineDomain,
)
from db.models.scope import ScopedEntry


class Finding(ScopedEntry):
    """Main security finding model."""
    id = fields.BigIntField(primary_key=True)
    title = fields.CharField(max_length=512, db_index=True)
    description = fields.TextField()
    severity = fields.CharEnumField(Severity, default=Severity.MEDIUM, db_index=True)
    status = fields.CharEnumField(FindingStatus, default=FindingStatus.OPEN, db_index=True)
    confidence = fields.CharEnumField(Confidence, default=Confidence.MEDIUM, db_index=True)
    location = fields.CharField(max_length=1024, null=True)
    evidence = fields.TextField(null=True)
    evidence_hash = fields.CharField(max_length=128, null=True)
    command_output = fields.TextField(null=True)
    cross_validation = fields.TextField(null=True)
    next_action = fields.TextField(null=True)
    analyst_notes = fields.TextField(default="")
    remediation = fields.TextField(default="")
    resolved_at = fields.DatetimeField(null=True)
    tags = fields.JSONField(default=list)

    # Relationships
    related_iocs: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.IOC", related_name="findings", through="finding_ioc"
    )
    related_hosts: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.Host", related_name="findings", through="finding_host"
    )
    mitre_techniques: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.MITRETechnique", related_name="findings"
    )

    class Meta:
        table = "findings"
        ordering = ["-updated_at"]
        indexes = [
            ("project_id", "severity", "status"),
            ("session_id", "severity"),
            ("created_at",),
        ]


class IOC(ScopedEntry):
    """Indicator of Compromise."""
    id = fields.BigIntField(primary_key=True)
    ioc_id = fields.CharField(max_length=50, unique=True, db_index=True)
    ioc_type = fields.CharField(max_length=64, db_index=True)
    value = fields.CharField(max_length=2048, db_index=True)
    confidence = fields.CharEnumField(Confidence, default=Confidence.LOW, db_index=True)
    status = fields.CharEnumField(IOCStatus, default=IOCStatus.ACTIVE, db_index=True)
    sightings = fields.IntField(default=1)
    first_session_id = fields.CharField(max_length=128, null=True)
    last_session_id = fields.CharField(max_length=128, null=True)
    context = fields.JSONField(default=dict)
    source = fields.CharField(max_length=256, null=True)
    evidence_hash = fields.CharField(max_length=128, null=True)
    tags = fields.JSONField(default=list)

    # Link to canonical intelligence record
    intel_match = fields.ForeignKeyField(
        "models.IOCDatabaseEntry", related_name="ioc_matches", null=True, on_delete=fields.SET_NULL
    )

    class Meta:
        table = "iocs"
        ordering = ["-updated_at"]
        indexes = [
            ("ioc_type", "status"),
            ("value",),
        ]


class Risk(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    risk_id = fields.CharField(max_length=128, db_index=True)
    title = fields.CharField(max_length=512, default="")
    description = fields.TextField(default="")
    impact = fields.CharField(max_length=64, default="")
    likelihood = fields.CharField(max_length=64, default="")
    mitigation = fields.TextField(default="")
    tags = fields.JSONField(default=list)

    class Meta:
        table = "risks"
        ordering = ["-updated_at"]


class MITRETechnique(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    technique_id = fields.CharField(max_length=32, db_index=True)
    name = fields.CharField(max_length=256)
    description = fields.TextField(default="")
    tactic = fields.CharField(max_length=64, default="")
    finding = fields.ForeignKeyField("models.Finding", related_name="primary_mitre_techniques", null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "mitre_techniques"


class Baseline(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    domain = fields.CharEnumField(BaselineDomain, db_index=True)
    snapshot_data = fields.JSONField(default=dict)
    snapshot_hash = fields.CharField(max_length=128, default="")
    confirmed_clean = fields.BooleanField(default=False)
    session_ref = fields.CharField(max_length=128, default="")
    notes = fields.TextField(default="")

    class Meta:
        table = "baselines"


class WatchlistItem(ScopedEntry):
    id = fields.BigIntField(primary_key=True)
    item_type = fields.CharField(max_length=64, db_index=True)
    value_pattern = fields.TextField()
    reason = fields.TextField(default="")
    priority = fields.CharEnumField(WatchlistPriority, default=WatchlistPriority.MEDIUM, db_index=True)
    added_by_session_id = fields.CharField(max_length=128, default="")
    last_checked = fields.DatetimeField(null=True)
    clean_check_count = fields.IntField(default=0)

    class Meta:
        table = "watchlist_items"
