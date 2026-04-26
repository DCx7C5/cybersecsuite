
---
name: hardware-thunderbolt-dma-attack-detect
description: Detect Thunderbolt DMA attack vectors (Thunderspy) — enumerate Thunderbolt devices, check security levels, and detect unauthorized DMA access to host memory.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- thunderbolt
- dma
- thunderspy
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1200
capec: []
