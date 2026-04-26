
---
name: identity-ssh-authorized-keys-backdoor-detect
description: Detect SSH authorized_keys backdoors — scan all user ~/.ssh/authorized_keys for unauthorized keys, detect non-standard AuthorizedKeysFile locations, and identify key-based persistence.
domain: cybersecurity
subdomain: identity-forensics
tags:
- linux
- ssh
- authorized-keys
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1098.004
- T1021.004
capec: []
