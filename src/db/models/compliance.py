"""
Compliance & Agent Permission Models
- Regulatory compliance rules
- Agent permission & root/sudo control (reference layer only)
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import Severity


# =====================================================================
# Regulatory / Compliance (unchanged from previous version)
# =====================================================================
class ComplianceRule(Model):
    """Compliance and regulatory requirements."""
    id = fields.IntField(primary_key=True)
    rule_id = fields.CharField(max_length=100, unique=True, db_index=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    framework = fields.CharField(max_length=100)
    severity = fields.CharEnumField(Severity, null=True)
    check_procedures = fields.JSONField(default=list)
    remediation_steps = fields.JSONField(default=list)
    evidence_requirements = fields.JSONField(default=list)
    retention_period_days = fields.IntField(default=365)
    audit_frequency = fields.CharField(max_length=50, default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "compliance_rules"


class ComplianceCheck(Model):
    """Compliance check results."""
    id = fields.IntField(primary_key=True)
    session = fields.ForeignKeyField("models.Session", related_name="compliance_checks")
    rule = fields.ForeignKeyField("models.ComplianceRule", related_name="check_results")
    status = fields.CharField(max_length=50)
    score = fields.FloatField(null=True)
    findings = fields.JSONField(default=list)
    remediation_required = fields.BooleanField(default=False)
    remediation_priority = fields.CharEnumField(Severity, null=True)
    checked_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "compliance_checks"


# =====================================================================
# AGENT PERMISSION & ROOT CONTROL (NEW)
# =====================================================================
class AgentRootPermission(Model):
    """Controls which agents are allowed to request root/sudo execution.
    This is a REFERENCE / POLICY layer only — agents MUST check these rules themselves.
    """
    id = fields.IntField(primary_key=True)

    # Which agent this rule applies to
    agent_name = fields.CharField(max_length=100, db_index=True)

    # Run as which user (0 = true root, 1000 = normal user, etc.)
    run_as_uid = fields.IntField(default=1000, db_index=True)

    # === DEFAULTS YOU REQUESTED ===
    default_read = fields.BooleanField(
        default=True,
        description="Read access everywhere by default (unless overridden)"
    )
    can_write_project = fields.BooleanField(
        default=True,
        description="Can write inside current project/session directories"
    )
    can_write_anywhere = fields.BooleanField(
        default=False,
        description="True = can write system-wide (very dangerous, rarely used)"
    )

    # Fine-grained overrides
    path_pattern = fields.CharField(
        max_length=500,
        null=True,
        description="Specific path pattern this rule applies to (e.g. '/var/log/*', 'cybersec-sessions/**')"
    )
    can_read = fields.BooleanField(default=False)
    can_write = fields.BooleanField(default=False)
    can_execute = fields.BooleanField(default=False)

    # Explicit root tools & commands
    allowed_tools = fields.JSONField(
        default=list,
        description="Explicit list of allowed root tools (e.g. ['journalctl', 'bpftool', 'tcpdump'])"
    )
    command_pattern = fields.CharField(
        max_length=500,
        null=True,
        description="Regex/glob pattern for full command line"
    )

    # General flags
    allowed = fields.BooleanField(default=False)
    requires_user_approval = fields.BooleanField(default=True)
    max_duration_seconds = fields.IntField(default=60)

    description = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "agent_root_permissions"
        indexes = [
            ("agent_name",),
            ("run_as_uid",),
            ("allowed",),
        ]
        unique_together = [("agent_name", "command_pattern")]
