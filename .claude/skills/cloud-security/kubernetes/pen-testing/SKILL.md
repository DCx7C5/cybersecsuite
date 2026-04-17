---
name: performing-kubernetes-penetration-testing
description: "Kubernetes penetration testing systematically evaluates cluster security by simulating attacker techniques against"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-penetration-testing/SKILL.md"
---
# Performing Kubernetes Penetration Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-penetration-testing/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-kubernetes-penetration-testing", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-kubernetes-penetration-testing")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
