---
name: performing-bandwidth-throttling-attack-simulation
description: "'Simulates bandwidth throttling and network degradation attacks using tc, iperf3, and Scapy in authorized environments"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-bandwidth-throttling-attack-simulation/SKILL.md"
---
# Performing Bandwidth Throttling Attack Simulation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-bandwidth-throttling-attack-simulation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-bandwidth-throttling-attack-simulation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-bandwidth-throttling-attack-simulation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
