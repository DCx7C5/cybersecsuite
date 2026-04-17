---
name: securing-kubernetes-on-cloud
description: "'This skill covers hardening managed Kubernetes clusters on EKS, AKS, and GKE by implementing Pod Security Standards,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-kubernetes-on-cloud/SKILL.md"
---
# Securing Kubernetes On Cloud

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-kubernetes-on-cloud/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="securing-kubernetes-on-cloud", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="securing-kubernetes-on-cloud")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
