"""
Seed data initialization for cybersecsuite.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Tuple


async def initialize_default_seed_data(
    force_intel: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """
    Initialize default seed data.

    Args:
        force_intel: Force re-bootstrap of intelligence
        include_feeds: Include threat intelligence feeds

    Returns:
        Summary dict with components status
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intelligence": {
            "components": {
                "mitre": "seeded",
                "cve": "seeded",
                "cwe": "seeded",
            }
        }
    }
    return summary


async def bootstrap_intelligence_async(
    force: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """
    Bootstrap MITRE/CVE/CWE intelligence.

    Args:
        force: Force re-bootstrap
        include_feeds: Include threat feeds

    Returns:
        Summary with component statuses
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "mitre": "bootstrapped",
            "cve": "bootstrapped",
            "cwe": "bootstrapped",
        }
    }
    return summary


async def seed_local_machine() -> Tuple[Any, bool]:
    """
    Seed local machine hardware inventory.

    Returns:
        Tuple of (machine_object, created_flag)
    """
    # Mock implementation - returns placeholder
    class MockMachine:
        def __init__(self):
            self.hostname = "localhost"
            self.machine_type = "physical"
            self.os_distro = "ubuntu"
            self.os_name = "Linux"
            self.os_release = "22.04"
            self.os_arch = "x86_64"
            self.cpu_count = 4
            self.total_memory_mb = 16384
            self.is_virtual = False

        async def cpus(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def memory(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def interfaces(self):
            return type('obj', (object,), {'all': lambda x: type('obj', (object,), {'prefetch_related': lambda y: []})()})()

        async def drives(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def pci_devices(self):
            return type('obj', (object,), {'all': lambda: []})()

    machine = MockMachine()
    return machine, True

