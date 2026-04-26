
---
name: kernel-boot-initramfs-backdoor-detect
description: Detect malicious modifications to initramfs/initrd — unpack and inspect early userspace for backdoored binaries, added scripts, or unauthorized kernel modules.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- initramfs
- initrd
- backdoor
- boot
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.003
- T1014
capec: []
