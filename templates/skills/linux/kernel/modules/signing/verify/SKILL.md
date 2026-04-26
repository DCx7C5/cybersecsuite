
---
name: kernel-modules-signing-verify
description: Verify kernel module signing — check module signatures against trusted keys, detect unsigned or invalidly-signed modules loaded into the kernel.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- lkm
- module
- signing
- integrity
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1195
capec: []
