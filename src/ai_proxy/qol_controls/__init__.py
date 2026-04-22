"""QoL Output Controls — server-side injection of output behaviour fragments.

Provides:
    - QoLToggle / QoLSettings models  (models.py)
    - Prompt fragments               (prompts.py)
    - Manager: build + inject        (manager.py)
"""
from __future__ import annotations

from ai_proxy.qol_controls.models import QoLToggle, QoLSettings
from ai_proxy.qol_controls.manager import QoLManager, get_manager

__all__ = ["QoLToggle", "QoLSettings", "QoLManager", "get_manager"]
