"""Alerts module — notifications for incidents, threats, task completion (Phase 7).

Models:
- AlertRule: Define alert conditions (event type, severity threshold, channels)
- AlertHistory: Log of fired alerts with delivery status per channel
- ChannelConfig: SMTP email, Slack webhook, generic webhook configuration

Alert Dispatcher subscribes to EventStore and fires alerts based on rules.
Multi-channel delivery: email (SMTP), Slack, webhooks.
"""

from tortoise import Model, fields
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"


class AlertRule(Model):
    """Alert rule — trigger condition + notification channels."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="alert_rules",
        on_delete=fields.CASCADE,
    )
    
    # Rule definition
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField(default="")
    is_active = fields.BooleanField(default=True, db_index=True)
    
    # Trigger condition
    event_type = fields.CharField(
        max_length=64,
        db_index=True,
        help_text="DomainEvent.kind to match (e.g., 'incident.created', 'threat.detected')"
    )
    severity_threshold = fields.CharField(
        max_length=16,
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help_text="Only fire for events with severity >= threshold"
    )
    
    # Condition expression (optional JSONPath/CEL filter)
    condition_expr = fields.TextField(
        default="",
        help_text="Optional JSONPath expression for advanced filtering"
    )
    
    # Notification channels
    channels = fields.JSONField(
        default=list,
        help_text="List of channel names to send to (e.g., ['email', 'slack'])"
    )
    
    # Rate limiting
    cooldown_minutes = fields.IntField(
        default=0,
        help_text="Minimum minutes between alerts for same event type"
    )
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "alert_rules"
        unique_together = (("organization", "name"),)


class AlertHistory(Model):
    """History of fired alerts with delivery status per channel."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="alert_history",
        on_delete=fields.CASCADE,
    )
    rule: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.AlertRule",
        related_name="firing_history",
        on_delete=fields.SET_NULL,
        null=True,
    )
    
    # Alert source
    event_id = fields.CharField(max_length=255, db_index=True)
    event_type = fields.CharField(max_length=64)
    event_data = fields.JSONField()
    
    # Delivery status per channel
    delivery_status = fields.JSONField(
        default=dict,
        help_text={
            "email": {"status": "sent|failed", "error": "..."},
            "slack": {"status": "sent|failed", "error": "..."},
        }
    )
    
    # Metadata
    fired_at = fields.DatetimeField(auto_now_add=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "alert_history"
        ordering = ["-fired_at"]
        indexes = [
            fields.Index(["organization", "event_type", "fired_at"]),
            fields.Index(["event_id"]),
        ]


class ChannelConfig(Model):
    """Configuration for alert delivery channels."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="alert_channels",
        on_delete=fields.CASCADE,
    )
    
    # Channel type
    channel_type = fields.CharField(
        max_length=32,
        choices=["email", "slack", "webhook"],
        db_index=True
    )
    
    # Configuration
    config = fields.JSONField(
        help_text={
            "email": {"smtp_host": "...", "smtp_port": 587, "from_address": "..."},
            "slack": {"webhook_url": "...", "channel": "#alerts"},
            "webhook": {"url": "...", "headers": {"Authorization": "Bearer ..."}}
        }
    )
    
    # Status
    is_active = fields.BooleanField(default=True)
    last_test_at = fields.DatetimeField(null=True)
    last_test_status = fields.CharField(max_length=16, null=True)  # success/failed
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "alert_channel_configs"
        unique_together = (("organization", "channel_type"),)


__all__ = [
    "AlertSeverity",
    "AlertChannel",
    "AlertRule",
    "AlertHistory",
    "ChannelConfig",
]
