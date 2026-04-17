"""Update the log entry model for intelligence sync history."""

from tortoise import fields
from tortoise.models import Model


class IntelligenceUpdateLogEntry(Model):
    """Parsed update events from update-log.md."""

    id = fields.IntField(primary_key=True)
    run_id = fields.CharField(max_length=32)
    category = fields.CharField(max_length=32)
    status = fields.CharField(max_length=32)
    message = fields.TextField()
    line_number = fields.IntField(null=True)
    source_file = fields.CharField(max_length=500, default="data/cybersec-shared/intelligence/update-log.md")
    logged_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_update_log_entries"
        indexes = (("run_id",), ("category",), ("status",), ("line_number",))

