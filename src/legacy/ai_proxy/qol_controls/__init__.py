"""QoL Output Controls — server-side injection of output behaviour fragments.

Provides:
    - QoLToggle / QoLSettings models  (models.py)
    - Prompt fragments               (prompts.py)
    - Manager: build + inject        (manager.py)
"""


from ai_proxy.qol_controls.models import QoLToggle, QoLSettings, QoLSecurityError, validate_toggle_combo
from ai_proxy.qol_controls.manager import QoLManager, get_manager

__all__ = ["QoLToggle", "QoLSettings", "QoLSecurityError", "validate_toggle_combo", "QoLManager", "get_manager"]
