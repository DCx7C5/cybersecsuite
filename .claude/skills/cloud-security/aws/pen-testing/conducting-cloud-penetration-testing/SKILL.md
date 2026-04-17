---
name: conducting-cloud-penetration-testing
description: "'This skill outlines methodologies for performing authorized penetration testing against AWS, Azure, and GCP"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-cloud-penetration-testing/SKILL.md"
---
# Conducting Cloud Penetration Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-cloud-penetration-testing/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="conducting-cloud-penetration-testing", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-cloud-penetration-testing")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
