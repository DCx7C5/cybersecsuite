---
name: detecting-network-scanning-with-ids-signatures
description: "Detect network reconnaissance and port scanning using Suricata and Snort IDS signatures, threshold-based detection"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-network-scanning-with-ids-signatures/SKILL.md"
---
# Detecting Network Scanning With Ids Signatures

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-network-scanning-with-ids-signatures/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-network-scanning-with-ids-signatures", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-network-scanning-with-ids-signatures")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
