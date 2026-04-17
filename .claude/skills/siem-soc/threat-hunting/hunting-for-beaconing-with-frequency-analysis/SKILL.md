---
name: hunting-for-beaconing-with-frequency-analysis
description: "Identify command-and-control beaconing patterns in network traffic by applying statistical frequency analysis,"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-beaconing-with-frequency-analysis/SKILL.md"
---
# Hunting For Beaconing With Frequency Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-beaconing-with-frequency-analysis/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-beaconing-with-frequency-analysis", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-beaconing-with-frequency-analysis")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
