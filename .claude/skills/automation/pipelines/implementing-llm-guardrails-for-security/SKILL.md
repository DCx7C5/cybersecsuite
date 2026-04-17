---
name: implementing-llm-guardrails-for-security
description: "'Implements input and output validation guardrails for LLM-powered applications to prevent prompt injection,"
domain: cybersecurity
subdomain: ai-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-llm-guardrails-for-security/SKILL.md"
---
# Implementing Llm Guardrails For Security

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-llm-guardrails-for-security/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-llm-guardrails-for-security", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-llm-guardrails-for-security")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
