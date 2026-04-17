#!/usr/bin/env bash
# mcp_commands.sh — Reference script for all kerneldev-mcp CLI commands
# Usage: source or read as reference; execute individual commands as needed.

set -euo pipefail

SESSION_ID="${SESSION_ID:-$(cat /tmp/current_session_id 2>/dev/null || echo 'unknown')}"

echo "=== Module Management ==="
/kerneldev create --template=forensic-sysfs
/kerneldev build --target=all
/kerneldev load --module=detector.ko --verify
/kerneldev unload --module=detector --safe

echo "=== Development Assistance ==="
/kerneldev lint --source=detector.c
/kerneldev test --module=detector --suite=forensic
/kerneldev docs --generate=api

echo "=== Integration Helpers ==="
/kerneldev integrate --with=cybersec-db
/kerneldev deploy --session="$SESSION_ID"
/kerneldev cleanup --remove-test-modules

