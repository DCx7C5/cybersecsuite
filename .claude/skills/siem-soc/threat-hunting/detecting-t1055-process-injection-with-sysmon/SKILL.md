---
name: detecting-t1055-process-injection-with-sysmon
description: "Detect process injection techniques (T1055) including classic DLL injection, process hollowing, and APC injection"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-t1055-process-injection-with-sysmon/SKILL.md"
---
# Detecting T1055 Process Injection With Sysmon

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-t1055-process-injection-with-sysmon/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-t1055-process-injection-with-sysmon", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-t1055-process-injection-with-sysmon")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
