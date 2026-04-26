
---
name: network-services-docker-socket-expose-detect
description: Detect exposed Docker daemon socket — identify bind-mounted /var/run/docker.sock in containers (instant root escape), TCP Docker API exposure, and unauthorized socket access.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- docker
- socket
- expose
- root-escape
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
- T1190
capec: []
