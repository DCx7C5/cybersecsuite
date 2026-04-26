
---
name: network-services-ssh-tunnel-detect
description: Detect unauthorized SSH tunneling — identify LocalForward/RemoteForward/DynamicForward connections, SOCKS proxy via SSH, and SSH as a covert C2 channel.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- ssh
- tunnel
- forward
- c2
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1572
- T1021.004
capec: []
