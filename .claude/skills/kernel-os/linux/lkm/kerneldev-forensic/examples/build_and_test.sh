#!/usr/bin/env bash
# build_and_test.sh — Build, load, and monitor a forensic kernel module
# Usage: bash examples/build_and_test.sh [module_name]

set -euo pipefail

MODULE_NAME="${1:-custom_detector}"

echo "[*] Building module with kerneldev-mcp (debug mode)..."
/kerneldev build --module="${MODULE_NAME}.c" --debug

echo "[*] Loading module in test mode..."
/kerneldev load --module="${MODULE_NAME}.ko" --test-mode

echo "[*] Monitoring module status via sysfs (Ctrl+C to stop)..."
watch -n 1 "cat /sys/kernel/${MODULE_NAME}/status"

