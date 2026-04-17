---
name: hunting-for-living-off-the-land-binaries
description: "Proactively hunt for adversary abuse of legitimate system binaries (LOLBins) to execute malicious payloads while"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-living-off-the-land-binaries/SKILL.md"
---
# Hunting For Living Off The Land Binaries

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-living-off-the-land-binaries/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-living-off-the-land-binaries", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-living-off-the-land-binaries")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
