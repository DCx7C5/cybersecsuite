
---
name: filesystem-fat32-efi-partition-forensic
description: Forensic analysis of the EFI System Partition (ESP) — enumerate ESP contents, detect rogue EFI applications, check bootloader integrity, and identify persistence via ESP.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- fat32
- efi
- esp
- bootloader
- forensics
nist_csf:
- RS.AN-01
- RS.AN-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []
