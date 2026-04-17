---
name: implementing-syslog-centralization-with-rsyslog
description: "Configure rsyslog for centralized log collection with TLS encryption, custom templates, and log rotation. Generates"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-syslog-centralization-with-rsyslog/SKILL.md"
---
# Implementing Syslog Centralization With Rsyslog

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-syslog-centralization-with-rsyslog/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-syslog-centralization-with-rsyslog", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-syslog-centralization-with-rsyslog")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
