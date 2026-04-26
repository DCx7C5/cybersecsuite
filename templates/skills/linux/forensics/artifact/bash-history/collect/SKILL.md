
---
name: forensics-artifact-bash-history-collect
description: Collect and preserve shell history artifacts for forensic investigation — acquire .bash_history, .zsh_history, and in-memory history from all users including cleared history artifacts.
domain: cybersecurity
subdomain: forensic-collection
tags:
- linux
- bash
- history
- artifact
- forensics
nist_csf:
- RS.AN-01
- DE.CM-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.003
- T1005
capec: []
