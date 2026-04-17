---
name: implementing-soar-automation-with-phantom
description: "'Implements Security Orchestration, Automation, and Response (SOAR) workflows using Splunk SOAR (formerly Phantom)"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-soar-automation-with-phantom/SKILL.md"
---
# Implementing Soar Automation With Phantom

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-soar-automation-with-phantom/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-soar-automation-with-phantom", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-soar-automation-with-phantom")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
