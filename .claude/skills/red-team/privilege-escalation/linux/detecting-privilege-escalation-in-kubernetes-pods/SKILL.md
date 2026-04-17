---
name: detecting-privilege-escalation-in-kubernetes-pods
description: "Detect and prevent privilege escalation in Kubernetes pods by monitoring security contexts, capabilities, and"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-privilege-escalation-in-kubernetes-pods/SKILL.md"
---
# Detecting Privilege Escalation In Kubernetes Pods

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-privilege-escalation-in-kubernetes-pods/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-privilege-escalation-in-kubernetes-pods", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-privilege-escalation-in-kubernetes-pods")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
