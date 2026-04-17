#!/usr/bin/env bash
# scenario_memory_forensics.sh — Scenario 3: Memory Forensics Collection
# Deploy live memory analysis module and collect process, heap, stack, and VMA artifacts.

set -euo pipefail

OUTPUT_DIR="${1:-/forensic/memory-artifacts}"

echo "[*] Loading memory forensics collector module..."
/kerneldev load --module=memory_forensics_collector.ko --verify

echo "[*] Configuring collection targets: processes, heap, stack, vma..."
echo "processes,heap,stack,vma" > /sys/kernel/memory_forensics_collector/targets

echo "[*] Starting collection into: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
echo "$OUTPUT_DIR" > /sys/kernel/memory_forensics_collector/output_path
echo "1" > /sys/kernel/memory_forensics_collector/enable

echo "[+] Memory forensics collector active."
echo "    Artifacts will be written to: $OUTPUT_DIR"

