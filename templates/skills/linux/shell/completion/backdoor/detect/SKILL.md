
---
name: shell-completion-backdoor-detect
description: Detect shell completion script backdoors — identify malicious completion functions in /etc/bash_completion.d/ or ~/.bash_completion that execute commands on tab-completion events.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- bash-completion
- shell
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
