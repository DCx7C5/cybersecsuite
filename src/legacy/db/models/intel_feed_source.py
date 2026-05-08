"""Intelligence feed source management."""
from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField, UrlField


class IntelFeedSource(BaseModel):
    """A managed intelligence feed source (RSS, ATOM, JSON, or HTML scrape)."""

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=255)
    url = UrlField(max_length=2048, unique=True)
    feed_type = fields.CharField(max_length=32, default="rss")  # rss | atom | json | html
    category = fields.CharField(max_length=64, default="general")  # threat | vuln | news | apt | general
    is_active = fields.BooleanField(default=True)
    last_fetched_at = fields.DatetimeField(null=True)
    description = DescriptionField(max_length=512, default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_feed_sources"
        ordering = ["name"]
