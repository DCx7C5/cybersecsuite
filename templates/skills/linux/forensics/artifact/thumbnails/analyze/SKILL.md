
---
name: forensics-artifact-thumbnails-analyze
description: Analyze thumbnail cache artifacts for forensic investigation — extract GNOME/KDE thumbnail databases to recover deleted image evidence and reconstruct accessed file history.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- thumbnails
- cache
- artifact
- forensics
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []
