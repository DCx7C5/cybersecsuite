"""Alert dispatcher — sends alerts via multiple channels (email, Slack, webhooks)."""

from css.core.logger import getLogger
import asyncio
from typing import Dict
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from .enums import DeliveryStatus

logger = getLogger(__name__)


class AlertDispatcher:
    """Dispatch alerts via multiple channels (email, Slack, webhooks)."""
    
    def __init__(self, event_store, channel_configs: Dict):
        """
        Args:
            event_store: DomainEvent store for subscribing to events
            channel_configs: Dict of {"email": {...}, "slack": {...}, "webhook": {...}}
        """
        self.event_store = event_store
        self.channel_configs = channel_configs
        self.cooldown_tracker: Dict[str, datetime] = {}
    
    async def evaluate_and_dispatch(
        self,
        rule,
        event_data: Dict,
    ) -> Dict[str, Dict]:
        """
        Evaluate rule against event and dispatch to configured channels.
        
        Args:
            rule: AlertRule model instance
            event_data: DomainEvent data
        
        Returns:
            {"email": {"status": "sent"}, "slack": {"status": "failed", "error": "..."}}
        """
        # Check cooldown
        cooldown_key = f"{rule.id}:{event_data['kind']}"
        if not self._is_cooled_down(cooldown_key, rule.cooldown_minutes):
            logger.info(f"Alert {rule.id} on cooldown, skipping")
            return {ch: {"status": "skipped", "reason": "cooldown"} for ch in rule.channels}
        
        # Evaluate condition expression if present
        if rule.condition_expr and not self._evaluate_condition(rule.condition_expr, event_data):
            logger.debug(f"Alert {rule.id} condition not met")
            return {ch: {"status": "skipped", "reason": "condition"} for ch in rule.channels}
        
        # Check severity threshold
        if not self._check_severity(event_data.get("severity", "low"), rule.severity_threshold):
            logger.debug(f"Alert {rule.id} severity below threshold")
            return {ch: {"status": "skipped", "reason": "severity"} for ch in rule.channels}
        
        # Dispatch to each channel
        results = {}
        for channel in rule.channels:
            try:
                status = await self._dispatch_to_channel(channel, rule, event_data)
                results[channel] = status
            except Exception as e:
                logger.exception(f"Failed to dispatch to {channel}: {e}")
                results[channel] = {"status": "failed", "error": str(e)}
        
        # Update cooldown
        self.cooldown_tracker[cooldown_key] = datetime.utcnow()
        
        return results
    
    async def _dispatch_to_channel(
        self,
        channel: str,
        rule,
        event_data: Dict,
    ) -> Dict:
        """Dispatch to specific channel."""
        if channel == "email":
            return await self._send_email(rule, event_data)
        elif channel == "slack":
            return await self._send_slack(rule, event_data)
        elif channel == "webhook":
            return await self._send_webhook(rule, event_data)
        else:
            return {"status": "failed", "error": f"Unknown channel: {channel}"}
    
    async def _send_email(self, rule, event_data: Dict) -> Dict:
        """Send email via SMTP."""
        config = self.channel_configs.get("email")
        if not config:
            return {"status": "failed", "error": "Email config not found"}
        
        try:
            # Build email
            subject = f"[{event_data.get('severity', 'info').upper()}] {rule.name}"
            body = self._format_alert_body(rule, event_data)
            
            # Send via SMTP (non-blocking in production; using threading here)
            await asyncio.to_thread(
                self._send_smtp,
                config,
                subject,
                body,
            )
            
            logger.info(f"Email alert sent for rule {rule.id}")
            return {"status": "sent"}
        
        except Exception as e:
            logger.exception(f"Email send failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _send_smtp(self, config: Dict, subject: str, body: str):
        """Send email via SMTP (blocking)."""
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = config.get("from_address", "alerts@cybersecsuite.local")
        msg["To"] = ", ".join(config.get("recipients", []))
        msg.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(config["smtp_host"], config.get("smtp_port", 587)) as server:
            if config.get("use_tls", True):
                server.starttls()
            if config.get("username"):
                server.login(config["username"], config["password"])
            server.send_message(msg)
    
    async def _send_slack(self, rule, event_data: Dict) -> Dict:
        """Send alert to Slack webhook."""
        config = self.channel_configs.get("slack")
        if not config or "webhook_url" not in config:
            return {"status": "failed", "error": "Slack webhook not configured"}
        
        try:
            payload = {
                "text": f"*{rule.name}* — {event_data.get('description', 'Alert')}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"🚨 {rule.name}"},
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Severity:*\n{event_data.get('severity', 'unknown')}"},
                            {"type": "mrkdwn", "text": f"*Event:*\n{event_data.get('kind', 'unknown')}"},
                        ],
                    },
                    {"type": "section", "text": {"type": "mrkdwn", "text": event_data.get('description', '')}},
                ],
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(config["webhook_url"], json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return {"status": "failed", "error": f"HTTP {resp.status}"}
            
            logger.info(f"Slack alert sent for rule {rule.id}")
            return {"status": "sent"}
        
        except Exception as e:
            logger.exception(f"Slack send failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _send_webhook(self, rule, event_data: Dict) -> Dict:
        """Send alert to generic webhook."""
        config = self.channel_configs.get("webhook")
        if not config or "url" not in config:
            return {"status": "failed", "error": "Webhook URL not configured"}
        
        try:
            payload = {
                "rule_id": rule.id,
                "rule_name": rule.name,
                "event": event_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            headers = config.get("headers", {})
            async with aiohttp.ClientSession() as session:
                async with session.post(config["url"], json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status not in (200, 201, 202, 204):
                        return {"status": "failed", "error": f"HTTP {resp.status}"}
            
            logger.info(f"Webhook alert sent for rule {rule.id}")
            return {"status": "sent"}
        
        except Exception as e:
            logger.exception(f"Webhook send failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _format_alert_body(self, rule, event_data: Dict) -> str:
        """Format alert as HTML email body."""
        return f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #d32f2f;">{rule.name}</h2>
    <p><strong>Severity:</strong> {event_data.get('severity', 'unknown').upper()}</p>
    <p><strong>Event Type:</strong> {event_data.get('kind', 'unknown')}</p>
    <p><strong>Time:</strong> {datetime.utcnow().isoformat()}</p>
    <hr>
    <p><strong>Description:</strong></p>
    <pre>{event_data.get('description', '')}</pre>
    <hr>
    <p><strong>Details:</strong></p>
    <pre>{str(event_data)}</pre>
  </body>
</html>
"""
    
    def _is_cooled_down(self, key: str, cooldown_minutes: int) -> bool:
        """Check if cooldown period has elapsed."""
        if cooldown_minutes <= 0:
            return True
        
        last_fire = self.cooldown_tracker.get(key)
        if not last_fire:
            return True
        
        elapsed = (datetime.utcnow() - last_fire).total_seconds() / 60
        return elapsed >= cooldown_minutes
    
    def _check_severity(self, event_severity: str, threshold: str) -> bool:
        """Check if event severity meets threshold."""
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        event_level = severity_levels.get(event_severity.lower(), 0)
        threshold_level = severity_levels.get(threshold.lower(), 2)
        return event_level >= threshold_level
    
    def _evaluate_condition(self, expr: str, data: Dict) -> bool:
        """
        Evaluate JSONPath or simple condition expression.
        
        Simple syntax: "$.field == 'value'" or "$.nested.value > 5"
        """
        try:
            # Very basic JSONPath-like evaluation (production should use jsonpath-ng or similar)
            if "==" in expr:
                left, right = expr.split("==")
                left = left.strip()
                right = right.strip().strip("'\"")
                
                # Extract field value from data
                field = left.replace("$.", "")
                value = data.get(field)
                return str(value) == right
            
            return True  # No condition means always true
        
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return True


__all__ = [
    "DeliveryStatus",
    "AlertDispatcher",
]
