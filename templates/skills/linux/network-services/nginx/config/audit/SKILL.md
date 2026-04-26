
---
name: network-services-nginx-config-audit
description: Security audit of nginx web server configuration — check for server version exposure, insecure headers, directory traversal, misconfigured SSL/TLS, and open proxy risks.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- nginx
- web
- configuration
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1190
- T1083
capec: []
