---
name: performing-arp-spoofing-attack-simulation
description: "'Simulates ARP spoofing attacks in authorized lab or pentest environments using arpspoof, Ettercap, and Scapy"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-arp-spoofing-attack-simulation/SKILL.md"
---
# Performing Arp Spoofing Attack Simulation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-arp-spoofing-attack-simulation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-arp-spoofing-attack-simulation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-arp-spoofing-attack-simulation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
