"""Alerts module — multi-channel alert dispatch (Phase 7)."""

from .enums import AlertSeverity, AlertChannel, DeliveryStatus
from .models import (
    AlertRule,
    AlertHistory,
    ChannelConfig,
)
from .dispatcher import AlertDispatcher
from .endpoints import router
