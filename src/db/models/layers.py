"""
Layer-specific models — system, project, and session state layers.
These are configuration and state layers, not operational data.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import Severity


class SystemLayer(Model):
    """System-wide persistent configuration and baselines."""
    id = fields.IntField(primary_key=True)
    hostname = fields.CharField(max_length=255, unique=True, null=True)
    name = fields.CharField(max_length=255, default="", db_index=True)
    data = fields.JSONField(default=dict)
    system_uuid = fields.CharField(max_length=100, null=True)
    security_profile = fields.JSONField(default=dict)
    trusted_processes = fields.JSONField(default=list)
    trusted_networks = fields.JSONField(default=list)
    hardening_level = fields.CharField(max_length=50, default="default")
    applied_hardenings = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "system_layers"


class ProjectLayer(Model):
    """Project-specific configuration overrides."""
    id = fields.IntField(primary_key=True)
    project = fields.OneToOneField("models.Project", related_name="layer_config", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=255, default="", db_index=True)
    data = fields.JSONField(default=dict)
    threat_model = fields.JSONField(default=dict)
    custom_baselines = fields.JSONField(default=dict)
    monitoring_rules = fields.JSONField(default=list)
    investigation_scope = fields.JSONField(default=list)
    excluded_areas = fields.JSONField(default=list)
    evidence_retention_days = fields.IntField(default=90)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "project_layers"


class SessionLayer(Model):
    """Session-specific ephemeral state."""
    id = fields.IntField(primary_key=True)
    session = fields.OneToOneField("models.Session", related_name="layer_state", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=255, default="", db_index=True)
    data = fields.JSONField(default=dict)
    active_phase = fields.CharField(max_length=64, default="init")
    investigation_focus = fields.JSONField(default=list)
    current_hypotheses = fields.JSONField(default=list)
    active_monitors = fields.JSONField(default=list)
    analysis_notes = fields.TextField(default="")
    current_threat_level = fields.CharEnumField(Severity, default=Severity.LOW)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "session_layers"
