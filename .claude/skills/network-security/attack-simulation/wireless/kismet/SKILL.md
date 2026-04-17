---
name: performing-wireless-security-assessment-with-kismet
description: "Conduct wireless network security assessments using Kismet to detect rogue access points, hidden SSIDs, weak"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-wireless-security-assessment-with-kismet/SKILL.md"
---
# Performing Wireless Security Assessment With Kismet

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-wireless-security-assessment-with-kismet/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-wireless-security-assessment-with-kismet", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-wireless-security-assessment-with-kismet")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
