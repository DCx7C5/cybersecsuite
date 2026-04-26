
---
name: kernel-network-stack-netfilter-nftables-audit
description: Forensic audit of nftables rules — enumerate nft tables/chains/rules, detect unauthorized modifications, and identify rules bypassing security controls.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- nftables
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
