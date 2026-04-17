"""Generic feed snapshot model for shared intelligence feeds."""

from tortoise import fields
from tortoise.models import Model


class ThreatIntelFeedSnapshot(Model):
    """Generic snapshots for arbitrary intelligence feeds under feeds/."""

    id = fields.IntField(primary_key=True)
    provider = fields.CharField(max_length=64, default="generic", db_index=True)
    feed_name = fields.CharField(max_length=255)
    feed_kind = fields.CharField(max_length=64, default="snapshot", db_index=True)
    snapshot_id = fields.CharField(max_length=64)
    source_file = fields.CharField(max_length=500, unique=True)
    source_url = fields.CharField(max_length=512, default="")
    record_count = fields.IntField(default=0)
    payload = fields.JSONField(default=dict)
    collected_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_feed_snapshots"
        unique_together = (("feed_name", "snapshot_id"),)
        indexes = (("provider",), ("feed_name",), ("feed_kind",), ("snapshot_id",))


