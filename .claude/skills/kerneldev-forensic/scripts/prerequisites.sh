#!/usr/bin/env bash
# prerequisites.sh — Install kernel development tools and kerneldev-mcp
# Usage: bash scripts/prerequisites.sh

set -euo pipefail

echo "[*] Installing kernel development tools..."
sudo pacman -S --needed linux-headers base-devel

echo "[*] Installing DKMS and module-init-tools..."
sudo pacman -S --needed dkms module-init-tools

echo "[*] Installing compiler toolchain..."
sudo pacman -S --needed gcc make

echo "[*] Installing kerneldev-mcp via pip (if available)..."
pip install kerneldev-mcp || echo "[!] kerneldev-mcp not available via pip — install manually."

echo "[+] Prerequisites installed successfully."

