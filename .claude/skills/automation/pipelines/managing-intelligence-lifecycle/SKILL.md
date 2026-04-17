---
name: managing-intelligence-lifecycle
description: "'Manages the end-to-end cyber threat intelligence lifecycle from planning and direction through collection, processing,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/managing-intelligence-lifecycle/SKILL.md"
---
# Managing Intelligence Lifecycle

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/managing-intelligence-lifecycle/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="managing-intelligence-lifecycle", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="managing-intelligence-lifecycle")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
