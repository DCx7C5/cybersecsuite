
---
name: filesystem-fuse-rootkit-detect
description: Detect FUSE-based filesystem rootkits — identify user-space filesystem mounts that intercept file operations to hide files or manipulate data transparently.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- fuse
- rootkit
- filesystem
- hide
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1036
capec: []
