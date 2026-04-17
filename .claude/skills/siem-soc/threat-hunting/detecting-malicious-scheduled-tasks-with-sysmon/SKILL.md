---
name: detecting-malicious-scheduled-tasks-with-sysmon
description: "'Detect malicious scheduled task creation and modification using Sysmon Event IDs 1 (Process Create for schtasks.exe),"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-malicious-scheduled-tasks-with-sysmon/SKILL.md"
---
# Detecting Malicious Scheduled Tasks With Sysmon

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-malicious-scheduled-tasks-with-sysmon/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-malicious-scheduled-tasks-with-sysmon", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-malicious-scheduled-tasks-with-sysmon")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
