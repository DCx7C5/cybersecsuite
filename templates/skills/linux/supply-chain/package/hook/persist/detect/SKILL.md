
---
name: supply-chain-package-hook-persist-detect
description: Detect persistence via package manager hooks — identify malicious dpkg/apt pre/post-install hooks, rpm scriptlets, and pacman hooks that execute attacker code on package operations.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- apt
- dpkg
- rpm
- hook
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
- T1543
capec: []
