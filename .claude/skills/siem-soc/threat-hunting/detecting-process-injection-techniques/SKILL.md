---
name: detecting-process-injection-techniques
description: "'Detects and analyzes process injection techniques used by malware including classic DLL injection, process hollowing,"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-process-injection-techniques/SKILL.md"
---
# Detecting Process Injection Techniques

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-process-injection-techniques/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-process-injection-techniques", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-process-injection-techniques")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
