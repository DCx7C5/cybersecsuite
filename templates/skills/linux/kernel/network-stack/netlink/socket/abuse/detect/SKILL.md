
---
name: kernel-network-stack-netlink-socket-abuse-detect
description: Detect Netlink socket privilege abuse — identify processes using Netlink to modify routing, firewall rules, or network interfaces without going through standard tools.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- netlink
- socket
- privilege
- abuse
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.004
- T1548
capec: []
