
---
name: identity-ssh-config-harden
description: Harden SSH server configuration (sshd_config) — disable root login, enforce key-only auth, restrict ciphers, set idle timeout, enable strict mode, and validate config.
domain: cybersecurity
subdomain: identity-hardening
tags:
- linux
- ssh
- sshd
- harden
- configuration
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1021.004
- T1078
capec: []
