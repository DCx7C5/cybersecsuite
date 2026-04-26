
---
name: memory-aslr-entropy-analyze
description: Analyze ASLR implementation strength on Linux — measure address randomization entropy, identify ASLR-defeating techniques (brute force, info leaks), and verify ASLR configuration.
domain: cybersecurity
subdomain: memory-security
tags:
- linux
- aslr
- entropy
- bypass
- memory
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
