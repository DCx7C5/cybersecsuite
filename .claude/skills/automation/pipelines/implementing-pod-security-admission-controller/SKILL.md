---
name: implementing-pod-security-admission-controller
description: "Implement Kubernetes Pod Security Admission to enforce baseline and restricted security profiles at namespace"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pod-security-admission-controller/SKILL.md"
---
# Implementing Pod Security Admission Controller

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pod-security-admission-controller/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-pod-security-admission-controller", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-pod-security-admission-controller")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
