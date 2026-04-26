
---
name: network-services-dns-server-zone-exfil-detect
description: Detect DNS zone transfer data exfiltration — identify unauthorized AXFR/IXFR requests, misconfigured BIND allow-transfer ACLs, and DNS zone data as exfiltration vector.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- dns
- bind
- zone-transfer
- exfil
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1048
- T1590.002
capec: []
