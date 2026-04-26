
---
name: hardware-cpu-spectre-meltdown-detect
description: Detect Spectre and Meltdown hardware side-channel vulnerability exposure on Linux systems via microcode version checks, kernel mitigations, and CPU flags.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- cpu
- spectre
- meltdown
- side-channel
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1600
capec: []
