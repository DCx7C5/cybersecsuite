---
name: hardening-apparmor-profile-create-configure
description: Create and enforce AppArmor profiles for applications — generate profiles in complain mode, analyze violations, convert to enforce mode, and validate confinement.
domain: cybersecurity
subdomain: hardening-implementation
tags:
- linux
- apparmor
- profile
- mac
- harden
nist_csf:
- ID.RA-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
