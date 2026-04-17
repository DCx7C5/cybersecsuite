---
name: implementing-security-information-sharing-with-stix2
description: "'Create, validate, and share STIX 2.1 threat intelligence objects using the stix2 Python library. Covers indicators,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-security-information-sharing-with-stix2/SKILL.md"
---
# Implementing Security Information Sharing With Stix2

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-security-information-sharing-with-stix2/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-security-information-sharing-with-stix2", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-security-information-sharing-with-stix2")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
