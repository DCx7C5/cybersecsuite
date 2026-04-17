#!/usr/bin/env bash
# debug.sh — Debug helpers for forensic kernel modules
# Usage: bash scripts/debug.sh [module_name]

MODULE="${1:-forensic}"

echo "=== Loaded Modules (filter: $MODULE) ==="
cat /proc/modules | grep "$MODULE" || echo "(none found)"

echo ""
echo "=== lsmod (filter: detector) ==="
lsmod | grep detector || echo "(none found)"

echo ""
echo "=== Kernel Messages (last 50 lines, filter: forensic) ==="
dmesg | tail -50 | grep -i forensic || echo "(no forensic messages)"

echo ""
echo "=== Sysfs Forensic Interfaces ==="
ls -la /sys/kernel/forensic_*/ 2>/dev/null || echo "(no sysfs forensic interfaces found)"

