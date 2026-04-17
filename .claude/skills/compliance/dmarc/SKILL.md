---
name: performing-dmarc-policy-enforcement-rollout
description: "Execute a phased DMARC rollout from p=none monitoring through p=quarantine to p=reject enforcement, ensuring"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-dmarc-policy-enforcement-rollout/SKILL.md"
---
# Performing Dmarc Policy Enforcement Rollout

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-dmarc-policy-enforcement-rollout/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-dmarc-policy-enforcement-rollout", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-dmarc-policy-enforcement-rollout")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@phishing-defense-analyst` or `@cybersec-agent`
