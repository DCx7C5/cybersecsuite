
---
name: kernel-modules-blacklist-audit
description: Audit kernel module blacklists — review /etc/modprobe.d/ blacklist entries, identify missing critical blacklists (cramfs, freevxfs, usb-storage), and verify enforcement.
domain: cybersecurity
subdomain: kernel-hardening
tags:
- linux
- kernel-module
- blacklist
- harden
- modprobe
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1200
capec: []
