"""Threat Intelligence module — IOC tracking (Phase 7)."""

from tortoise import fields
from css.core.db.fields import DescriptionField, QualityScoreField, UrlField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .enums import IOCType, ThreatLevel


class IOC(BaseModel, TimestampMixin):
    """Indicator of Compromise."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="iocs",
        on_delete=fields.CASCADE,
    )
    
    # IOC data
    ioc_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in IOCType],
        db_index=True,
    )
    value = fields.CharField(max_length=512, db_index=True)
    
    # Threat classification
    threat_level = fields.CharField(
        max_length=16,
        choices=[t.value for t in ThreatLevel],
        default="medium",
        db_index=True,
    )
    
    # Source
    source = fields.CharField(
        max_length=256,
        help_text="Where IOC came from (feed name, report, etc.)"
    )
    
    # Context
    description = DescriptionField(default="")
    tags = fields.JSONField(default=list)
    threat_actors = fields.JSONField(default=list)
    
    # Timeline
    first_seen_at = fields.DatetimeField()
    last_seen_at = fields.DatetimeField()
    
    # Status
    is_active = fields.BooleanField(default=True, db_index=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "iocs"
        unique_together = (("organization_id", "ioc_type", "value"),)


class ThreatFeed(BaseModel):
    """External threat feed integration."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="threat_feeds",
        on_delete=fields.CASCADE,
    )
    
    name = fields.CharField(max_length=256)
    feed_url = UrlField(max_length=512)
    feed_type = fields.CharField(
        max_length=32,
        choices=["misp", "otx", "virustotal", "custom"],
    )
    
    is_active = fields.BooleanField(default=True)
    last_synced_at = fields.DatetimeField(null=True)
    sync_interval_hours = fields.IntField(default=24)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "threat_feeds"
        unique_together = (("organization_id", "name"),)


class IOCMatch(BaseModel):
    """Record of IOC matched against observables."""

    ioc: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.IOC",
        related_name="matches",
        on_delete=fields.CASCADE,
    )
    
    observable = fields.CharField(max_length=512)
    observable_type = fields.CharField(max_length=32)
    
    source = fields.CharField(
        max_length=64,
        help_text="Where observable came from (log, scan, etc.)"
    )
    
    match_confidence = QualityScoreField(default=1.0)
    
    matched_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "ioc_matches"

