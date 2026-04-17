---
name: implementing-container-network-policies-with-calico
description: "Enforce Kubernetes network segmentation using Calico CNI network policies and global network policies to control"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-container-network-policies-with-calico/SKILL.md"
---
# Implementing Container Network Policies With Calico

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-container-network-policies-with-calico/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-container-network-policies-with-calico", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-container-network-policies-with-calico")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
