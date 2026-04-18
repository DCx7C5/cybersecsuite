"""Browser forensic finding model."""
from tortoise import fields
from tortoise.models import Model


class BrowserForensicFinding(Model):
    """Single forensic finding produced by the browser-hunt skill."""

    id = fields.IntField(primary_key=True)
    severity = fields.CharField(max_length=32, db_index=True)
    title = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField()
    source = fields.CharField(max_length=128, default="browser-hunt", db_index=True)
    evidence = fields.JSONField(default=list)
    browser = fields.CharField(max_length=64, default="", db_index=True)
    timestamp = fields.DatetimeField(db_index=True)

    class Meta:
        table = "browser_forensic_findings"
        ordering = ["-timestamp"]
        indexes = [
            ("browser", "severity"),
            ("browser", "title"),
        ]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.browser}: {self.title}"
