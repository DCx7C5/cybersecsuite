
---
name: kernel-boot-uefi-variable-tamper-detect
description: Detect unauthorized UEFI variable manipulation — monitor EFI variable store for persistence via NVRAM, rogue boot entries, and BootOrder manipulation.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- uefi
- efi-variable
- nvram
- tamper
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []
