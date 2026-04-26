
---
name: supply-chain-package-apt-integrity-verify
description: Verify Debian/Ubuntu package integrity — use debsums to check installed file hashes, validate apt repository GPG signatures, and detect tampered packages.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- apt
- debian
- package
- integrity
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
capec: []
