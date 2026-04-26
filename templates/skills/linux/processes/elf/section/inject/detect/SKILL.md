
---
name: processes-elf-section-inject-detect
description: Detect ELF binary section injection — identify extra sections added to system binaries, unusual section names, and section-based persistence in modified executables.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- elf
- section
- injection
- binary
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036
- T1195
capec: []
