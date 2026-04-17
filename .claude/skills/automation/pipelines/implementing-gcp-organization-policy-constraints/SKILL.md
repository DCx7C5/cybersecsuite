---
name: implementing-gcp-organization-policy-constraints
description: "Implement GCP Organization Policy constraints to enforce security guardrails across the entire resource hierarchy,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-organization-policy-constraints/SKILL.md"
---
# Implementing Gcp Organization Policy Constraints

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-organization-policy-constraints/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-gcp-organization-policy-constraints", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-gcp-organization-policy-constraints")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
