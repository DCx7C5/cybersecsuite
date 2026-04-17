---
name: detecting-arp-poisoning-in-network-traffic
description: "Detect and prevent ARP spoofing attacks using ARPWatch, Dynamic ARP Inspection, Wireshark analysis, and custom"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-arp-poisoning-in-network-traffic/SKILL.md"
---
# Detecting Arp Poisoning In Network Traffic

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-arp-poisoning-in-network-traffic/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-arp-poisoning-in-network-traffic", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-arp-poisoning-in-network-traffic")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
