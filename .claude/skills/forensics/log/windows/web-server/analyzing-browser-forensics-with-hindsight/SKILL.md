---
name: analyzing-browser-forensics-with-hindsight
description: "Analyze Chromium-based browser artifacts using Hindsight to extract browsing history, downloads, cookies, cached"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-browser-forensics-with-hindsight/SKILL.md"
---
# Analyzing Browser Forensics With Hindsight

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-browser-forensics-with-hindsight/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="analyzing-browser-forensics-with-hindsight", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-browser-forensics-with-hindsight")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
