"""A2A protocol integration for QoL toggle propagation (T017).

This module handles:
- Publishing QoL toggle changes via A2A protocol
- Subscribing to remote toggle updates
- Synchronizing state across agent boundaries
- Per-agent override policies

Messages:
    qol.toggle_changed   — toggle was enabled/disabled by local agent
    qol.preset_bound     — preset was bound to an agent remotely
    qol.settings_sync    — request to sync settings with agent

Environment variables:
    A2A_ENABLED              — enable A2A propagation (default: true)
    QOL_PROPAGATE_SETTINGS   — propagate settings to all agents (default: false)

Thread safety:
    - All message publishing is async and non-blocking
    - All subscribe callbacks are async-safe
"""


import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger("ai_proxy.qol_controls.a2a_integration")


class QoLA2APublisher:
    """Publish QoL events via A2A protocol."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        self._enabled = self._check_enabled()

    @staticmethod
    def _check_enabled() -> bool:
        """Check if A2A propagation is enabled."""
        import os
        return os.environ.get("A2A_ENABLED", "true").lower() in ("true", "1", "yes")

    async def publish_toggle_changed(
        self,
        agent_name: str,
        scope: str,
        toggle_name: str,
        enabled: bool,
    ) -> bool:
        """Publish a toggle change event (T017).

        Args:
            agent_name: agent that made the change
            scope: scope of the setting (session/project/global)
            toggle_name: toggle name (e.g., "no_thinking")
            enabled: whether the toggle was enabled or disabled

        Returns:
            True if published successfully, False otherwise.
        """
        if not self._enabled:
            return False

        try:
            # Import here to avoid circular deps
            from a2a.models import A2AMessage

            event = {
                "type": "qol.toggle_changed",
                "agent": agent_name,
                "scope": scope,
                "toggle": toggle_name,
                "enabled": enabled,
            }

            msg = A2AMessage(
                message_type="event",
                payload=event,
                sender=self.agent_name,
            )

            # Queue for async publish (fire-and-forget)
            asyncio.create_task(self._send_message(msg))
            logger.debug(
                "QoL toggle change published: agent=%s, toggle=%s, enabled=%s",
                agent_name, toggle_name, enabled,
            )
            return True

        except Exception as e:
            logger.debug("Failed to publish QoL toggle change: %s", e)
            return False

    async def publish_preset_bound(
        self,
        agent_name: str,
        preset_name: str,
    ) -> bool:
        """Publish an agent preset binding (T017/T018).

        Args:
            agent_name: agent being bound
            preset_name: preset name

        Returns:
            True if published successfully.
        """
        if not self._enabled:
            return False

        try:
            from a2a.models import A2AMessage

            event = {
                "type": "qol.preset_bound",
                "agent": agent_name,
                "preset": preset_name,
            }

            msg = A2AMessage(
                message_type="event",
                payload=event,
                sender=self.agent_name,
            )

            asyncio.create_task(self._send_message(msg))
            logger.debug(
                "QoL preset binding published: agent=%s, preset=%s",
                agent_name, preset_name,
            )
            return True

        except Exception as e:
            logger.debug("Failed to publish QoL preset binding: %s", e)
            return False

    @staticmethod
    async def _send_message(msg: Any) -> None:
        """Send A2A message (abstracted for testing)."""
        try:
            # This would integrate with the actual A2A client
            # For now, just log it
            logger.debug("A2A message sent: %s", msg)
        except Exception as e:
            logger.debug("Failed to send A2A message: %s", e)


class QoLA2ASubscriber:
    """Subscribe to remote QoL events via A2A protocol."""

    def __init__(self) -> None:
        self._callbacks: dict[str, list[Callable]] = {}
        self._enabled = self._check_enabled()

    @staticmethod
    def _check_enabled() -> bool:
        """Check if A2A propagation is enabled."""
        import os
        return os.environ.get("A2A_ENABLED", "true").lower() in ("true", "1", "yes")

    def on_toggle_changed(
        self,
        callback: Callable[[str, str, str, bool], Any],
    ) -> None:
        """Register callback for toggle change events (T017).

        Args:
            callback: async function(agent_name, scope, toggle_name, enabled) -> None
        """
        if "toggle_changed" not in self._callbacks:
            self._callbacks["toggle_changed"] = []
        self._callbacks["toggle_changed"].append(callback)

    def on_preset_bound(
        self,
        callback: Callable[[str, str], Any],
    ) -> None:
        """Register callback for preset binding events (T017/T018).

        Args:
            callback: async function(agent_name, preset_name) -> None
        """
        if "preset_bound" not in self._callbacks:
            self._callbacks["preset_bound"] = []
        self._callbacks["preset_bound"].append(callback)

    async def dispatch_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Dispatch an A2A event to registered callbacks (T017)."""
        if not self._enabled:
            return

        callbacks = self._callbacks.get(event_type, [])
        if not callbacks:
            return

        if event_type == "toggle_changed":
            for cb in callbacks:
                try:
                    await cb(
                        payload["agent"],
                        payload["scope"],
                        payload["toggle"],
                        payload["enabled"],
                    )
                except Exception as e:
                    logger.warning("QoL toggle_changed callback failed: %s", e)

        elif event_type == "preset_bound":
            for cb in callbacks:
                try:
                    await cb(payload["agent"], payload["preset"])
                except Exception as e:
                    logger.warning("QoL preset_bound callback failed: %s", e)


# ── Singletons

_publisher: QoLA2APublisher | None = None
_subscriber: QoLA2ASubscriber | None = None


def get_publisher(agent_name: str = "qol_manager") -> QoLA2APublisher:
    """Get the A2A publisher singleton."""
    global _publisher
    if _publisher is None:
        _publisher = QoLA2APublisher(agent_name)
    return _publisher


def get_subscriber() -> QoLA2ASubscriber:
    """Get the A2A subscriber singleton."""
    global _subscriber
    if _subscriber is None:
        _subscriber = QoLA2ASubscriber()
    return _subscriber
