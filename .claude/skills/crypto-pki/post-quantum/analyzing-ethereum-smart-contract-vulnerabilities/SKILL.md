---
name: analyzing-ethereum-smart-contract-vulnerabilities
description: "Perform static and symbolic analysis of Solidity smart contracts using Slither and Mythril to detect reentrancy,"
domain: cybersecurity
subdomain: blockchain-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-ethereum-smart-contract-vulnerabilities/SKILL.md"
---
# Analyzing Ethereum Smart Contract Vulnerabilities

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-ethereum-smart-contract-vulnerabilities/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="analyzing-ethereum-smart-contract-vulnerabilities", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-ethereum-smart-contract-vulnerabilities")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
