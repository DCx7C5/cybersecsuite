---
name: implementing-endpoint-dlp-controls
description: "'Implements endpoint Data Loss Prevention (DLP) controls to detect and prevent sensitive data exfiltration through"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-endpoint-dlp-controls/SKILL.md"
---
# Implementing Endpoint Dlp Controls

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-endpoint-dlp-controls/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-endpoint-dlp-controls", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-endpoint-dlp-controls")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
