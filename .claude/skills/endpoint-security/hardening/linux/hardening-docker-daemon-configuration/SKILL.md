---
name: hardening-docker-daemon-configuration
description: "Harden the Docker daemon by configuring daemon.json with user namespace remapping, TLS authentication, rootless"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-docker-daemon-configuration/SKILL.md"
---
# Hardening Docker Daemon Configuration

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-docker-daemon-configuration/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hardening-docker-daemon-configuration", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hardening-docker-daemon-configuration")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
