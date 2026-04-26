
---
name: logging-syslog-forwarding-harden
description: Harden syslog forwarding configuration — configure TLS-encrypted log forwarding (rsyslog/syslog-ng), prevent log injection, and set up centralized SIEM integration securely.
domain: cybersecurity
subdomain: logging-hardening
tags:
- linux
- syslog
- rsyslog
- forwarding
- harden
- tls
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.001
capec: []
