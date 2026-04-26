
---
name: supply-chain-binary-hash-verify
description: Verify system binary integrity via hash comparison — baseline critical binaries (ls, ps, netstat, sshd), detect replacements, and identify trojanized executables.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- binary
- hash
- integrity
- trojan
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036
- T1195
capec: []
