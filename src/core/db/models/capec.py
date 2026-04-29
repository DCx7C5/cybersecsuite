"""CAPEC attack-pattern intelligence model."""

from tortoise import fields
from tortoise.models import Model


class CapecAttackPatternIntel(Model):
    """Canonical CAPEC attack patterns for detection engineering and threat hunting."""

    id = fields.BigIntField(primary_key=True)
    capec_id = fields.CharField(max_length=32, unique=True, db_index=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField(null=True)
    abstraction = fields.CharField(max_length=64, default="", db_index=True)
    domains = fields.JSONField(default=list)
    prerequisites = fields.JSONField(default=list)
    resources_required = fields.JSONField(default=list)
    skills_required = fields.JSONField(default=list)
    consequences = fields.JSONField(default=list)
    execution_flow = fields.JSONField(default=list)
    example_instances = fields.JSONField(default=list)
    parent_capec_ids = fields.JSONField(default=list)
    child_capec_ids = fields.JSONField(default=list)
    likelihood_of_attack = fields.CharField(max_length=64, default="", db_index=True)
    severity = fields.CharField(max_length=64, default="", db_index=True)
    url = fields.CharField(max_length=512, default="")
    source_file = fields.CharField(max_length=500, null=True)
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_capec_patterns"
        ordering = ["capec_id"]
        indexes = (("capec_id",), ("name",), ("abstraction",), ("severity",))

    def __str__(self):
        return f"{self.capec_id}: {self.name}"

