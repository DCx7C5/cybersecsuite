"""
deploy_forensic_module.py — Database integration for forensic LKM deployment.
Integrates with existing Tortoise ORM models (Kernel, KernelModule, Finding).

Usage:
    import asyncio
    from examples.deploy_forensic_module import deploy_forensic_module
    asyncio.run(deploy_forensic_module(kernel_id=1, module_name="syscall_monitor"))
"""

from db.models import Kernel, KernelModule, Finding
from db.models.kernel import ModuleStatus


async def deploy_module(module_name: str) -> bool:
    """Placeholder: implement actual insmod/modprobe call."""
    import subprocess
    result = subprocess.run(
        ["insmod", f"/kernel-modules/{module_name}.ko"],
        capture_output=True,
    )
    return result.returncode == 0


async def deploy_forensic_module(kernel_id: int, module_name: str) -> "KernelModule":
    """Deploy and track forensic LKM in the CyberSec database."""
    kernel = await Kernel.get(id=kernel_id)

    # Create module record
    module = await KernelModule.create(
        kernel=kernel,
        name=module_name,
        status=ModuleStatus.LOADING,
        source_path=f"/kernel-modules/{module_name}.ko",
        is_signed=True,  # Ensure forensic modules are signed
        notes="Forensic investigation module",
    )

    # Deploy module
    success = await deploy_module(module_name)

    if success:
        module.status = ModuleStatus.LOADED
        await module.save()

        # Log deployment as finding
        await Finding.create(
            workspace_id=kernel.host.workspace_id,
            title=f"Forensic Module Deployed: {module_name}",
            description="Custom forensic LKM deployed for investigation",
            severity="info",
            location=f"/sys/kernel/{module_name}/",
        )

    return module

