
---
name: network-services-ssh-brute-detect
description: Detect SSH brute force attacks — analyze /var/log/auth.log for failed authentication patterns, configure fail2ban rules, and identify credential stuffing campaigns.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- ssh
- brute-force
- detect
- auth-log
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1110.001
- T1021.004
capec: []
