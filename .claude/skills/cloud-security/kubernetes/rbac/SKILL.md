---
name: auditing-kubernetes-cluster-rbac
description: "'Auditing Kubernetes cluster RBAC configurations to identify overly permissive roles, wildcard permissions, dangerous"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-kubernetes-cluster-rbac/SKILL.md"
---
# Auditing Kubernetes Cluster Rbac

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-kubernetes-cluster-rbac/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="auditing-kubernetes-cluster-rbac", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="auditing-kubernetes-cluster-rbac")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
