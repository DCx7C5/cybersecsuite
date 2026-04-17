#!/usr/bin/env bash
# integration_testing.sh — Integration tests for forensic kernel modules
# Usage: bash examples/integration_testing.sh [module_name]

set -euo pipefail

MODULE_NAME="${1:-custom_detector}"
REPO_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"

echo "[*] Running rootkit-scan with module: $MODULE_NAME"
"$REPO_ROOT/commands/rootkit-scan" --kernel-module="$MODULE_NAME"

echo "[*] Running memory-dump with module: $MODULE_NAME"
"$REPO_ROOT/commands/memory-dump" --use-module="$MODULE_NAME"

echo "[*] Verifying database integration..."
python -c "
import asyncio
from tortoise import Tortoise
async def check():
    from db.models import KernelModule
    module = await KernelModule.filter(name='$MODULE_NAME').first()
    print(f'DB record: {module}')
asyncio.run(check())
"

echo "[+] Integration tests completed."

