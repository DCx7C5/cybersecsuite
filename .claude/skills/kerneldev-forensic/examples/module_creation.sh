#!/usr/bin/env bash
# module_creation.sh — Create a new forensic kernel module via kerneldev-mcp
# Usage: bash examples/module_creation.sh [module_name]

set -euo pipefail

MODULE_NAME="${1:-custom_detector}"

echo "[*] Creating new forensic module: $MODULE_NAME"
/kerneldev new-module --template=forensic --name="$MODULE_NAME"

echo "[*] Generating syscall-monitor template into ./modules/"
/kerneldev generate --type=syscall-monitor --output=./modules/

echo "[+] Module scaffold created for: $MODULE_NAME"

