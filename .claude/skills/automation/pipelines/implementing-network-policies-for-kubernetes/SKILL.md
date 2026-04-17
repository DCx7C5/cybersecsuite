---
name: implementing-network-policies-for-kubernetes
description: "Kubernetes NetworkPolicies provide pod-level network segmentation by defining ingress and egress rules that control"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-policies-for-kubernetes/SKILL.md"
---
# Implementing Network Policies For Kubernetes

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-policies-for-kubernetes/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-policies-for-kubernetes", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-policies-for-kubernetes")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
