
---
name: identity-pam-stack-bypass-detect
description: Detect PAM authentication stack bypass — identify pam_permit abuse, 'sufficient' control flag manipulation, and PAM stack modifications that bypass authentication.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- pam
- authentication
- bypass
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1556.003
- T1078
capec: []
