
---
name: hardware-storage-nvme-forensic
description: Forensic acquisition and analysis of NVMe block devices — raw image creation, wear leveling artifact analysis, and deleted data recovery from NVMe SSDs.
domain: cybersecurity
subdomain: hardware-forensics
tags:
- linux
- nvme
- storage
- forensics
- block-device
nist_csf:
- RS.AN-01
- RS.AN-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []
