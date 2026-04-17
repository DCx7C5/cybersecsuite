---
name: implementing-gcp-binary-authorization
description: "Implement GCP Binary Authorization to enforce deploy-time security controls that ensure only trusted, attested"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-binary-authorization/SKILL.md"
---
# Implementing Gcp Binary Authorization

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-binary-authorization/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-gcp-binary-authorization", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-gcp-binary-authorization")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
