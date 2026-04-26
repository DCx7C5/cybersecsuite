
---
name: filesystem-squashfs-unpack-analyze
description: Unpack and analyze SquashFS images from AppImage, Snap packages, or embedded Linux — extract contents, verify integrity, and scan for malicious payloads.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- squashfs
- appimage
- snap
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
capec: []
