---
name: implementing-runtime-security-with-tetragon
description: "Implement eBPF-based runtime security observability and enforcement in Kubernetes clusters using Cilium Tetragon"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-runtime-security-with-tetragon/SKILL.md"
---
# Implementing Runtime Security With Tetragon

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-runtime-security-with-tetragon/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-runtime-security-with-tetragon", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-runtime-security-with-tetragon")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
