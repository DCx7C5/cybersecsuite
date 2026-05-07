"""Threat Intelligence module — IOC tracking (Phase 7)."""

from tortoise import Model, fields
from datetime import datetime
from enum import Enum


class IOCType(str, Enum):
    """Indicator of Compromise types."""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    REGISTRY_KEY = "registry_key"
    USER_AGENT = "user_agent"


class ThreatLevel(str, Enum):
    """IOC threat level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IOC(Model):
    """Indicator of Compromise."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
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
    description = fields.TextField(default="")
    tags = fields.JSONField(default=list)
    threat_actors = fields.JSONField(default=list)
    
    # Timeline
    first_seen_at = fields.DatetimeField()
    last_seen_at = fields.DatetimeField()
    
    # Status
    is_active = fields.BooleanField(default=True, db_index=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "iocs"
        unique_together = (("organization", "ioc_type", "value"),)


class ThreatFeed(Model):
    """External threat feed integration."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="threat_feeds",
        on_delete=fields.CASCADE,
    )
    
    name = fields.CharField(max_length=256)
    feed_url = fields.CharField(max_length=512)
    feed_type = fields.CharField(
        max_length=32,
        choices=["misp", "otx", "virustotal", "custom"],
    )
    
    is_active = fields.BooleanField(default=True)
    last_synced_at = fields.DatetimeField(null=True)
    sync_interval_hours = fields.IntField(default=24)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "threat_feeds"
        unique_together = (("organization", "name"),)


class IOCMatch(Model):
    """Record of IOC matched against observables."""
    
    id = fields.BigIntField(primary_key=True)
    ioc: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.IOC",
        related_name="matches",
        on_delete=fields.CASCADE,
    )
    
    observable = fields.CharField(max_length=512)
    observable_type = fields.CharField(max_length=32)
    
    source = fields.CharField(
        max_length=64,
        help_text="Where observable came from (log, scan, etc.)"
    )
    
    match_confidence = fields.FloatField(default=1.0)
    
    matched_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "ioc_matches"


__all__ = [
    "IOCType",
    "ThreatLevel",
    "IOC",
    "ThreatFeed",
    "IOCMatch",
]
