"""
Defense models — anti-forensic techniques and hardening recommendations.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import Severity, Confidence


class AntiForensicTechnique(Model):
    """Detected anti-forensic or evasion technique."""
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField("models.Session", related_name="anti_forensic_techniques", db_index=True, null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=255, db_index=True)
    category = fields.CharField(max_length=100, db_index=True, default="")
    severity = fields.CharEnumField(Severity, db_index=True, null=True)
    confidence = fields.CharEnumField(Confidence, db_index=True, null=True)
    description = fields.TextField(default="")
    mitre_technique_id = fields.CharField(max_length=32, default="", db_index=True)
    indicators = fields.JSONField(default=list)
    detection_methods = fields.JSONField(default=list)
    mitigation_strategies = fields.JSONField(default=list)
    detected_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "anti_forensic_techniques"


class HardeningRecommendation(Model):
    """Hardening recommendation for the system."""
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField("models.Session", related_name="hardening_recommendations", db_index=True, null=True, on_delete=fields.SET_NULL)
    title = fields.CharField(max_length=255)
    category = fields.CharField(max_length=100, default="")
    priority = fields.CharEnumField(Severity, db_index=True)
    description = fields.TextField(default="")
    implementation_steps = fields.JSONField(default=list)
    current_risk = fields.CharEnumField(Severity, null=True)
    residual_risk = fields.CharEnumField(Severity, null=True)
    mitre_technique_id = fields.CharField(max_length=32, default="", db_index=True)
    implementation_status = fields.CharField(max_length=50, default="pending")
    implemented_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "hardening_recommendations"
