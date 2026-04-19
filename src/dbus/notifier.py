"""DBus notifier backend for desktop notifications and signals."""
from __future__ import annotations

import asyncio
import subprocess
import sys
from typing import Any

if sys.platform == "linux":
    try:
        from dbus_next.aio import MessageBus
        from dbus_next import Message
        _DBUS_NEXT_AVAILABLE = True
    except ImportError:
        _DBUS_NEXT_AVAILABLE = False
else:
    _DBUS_NEXT_AVAILABLE = False


class DbusNotifier:
    """Async DBus notifier with fallback to subprocess."""

    def __init__(self) -> None:
        self._bus: MessageBus | None = None
        self._available: bool | None = None

    async def is_available(self) -> bool:
        """Check if DBus session bus is available."""
        if self._available is not None:
            return self._available

        if not _DBUS_NEXT_AVAILABLE:
            # Try subprocess fallback
            try:
                result = await asyncio.create_subprocess_exec(
                    "notify-send", "--version",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await result.wait()
                self._available = result.returncode == 0
            except (OSError, FileNotFoundError):
                self._available = False
        else:
            # Try dbus-next
            try:
                self._bus = MessageBus()
                await self._bus.connect()
                self._available = True
            except Exception:
                self._available = False

        return self._available

    async def notify(
        self,
        title: str,
        body: str = "",
        icon: str = "dialog-information",
        urgency: int = 1,
    ) -> int:
        """Send desktop notification. Returns notification ID or -1 on failure."""
        if not await self.is_available():
            print(f"DBus not available, skipping notification: {title}", file=sys.stderr)
            return -1

        if _DBUS_NEXT_AVAILABLE and self._bus:
            # Use dbus-next
            try:
                reply = await self._bus.call(
                    Message(
                        destination="org.freedesktop.Notifications",
                        path="/org/freedesktop/Notifications",
                        interface="org.freedesktop.Notifications",
                        member="Notify",
                        signature="susssasa{sv}i",
                        body=[
                            "CyberSecSuite",  # app_name
                            0,  # replaces_id
                            icon,  # app_icon
                            title,  # summary
                            body,  # body
                            [],  # actions
                            {},  # hints
                            -1,  # expire_timeout
                        ],
                    )
                )
                return reply.body[0] if reply.body else -1
            except Exception as e:
                print(f"DBus notification failed: {e}", file=sys.stderr)
                return -1
        else:
            # Subprocess fallback
            try:
                cmd = ["notify-send", title, body, f"--icon={icon}", f"--urgency={urgency}"]
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await result.wait()
                return 0 if result.returncode == 0 else -1
            except (OSError, FileNotFoundError) as e:
                print(f"notify-send failed: {e}", file=sys.stderr)
                return -1

    async def emit_signal(self, signal_name: str, args: list[Any]) -> None:
        """Emit custom signal on io.cybersecsuite.Agent bus."""
        if not await self.is_available() or not _DBUS_NEXT_AVAILABLE or not self._bus:
            return

        try:
            # This is a simplified implementation - real implementation would need
            # to register the bus name and interface first
            await self._bus.send(
                Message(
                    path="/io/cybersecsuite/Agent",
                    interface="io.cybersecsuite.Agent",
                    member=signal_name,
                    signature="",  # Would need proper signature for args
                    body=args,
                )
            )
        except Exception as e:
            print(f"DBus signal emission failed: {e}", file=sys.stderr)


# Global singleton
_notifier: DbusNotifier | None = None


def get_notifier() -> DbusNotifier:
    """Get the global DbusNotifier instance."""
    global _notifier
    if _notifier is None:
        _notifier = DbusNotifier()
    return _notifier
