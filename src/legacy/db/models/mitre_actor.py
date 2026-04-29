"""MITRE threat actor intelligence model."""

from tortoise import fields
from tortoise.models import Model


class MitreThreatActorIntel(Model):
    """MITRE ATT&CK threat actor/group catalog from shared actor snapshots."""

    id = fields.BigIntField(primary_key=True)
    actor_name = fields.CharField(max_length=255, unique=True, db_index=True)
    description = fields.TextField(null=True)
    aliases = fields.JSONField(default=list, description="Known alternative names.")
    country_of_origin = fields.CharField(max_length=3, default="", description="ISO 3166-1 alpha-2.")
    motivation = fields.CharField(max_length=128, default="", description="Financial, espionage, …")
    first_seen = fields.DatetimeField(null=True, description="First known activity.")
    last_seen = fields.DatetimeField(null=True, description="Most recent known activity.")
    target_sectors = fields.JSONField(default=list, description="Targeted industry sectors.")
    target_regions = fields.JSONField(default=list, description="Targeted geographic regions.")
    associated_groups = fields.JSONField(default=list, description="Related group IDs/names.")
    tools_used = fields.JSONField(default=list, description="Known tools and malware families.")
    url = fields.CharField(max_length=512, default="", description="ATT&CK actor URL.")
    source_file = fields.CharField(max_length=500, null=True)
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_mitre_threat_actors"
        ordering = ["actor_name"]
        indexes = (("actor_name",), ("country_of_origin",), ("motivation",))

    def __str__(self):
        return self.actor_name
