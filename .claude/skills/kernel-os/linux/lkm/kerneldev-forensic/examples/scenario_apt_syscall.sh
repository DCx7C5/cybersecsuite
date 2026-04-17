#!/usr/bin/env bash
# scenario_apt_syscall.sh — Scenario 1: APT Syscall Analysis
# Deploy a syscall monitor targeting MITRE ATT&CK process-injection techniques.
# Techniques: T1055 (Process Injection), T1134 (Token Impersonation), T1055.012 (PE Hollowing)

set -euo pipefail

echo "[*] Loading APT syscall monitor module..."
/kerneldev load --module=apt_syscall_monitor.ko --verify

echo "[*] Configuring syscall filter for process-injection techniques..."
echo "T1055,T1134,T1055.012" > /sys/kernel/apt_syscall_monitor/filter

echo "[*] Starting monitoring — output: /var/log/forensic/syscalls.log"
mkdir -p /var/log/forensic
echo "/var/log/forensic/syscalls.log" > /sys/kernel/apt_syscall_monitor/log_path
echo "1" > /sys/kernel/apt_syscall_monitor/enable

echo "[+] APT syscall monitor active. Tail log with:"
echo "    tail -f /var/log/forensic/syscalls.log"

