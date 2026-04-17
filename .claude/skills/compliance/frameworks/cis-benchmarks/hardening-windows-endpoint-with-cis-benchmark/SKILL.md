---
name: hardening-windows-endpoint-with-cis-benchmark
description: "'Hardens Windows endpoints using CIS (Center for Internet Security) Benchmark recommendations to reduce attack"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-windows-endpoint-with-cis-benchmark/SKILL.md"
---
# Hardening Windows Endpoint With Cis Benchmark

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-windows-endpoint-with-cis-benchmark/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hardening-windows-endpoint-with-cis-benchmark", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hardening-windows-endpoint-with-cis-benchmark")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
