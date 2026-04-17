---
name: securing-helm-chart-deployments
description: "Secure Helm chart deployments by validating chart integrity, scanning templates for misconfigurations, and enforcing"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-helm-chart-deployments/SKILL.md"
---
# Securing Helm Chart Deployments

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-helm-chart-deployments/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="securing-helm-chart-deployments", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="securing-helm-chart-deployments")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
