
---
name: hardware-memory-cold-boot-artifact-collect
description: Collect memory artifacts from a cold boot attack — physical memory dump techniques, DIMM cooling, and live memory acquisition before volatile data is lost.
domain: cybersecurity
subdomain: hardware-forensics
tags:
- linux
- memory
- cold-boot
- dram
- forensics
nist_csf:
- RS.AN-01
- DE.CM-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1200
- T1005
capec: []
