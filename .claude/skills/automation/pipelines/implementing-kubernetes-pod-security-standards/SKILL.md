---
name: implementing-kubernetes-pod-security-standards
description: "Pod Security Standards (PSS) define three levels of security policies -- Privileged, Baseline, and Restricted"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-kubernetes-pod-security-standards/SKILL.md"
---
# Implementing Kubernetes Pod Security Standards

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-kubernetes-pod-security-standards/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-kubernetes-pod-security-standards", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-kubernetes-pod-security-standards")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
