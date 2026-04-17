---
name: performing-kubernetes-etcd-security-assessment
description: "Assess the security posture of Kubernetes etcd clusters by evaluating encryption at rest, TLS configuration,"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-etcd-security-assessment/SKILL.md"
---
# Performing Kubernetes Etcd Security Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-etcd-security-assessment/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-kubernetes-etcd-security-assessment", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-kubernetes-etcd-security-assessment")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
