---
name: forensics-timeline-plaso-create-configure
description: Create a forensic super-timeline of a Linux system using Plaso (log2timeline) — aggregate artifacts from filesystem, logs, shell history, browser data into a unified timeline.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- plaso
- log2timeline
- timeline
- forensics
nist_csf:
- ID.RA-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1070
capec: []
