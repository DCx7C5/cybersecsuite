
---
name: network-services-apache-config-audit
description: Security audit of Apache httpd configuration — review ServerTokens, directory indexing, mod_status exposure, .htaccess risks, and SSL/TLS configuration weaknesses.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- apache
- httpd
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
