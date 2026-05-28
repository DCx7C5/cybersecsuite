"""Outbound webhook module for SIEM/Slack/PagerDuty integrations."""

from .models import WebhookDelivery, WebhookEndpoint
from .dispatcher import WebhookDispatcher
from .endpoints import router
