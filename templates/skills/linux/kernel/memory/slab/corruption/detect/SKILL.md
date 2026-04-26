
---
name: kernel-memory-slab-corruption-detect
description: Detect kernel slab heap corruption — identify heap spray attempts, use-after-free patterns in kernel allocators (SLUB/SLAB/SLOB), and kernel oops artifacts.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- slab
- heap
- kernel
- corruption
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
