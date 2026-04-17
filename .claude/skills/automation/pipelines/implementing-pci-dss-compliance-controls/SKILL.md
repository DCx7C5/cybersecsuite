---
name: implementing-pci-dss-compliance-controls
description: "PCI DSS 4.0.1 establishes 12 requirements across 6 control objectives for organizations that store, process, or transmit cardholder data. With PCI DSS 3.2.1 retiring April 2024 and 51 new requirements"
domain: cybersecurity
subdomain: compliance-governance
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: [GV.PO-01, PR.DS-01, PR.AA-01, DE.CM-01, ID.RA-01]
tags: [compliance, governance, pci-dss, payment-security, cardholder-data]
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pci-dss-compliance-controls/SKILL.md"
---
# Implementing Pci Dss Compliance Controls

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pci-dss-compliance-controls/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-pci-dss-compliance-controls", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-pci-dss-compliance-controls")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
