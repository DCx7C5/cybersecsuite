
---
name: kernel-network-stack-raw-socket-abuse-detect
description: Detect raw socket abuse by unprivileged processes — identify CAP_NET_RAW abuse, packet sniffing without legitimate tools, and packet injection via raw sockets.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- raw-socket
- cap-net-raw
- sniff
- abuse
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1040
- T1095
capec: []
