---
name: implementing-policy-as-code-with-open-policy-agent
description: "'This skill covers implementing Open Policy Agent (OPA) and Gatekeeper for policy-as-code enforcement in Kubernetes"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-policy-as-code-with-open-policy-agent/SKILL.md"
---
# Implementing Policy As Code With Open Policy Agent

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-policy-as-code-with-open-policy-agent/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-policy-as-code-with-open-policy-agent", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-policy-as-code-with-open-policy-agent")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
