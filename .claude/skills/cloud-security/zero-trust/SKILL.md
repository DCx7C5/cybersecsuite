---
name: configuring-microsegmentation-for-zero-trust
description: "Configure microsegmentation policies to enforce least-privilege workload-to-workload access using tools like"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-microsegmentation-for-zero-trust/SKILL.md"
---
# Configuring Microsegmentation For Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-microsegmentation-for-zero-trust/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-microsegmentation-for-zero-trust", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-microsegmentation-for-zero-trust")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@zero-trust-architecture-analyst` or `@cybersec-agent`
