
---
name: kernel-memory-dma-attack-detect
description: Detect Direct Memory Access attacks targeting kernel memory — PCI device enumeration anomalies, IOMMU bypass attempts, and unauthorized DMA-capable device insertion.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- dma
- iommu
- memory
- hardware
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1200
capec: []
