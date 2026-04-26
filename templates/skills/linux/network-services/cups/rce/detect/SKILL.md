
---
name: network-services-cups-rce-detect
description: Detect CUPS Remote Code Execution exploitation (CVE-2024-47176, CVE-2024-47076) — identify unauthorized IPP requests, cups-browsed external connections, and PPD injection.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- cups
- printing
- rce
- cve-2024
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1190
- T1068
capec: []
