#!/usr/bin/env bash
# scenario_rootkit_detection.sh — Scenario 2: Rootkit Detection Campaign
# Deploy advanced rootkit scanner with deep scan mode and real-time alerts via sysfs.

set -euo pipefail

echo "[*] Loading advanced rootkit scanner module..."
/kerneldev load --module=advanced_rootkit_scanner.ko --verify

echo "[*] Configuring deep scan depth..."
echo "deep" > /sys/kernel/advanced_rootkit_scanner/scan_depth

echo "[*] Enabling real-time alerts via sysfs..."
echo "1" > /sys/kernel/advanced_rootkit_scanner/enable_alerts

echo "[+] Rootkit scanner active. Monitor alerts with:"
echo "    watch -n 1 'cat /sys/kernel/forensic_mcp/alerts'"
watch -n 1 'cat /sys/kernel/forensic_mcp/alerts'

