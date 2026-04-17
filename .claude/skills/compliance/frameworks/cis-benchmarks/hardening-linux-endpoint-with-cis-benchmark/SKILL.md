---
name: hardening-linux-endpoint-with-cis-benchmark
description: "'Hardens Linux endpoints using CIS Benchmark recommendations for Ubuntu, RHEL, and CentOS to reduce attack surface,"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-linux-endpoint-with-cis-benchmark/SKILL.md"
---
# Hardening Linux Endpoint With Cis Benchmark

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-linux-endpoint-with-cis-benchmark/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hardening-linux-endpoint-with-cis-benchmark", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hardening-linux-endpoint-with-cis-benchmark")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
