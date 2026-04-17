---
name: extracting-windows-event-logs-artifacts
description: "Extract, parse, and analyze Windows Event Logs (EVTX) using Chainsaw, Hayabusa, and EvtxECmd to detect lateral"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-windows-event-logs-artifacts/SKILL.md"
---
# Extracting Windows Event Logs Artifacts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-windows-event-logs-artifacts/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="extracting-windows-event-logs-artifacts", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="extracting-windows-event-logs-artifacts")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
