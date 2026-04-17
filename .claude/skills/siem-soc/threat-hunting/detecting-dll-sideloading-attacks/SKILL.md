---
name: detecting-dll-sideloading-attacks
description: "Detect DLL side-loading attacks where adversaries place malicious DLLs alongside legitimate applications to hijack"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dll-sideloading-attacks/SKILL.md"
---
# Detecting Dll Sideloading Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dll-sideloading-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-dll-sideloading-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-dll-sideloading-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
