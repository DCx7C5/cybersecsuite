
---
name: kernel-boot-grub-tamper-detect
description: Detect GRUB bootloader tampering — check GRUB binary hashes, grub.cfg integrity, password protection, and unauthorized menu entries that could load malicious kernels.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- grub
- bootloader
- tamper
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
- T1014
capec: []
