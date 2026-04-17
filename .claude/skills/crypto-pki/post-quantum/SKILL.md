---
name: performing-post-quantum-cryptography-migration
description: "'Assesses organizational readiness for post-quantum cryptography migration per NIST FIPS 203/204/205 standards."
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-post-quantum-cryptography-migration/SKILL.md"
---
# Performing Post Quantum Cryptography Migration

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-post-quantum-cryptography-migration/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-post-quantum-cryptography-migration", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-post-quantum-cryptography-migration")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cryptography-analyst` or `@cybersec-agent`
