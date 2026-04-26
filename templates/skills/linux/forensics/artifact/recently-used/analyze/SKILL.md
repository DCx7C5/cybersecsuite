
---
name: forensics-artifact-recently-used-analyze
description: Analyze recently-used file artifacts on Linux — extract GTK recently-used.xbel, KDE recent documents, and XDG runtime artifacts to reconstruct user/attacker file access timeline.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- recently-used
- xbel
- gtk
- artifact
- timeline
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1083
capec: []
