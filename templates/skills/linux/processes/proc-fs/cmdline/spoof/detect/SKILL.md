
---
name: processes-proc-fs-cmdline-spoof-detect
description: Detect process name and cmdline spoofing — identify processes manipulating argv[0], prctl(PR_SET_NAME), or /proc/self/comm to disguise malicious activity.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- proc
- cmdline
- spoof
- masquerade
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036.005
capec: []
