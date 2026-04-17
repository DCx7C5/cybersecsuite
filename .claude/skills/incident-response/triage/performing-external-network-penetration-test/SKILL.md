---
name: performing-external-network-penetration-test
description: "Conduct a comprehensive external network penetration test to identify vulnerabilities in internet-facing infrastructure"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-external-network-penetration-test/SKILL.md"
---
# Performing External Network Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-external-network-penetration-test/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-external-network-penetration-test", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-external-network-penetration-test")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
