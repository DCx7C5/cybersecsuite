#!/usr/bin/env bash
# sign_module.sh — Generate signing key and sign a kernel module for forensic use
# Usage: bash scripts/sign_module.sh <module.ko>
#
# NOTE: Development-only signing. Do NOT use in production without a proper PKI.

set -euo pipefail

MODULE="${1:-module.ko}"
KEY_DIR="./signing-keys"
mkdir -p "$KEY_DIR"

echo "[*] Generating self-signed MOK key pair (development only)..."
openssl req -new -x509 -newkey rsa:2048 \
  -keyout "$KEY_DIR/MOK.priv" \
  -outform DER \
  -out "$KEY_DIR/MOK.der" \
  -nodes \
  -days 36500 \
  -subj "/CN=Forensic Module Signing/"

echo "[*] Signing module: $MODULE"
/usr/src/linux-headers-$(uname -r)/scripts/sign-file \
  sha256 \
  "$KEY_DIR/MOK.priv" \
  "$KEY_DIR/MOK.der" \
  "$MODULE"

echo "[+] Module signed: $MODULE"
echo "[!] Remember to enroll MOK.der via: sudo mokutil --import $KEY_DIR/MOK.der"

