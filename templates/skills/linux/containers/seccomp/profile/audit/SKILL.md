
---
name: containers-seccomp-profile-audit
description: Audit container seccomp profiles — analyze Docker/Kubernetes seccomp policies for dangerous syscalls, identify containers running without seccomp, and compare against default profiles.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- container
- seccomp
- docker
- kubernetes
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
capec: []
