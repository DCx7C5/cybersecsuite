---
name: performing-wireless-network-penetration-test
description: "Execute a wireless network penetration test to assess WiFi security by capturing handshakes, cracking WPA2/WPA3"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-wireless-network-penetration-test/SKILL.md"
---
# Performing Wireless Network Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-wireless-network-penetration-test/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-wireless-network-penetration-test", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-wireless-network-penetration-test")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@penetration-testing-analyst` or `@cybersec-agent`
