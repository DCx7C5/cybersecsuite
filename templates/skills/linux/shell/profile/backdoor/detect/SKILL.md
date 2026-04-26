
---
name: shell-profile-backdoor-detect
description: Detect shell profile backdoors — scan .bashrc, .bash_profile, .profile, .zshrc, /etc/profile.d/ for injected commands, reverse shells, and credential harvesting hooks.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- shell
- bashrc
- profile
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1546.004
capec: []
