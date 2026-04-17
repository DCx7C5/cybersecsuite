---
name: performing-kubernetes-cis-benchmark-with-kube-bench
description: "Audit Kubernetes cluster security posture against CIS benchmarks using kube-bench with automated checks for control"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-cis-benchmark-with-kube-bench/SKILL.md"
---
# Performing Kubernetes Cis Benchmark With Kube Bench

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-kubernetes-cis-benchmark-with-kube-bench/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-kubernetes-cis-benchmark-with-kube-bench", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-kubernetes-cis-benchmark-with-kube-bench")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
