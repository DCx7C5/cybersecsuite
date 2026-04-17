---
name: performing-brand-monitoring-for-impersonation
description: "Monitor for brand impersonation attacks across domains, social media, mobile apps, and dark web channels to detect"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-brand-monitoring-for-impersonation/SKILL.md"
---
# Performing Brand Monitoring For Impersonation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-brand-monitoring-for-impersonation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-brand-monitoring-for-impersonation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-brand-monitoring-for-impersonation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
