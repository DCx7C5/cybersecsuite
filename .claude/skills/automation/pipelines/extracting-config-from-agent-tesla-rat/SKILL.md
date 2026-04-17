---
name: extracting-config-from-agent-tesla-rat
description: "Extract embedded configuration from Agent Tesla RAT samples including SMTP/FTP/Telegram exfiltration credentials,"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-config-from-agent-tesla-rat/SKILL.md"
---
# Extracting Config From Agent Tesla Rat

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-config-from-agent-tesla-rat/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="extracting-config-from-agent-tesla-rat", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="extracting-config-from-agent-tesla-rat")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
