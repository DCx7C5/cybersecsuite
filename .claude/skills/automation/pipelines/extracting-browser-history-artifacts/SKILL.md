---
name: extracting-browser-history-artifacts
description: "Extract and analyze browser history, cookies, cache, downloads, and bookmarks from Chrome, Firefox, and Edge"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-browser-history-artifacts/SKILL.md"
---
# Extracting Browser History Artifacts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-browser-history-artifacts/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="extracting-browser-history-artifacts", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="extracting-browser-history-artifacts")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
