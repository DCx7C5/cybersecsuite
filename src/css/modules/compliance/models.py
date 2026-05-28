"""Compliance module — regulatory framework mapping and reporting (Phase 7).

Models:
- ComplianceFramework: Define regulatory framework (NIST CSF, SOC2, ISO27001, MITRE)
- ControlMapping: Map findings/incidents to compliance controls
- ComplianceReport: Track compliance coverage % per framework + org
- FrameworkControl: Individual control definition within framework
"""

from tortoise import fields, models
from css.core.db.fields import DescriptionField, VersionField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .enums import FrameworkType, ComplianceStatus


class ComplianceFramework(BaseModel, TimestampMixin):
    """Compliance framework definition."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="compliance_frameworks",
        on_delete=fields.CASCADE,
    )
    
    # Framework type
    framework_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in FrameworkType],
        db_index=True,
    )
    
    # Metadata
    name = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="1.0.0")
    
    # Status
    is_active = fields.BooleanField(default=True, db_index=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "compliance_frameworks"
        unique_together = (("organization_id", "framework_type"),)


class FrameworkControl(BaseModel, TimestampMixin):
    """Individual control within compliance framework."""

    framework: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.ComplianceFramework",
        related_name="controls",
        on_delete=fields.CASCADE,
    )
    
    # Control identifier
    control_id = fields.CharField(max_length=64, db_index=True)
    
    # Details
    name = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    category = fields.CharField(max_length=128, db_index=True)
    
    # Mapping to attack surfaces
    cwe_ids = fields.JSONField(
        default=list,
        help_text="CWE identifiers covered by this control"
    )
    mitre_techniques = fields.JSONField(
        default=list,
        help_text="MITRE ATT&CK techniques mitigated"
    )
    
    # Risk assessment
    priority = fields.CharField(
        max_length=16,
        choices=["critical", "high", "medium", "low"],
        default="medium",
    )
    risk_impact = fields.CharField(max_length=255, default="")
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "framework_controls"
        unique_together = (("framework_id", "control_id"),)
        indexes = [
            models.Index(fields=["framework_id", "category"]),  # type: ignore[reportPrivateImportUsage]
        ]


class ControlMapping(BaseModel, TimestampMixin):
    """Map findings/incidents/scans to compliance controls."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="control_mappings",
        on_delete=fields.CASCADE,
    )
    
    control: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.FrameworkControl",
        related_name="mappings",
        on_delete=fields.CASCADE,
    )
    
    # Finding source (incident, scan result, evidence, etc.)
    finding_type = fields.CharField(
        max_length=32,
        choices=["incident", "scan", "evidence", "assessment", "audit"],
        db_index=True,
    )
    finding_id = fields.CharField(max_length=255, db_index=True)
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=[s.value for s in ComplianceStatus],
        default="unknown",
        db_index=True,
    )
    
    # Details
    evidence = fields.TextField(
        default="",
        help_text="How this finding demonstrates control compliance"
    )
    remediation_notes = fields.TextField(default="")
    
    # Timeline
    found_at = fields.DatetimeField(db_index=True)
    remediated_at = fields.DatetimeField(null=True)
    verified_at = fields.DatetimeField(null=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "control_mappings"
        unique_together = (("control_id", "finding_id"),)
        indexes = [
            models.Index(fields=["organization_id", "status"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["finding_type", "finding_id"]),  # type: ignore[reportPrivateImportUsage]
        ]


class ComplianceReport(BaseModel):
    """Compliance report snapshot — % coverage per framework."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="compliance_reports",
        on_delete=fields.CASCADE,
    )
    framework: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.ComplianceFramework",
        related_name="reports",
        on_delete=fields.CASCADE,
    )
    
    # Coverage metrics
    total_controls = fields.IntField(default=0)
    compliant_controls = fields.IntField(default=0)
    partially_compliant_controls = fields.IntField(default=0)
    non_compliant_controls = fields.IntField(default=0)
    not_applicable_controls = fields.IntField(default=0)
    
    # Summary
    compliance_percentage = fields.FloatField(default=0.0)
    
    # Risk score (0-100, higher = worse)
    risk_score = fields.FloatField(default=50.0)
    
    # Trend
    previous_percentage = fields.FloatField(null=True)
    trend = fields.CharField(
        max_length=16,
        choices=["improving", "stable", "declining"],
        default="stable",
    )
    
    # Report metadata
    generated_at = fields.DatetimeField(auto_now_add=True)
    scope = fields.CharField(
        max_length=255,
        default="",
        help_text="e.g., 'all systems', 'production only', 'data processing'"
    )
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "compliance_reports"
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["organization_id", "framework_id", "generated_at"]),  # type: ignore[reportPrivateImportUsage]
        ]

