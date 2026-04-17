---
name: scanning-network-with-nmap-advanced
description: "'Performs advanced network reconnaissance using Nmap''s scripting engine, timing controls, evasion techniques,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/scanning-network-with-nmap-advanced/SKILL.md"
---
# Scanning Network With Nmap Advanced

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/scanning-network-with-nmap-advanced/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="scanning-network-with-nmap-advanced", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="scanning-network-with-nmap-advanced")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
