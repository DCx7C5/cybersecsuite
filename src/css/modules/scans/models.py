"""Scans module — vulnerability assessment lifecycle (Phase 7)."""

from tortoise import Model, fields
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Types of security scans."""
    VULNERABILITY = "vulnerability"
    COMPLIANCE = "compliance"
    CONFIGURATION = "configuration"
    MALWARE = "malware"
    WEB_APPLICATION = "web_application"
    NETWORK = "network"
    CODE = "code"
    CONTAINER = "container"


class ScanStatus(str, Enum):
    """Scan lifecycle status."""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityRating(str, Enum):
    """Finding severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Scan(Model):
    """Vulnerability/compliance scan."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="scans",
        on_delete=fields.CASCADE,
    )
    
    # Identity
    scan_id = fields.CharField(max_length=64, db_index=True)
    scan_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in ScanType],
        db_index=True,
    )
    
    # Target
    target = fields.CharField(
        max_length=512,
        help_text="IP, domain, network range, or resource ID"
    )
    scope = fields.CharField(
        max_length=512,
        help_text="Detailed scope (ports, paths, etc.)"
    )
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=[s.value for s in ScanStatus],
        default="scheduled",
        db_index=True,
    )
    
    # Timeline
    scheduled_at = fields.DatetimeField()
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    
    # Results
    findings_count = fields.IntField(default=0)
    critical_count = fields.IntField(default=0)
    high_count = fields.IntField(default=0)
    medium_count = fields.IntField(default=0)
    low_count = fields.IntField(default=0)
    
    # Scanner
    scanner_name = fields.CharField(max_length=128, default="")
    scanner_version = fields.CharField(max_length=32, default="")
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "scans"
        unique_together = (("organization", "scan_id"),)


class Finding(Model):
    """Individual vulnerability/compliance finding."""
    
    id = fields.BigIntField(primary_key=True)
    scan: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Scan",
        related_name="findings",
        on_delete=fields.CASCADE,
    )
    
    # Identity
    finding_id = fields.CharField(max_length=128, db_index=True)
    
    # Issue details
    title = fields.CharField(max_length=512)
    description = fields.TextField()
    severity = fields.CharField(
        max_length=16,
        choices=[s.value for s in SeverityRating],
        db_index=True,
    )
    
    # Vulnerability data
    cve_id = fields.CharField(max_length=32, null=True, db_index=True)
    cwe_id = fields.CharField(max_length=32, null=True)
    cvss_score = fields.FloatField(null=True)
    
    # Remediation
    remediation = fields.TextField(default="")
    affected_resource = fields.CharField(max_length=512)
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=["open", "in_progress", "resolved", "false_positive"],
        default="open",
        db_index=True,
    )
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "scan_findings"
        unique_together = (("scan", "finding_id"),)


__all__ = [
    "ScanType",
    "ScanStatus",
    "SeverityRating",
    "Scan",
    "Finding",
]
