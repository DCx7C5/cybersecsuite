---
name: analyzing-kubernetes-audit-logs
description: "'Parses Kubernetes API server audit logs (JSON lines) to detect exec-into-pod, secret access, RBAC modifications,"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-kubernetes-audit-logs/SKILL.md"
---
# Analyzing Kubernetes Audit Logs

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-kubernetes-audit-logs/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-kubernetes-audit-logs", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-kubernetes-audit-logs")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
