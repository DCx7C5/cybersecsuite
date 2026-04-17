---
name: detecting-rootkit-activity
description: "'Detects rootkit presence on compromised systems by identifying hidden processes, hooked system calls, modified"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-rootkit-activity/SKILL.md"
---
# Detecting Rootkit Activity

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-rootkit-activity/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-rootkit-activity", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-rootkit-activity")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
