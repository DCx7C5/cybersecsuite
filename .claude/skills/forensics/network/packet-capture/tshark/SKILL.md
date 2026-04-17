---
name: performing-network-traffic-analysis-with-tshark
description: "Automate network traffic analysis using tshark and pyshark for protocol statistics, suspicious flow detection,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-network-traffic-analysis-with-tshark/SKILL.md"
---
# Performing Network Traffic Analysis With Tshark

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-network-traffic-analysis-with-tshark/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-network-traffic-analysis-with-tshark", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-network-traffic-analysis-with-tshark")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
