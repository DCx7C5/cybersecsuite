---
name: conducting-wireless-network-penetration-test
description: "'Conducts authorized wireless network penetration tests to assess the security of WiFi infrastructure by testing"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-wireless-network-penetration-test/SKILL.md"
---
# Conducting Wireless Network Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-wireless-network-penetration-test/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="conducting-wireless-network-penetration-test", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-wireless-network-penetration-test")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
