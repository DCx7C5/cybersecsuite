---
name: analyzing-network-packets-with-scapy
description: "Craft, send, sniff, and dissect network packets using Scapy for protocol analysis, network reconnaissance, and"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-network-packets-with-scapy/SKILL.md"
---
# Analyzing Network Packets With Scapy

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-network-packets-with-scapy/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-network-packets-with-scapy", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-network-packets-with-scapy")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
