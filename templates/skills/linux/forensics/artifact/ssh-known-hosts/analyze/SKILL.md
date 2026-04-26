
---
name: forensics-artifact-ssh-known-hosts-analyze
description: Analyze SSH known_hosts files for forensic intelligence — extract host fingerprints, identify lateral movement targets, detect unusual hosts, and correlate with network connections.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- ssh
- known-hosts
- lateral-movement
- forensics
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1021.004
- T1078
capec: []
