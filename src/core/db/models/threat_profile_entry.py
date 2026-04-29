"""Threat profile entry model from shared intelligence markdown."""

from tortoise import fields
from tortoise.models import Model


class ThreatProfileEntry(Model):
    """Structured threat profiles from threat-profile.md."""

    id = fields.BigIntField(primary_key=True)
    profile_name = fields.CharField(max_length=255, unique=True)
    actor = fields.ForeignKeyField("models.MitreThreatActorIntel", related_name="profiles", null=True)
    summary = fields.TextField(null=True)
    motivations = fields.JSONField(default=list)
    sectors = fields.JSONField(default=list)
    regions = fields.JSONField(default=list)
    ttps = fields.JSONField(default=list)
    confidence_score = fields.FloatField(null=True)
    source_file = fields.CharField(max_length=500, default="data/cybersec-shared/intelligence/threat-profile.md")
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_threat_profile_entries"
        table_description_plural = "Threat Profile Entries"
        table_description_singular = "Threat Profile Entry"
        indexes = (("profile_name",),)


