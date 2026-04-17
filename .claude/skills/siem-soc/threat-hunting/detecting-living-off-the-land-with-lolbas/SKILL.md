---
name: detecting-living-off-the-land-with-lolbas
description: "Detect Living Off the Land Binaries (LOLBins/LOLBAS) abuse including certutil, regsvr32, mshta, and rundll32"
domain: cybersecurity
subdomain: threat-detection
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-living-off-the-land-with-lolbas/SKILL.md"
---
# Detecting Living Off The Land With Lolbas

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-living-off-the-land-with-lolbas/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-living-off-the-land-with-lolbas", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-living-off-the-land-with-lolbas")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
