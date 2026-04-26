
---
name: filesystem-overlayfs-layer-analyze
description: Analyze OverlayFS layers used by container runtimes — inspect upper/lower/work directories, detect file modifications within containers, and recover deleted container artifacts.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- overlayfs
- container
- filesystem
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1036
capec: []
