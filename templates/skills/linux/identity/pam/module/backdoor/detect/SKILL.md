
---
name: identity-pam-module-backdoor-detect
description: Detect malicious PAM module insertion — identify unauthorized .so files in /lib/security/, modules logging credentials, and modified pam.d configurations.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- pam
- module
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1556.003
- T1078
capec: []
