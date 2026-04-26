
---
name: kernel-network-stack-netfilter-iptables-audit
description: Forensic audit of iptables rules — enumerate all tables/chains, detect firewall rule tampering, identify rules that allow unauthorized traffic or disable logging.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- iptables
- netfilter
- firewall
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.004
capec: []
