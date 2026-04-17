---
name: implementing-rbac-hardening-for-kubernetes
description: "Harden Kubernetes Role-Based Access Control by implementing least-privilege policies, auditing role bindings,"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-rbac-hardening-for-kubernetes/SKILL.md"
---
# Implementing Rbac Hardening For Kubernetes

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-rbac-hardening-for-kubernetes/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-rbac-hardening-for-kubernetes", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-rbac-hardening-for-kubernetes")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
