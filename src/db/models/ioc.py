"""
Forensic IOC models — IOCEntry, watchlist, cleared items.
"""
from tortoise.models import Model
from tortoise import fields
from db.models.enums import (
    IOCType, SeverityLevel, ConfidenceLevel, ForensicIOCStatus,
)


class IOCEntry(Model):
    """Indicators of Compromise with full forensic context."""
    id = fields.IntField(primary_key=True)
    workspace = fields.ForeignKeyField("models.Workspace", related_name="ioc_entries", null=True, on_delete=fields.SET_NULL)
    ioc_id = fields.CharField(max_length=50, unique=True, db_index=True, null=True)
    project = fields.ForeignKeyField("models.ForensicProject", related_name="iocs", db_index=True, null=True, on_delete=fields.SET_NULL)
    ioc_type = fields.CharEnumField(IOCType, db_index=True)
    value = fields.CharField(max_length=2000, db_index=True)
    context = fields.TextField(null=True)
    first_session = fields.ForeignKeyField("models.ForensicSession", related_name="first_iocs", db_index=True, null=True, on_delete=fields.SET_NULL)
    last_session = fields.ForeignKeyField("models.ForensicSession", related_name="last_iocs", null=True)
    sightings = fields.IntField(default=1)
    confidence = fields.CharEnumField(ConfidenceLevel, db_index=True, null=True)
    status = fields.CharEnumField(ForensicIOCStatus, default=ForensicIOCStatus.ACTIVE, db_index=True)
    severity = fields.CharEnumField(SeverityLevel, db_index=True, null=True)
    first_observed = fields.DatetimeField(auto_now_add=True)
    last_observed = fields.DatetimeField(auto_now=True)
    source = fields.CharField(max_length=256, default="", description="Discovery source (tool/agent).")
    tlp = fields.CharField(max_length=16, default="", description="TLP marking.")
    mitre_techniques = fields.JSONField(default=list)
    mitre_tactics = fields.JSONField(default=list)
    evasion_techniques = fields.JSONField(default=list)
    steganography_indicators = fields.JSONField(default=list)
    obfuscation_methods = fields.JSONField(default=list)
    extraction_method = fields.CharField(max_length=255, null=True)
    hash_verification = fields.CharField(max_length=128, null=True, description="SHA-256 hash of evidence.")
    chain_of_custody = fields.JSONField(default=dict)
    related_ioc_ids = fields.JSONField(default=list, description="Cross-referencing related IOC IDs.")
    tags = fields.JSONField(default=list)
    notes = fields.TextField(default="")
    # Link to canonical IOC intelligence database entry
    intel_match = fields.ForeignKeyField(
        "models.IOCDatabaseEntry",
        related_name="forensic_ioc_matches",
        null=True,
        on_delete=fields.SET_NULL,
        description="Matching canonical IOC from the intelligence database.",
    )

    class Meta:
        table = "ioc_entries"
        ordering = ["-last_observed"]
        indexes = [
            ("project", "ioc_type"),
            ("project", "status"),
            ("project", "severity"),
            ("ioc_type", "value"),
        ]

    def __str__(self):
        return f"IOC({self.ioc_type}: {self.value[:60]})"


class ForensicWatchlistItem(Model):
    """Items under active monitoring (forensic extension)."""
    id = fields.IntField(primary_key=True)
    watchlist_id = fields.CharField(max_length=50, unique=True, db_index=True)
    project = fields.ForeignKeyField("models.ForensicProject", related_name="watchlist", db_index=True)
    item_type = fields.CharEnumField(IOCType, db_index=True)
    value = fields.CharField(max_length=2000)
    pattern = fields.CharField(max_length=2000, null=True, description="Regex or glob pattern.")
    reason = fields.TextField()
    priority = fields.CharEnumField(SeverityLevel, db_index=True)
    added_by_session = fields.ForeignKeyField("models.ForensicSession", related_name="watchlist_additions")
    last_checked_session = fields.ForeignKeyField("models.ForensicSession", related_name="watchlist_checks", null=True)
    clean_checks = fields.IntField(default=0)
    status = fields.CharEnumField(ForensicIOCStatus, default=ForensicIOCStatus.WATCHING, db_index=True)
    escalated_to_ioc = fields.ForeignKeyField("models.IOCEntry", related_name="watchlist_origin", null=True)
    expires_at = fields.DatetimeField(null=True, description="Auto-remove after this date.")
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_checked = fields.DatetimeField(null=True)

    class Meta:
        table = "forensic_watchlist_items"
        ordering = ["-priority", "-created_at"]
        indexes = [
            ("project", "item_type"),
            ("project", "status"),
        ]

    def __str__(self):
        return f"Watch({self.item_type}: {self.value[:60]})"


class ClearedItem(Model):
    """Confirmed false positives and known-good items."""
    id = fields.IntField(primary_key=True)
    cleared_id = fields.CharField(max_length=50, unique=True, db_index=True)
    project = fields.ForeignKeyField("models.ForensicProject", related_name="cleared_items", db_index=True)
    item_type = fields.CharEnumField(IOCType, db_index=True)
    value = fields.CharField(max_length=2000)
    reason_cleared = fields.TextField()
    recheck_condition = fields.CharField(max_length=500, null=True, description="Condition to re-trigger review.")
    cleared_by_session = fields.ForeignKeyField("models.ForensicSession", related_name="cleared_items")
    cleared_by_investigator = fields.CharField(max_length=255, default="")
    clean_checks_before_clearing = fields.IntField(default=3)
    date_cleared = fields.DatetimeField(auto_now_add=True)
    review_date = fields.DatetimeField(null=True, description="Scheduled date to re-review.")
    original_watchlist = fields.ForeignKeyField("models.ForensicWatchlistItem", related_name="cleared_item", null=True)
    original_ioc = fields.ForeignKeyField("models.IOCEntry", related_name="cleared_items", null=True)
    tags = fields.JSONField(default=list)

    class Meta:
        table = "cleared_items"
        ordering = ["-date_cleared"]
        indexes = [
            ("project", "item_type"),
        ]

    def __str__(self):
        return f"Cleared({self.item_type}: {self.value[:60]})"
