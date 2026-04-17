# Agents Reference

All 32 specialist agents available in CyberSecSuite, plus 3 team compositions.

Agents are defined in `.claude/agents/*.md` and loaded at startup by `AgentRegistry` for A2A routing.

---

## Orchestrator

| Agent | Model | Description |
|-------|-------|-------------|
| `cybersec-agent` | Sonnet | Central orchestrator for APT/rootkit investigations. Accepts `blue\|red\|purple` mode. Delegates to all specialists. Trigger: any investigation, threat hunt, IOC analysis, artifact signing. |

---

## Forensics Analysts

| Agent | Model | Trigger |
|-------|-------|---------|
| `filesystem-analyst` | Sonnet | Hidden files, SUID binaries, timestamp anomalies, Deep Scan phase |
| `kernel-analyst` | Sonnet | LKM, eBPF, firmware, kernel rootkit, /proc anomalies |
| `memory-analyst` | Sonnet | Suspicious process, memory anomaly, injection indicator, Phase 5 |
| `persistence-analyst` | Sonnet | New service, cron anomaly, kernel module, startup persistence |
| `process-analyst` | Sonnet | Abnormal resource usage, Rapid Recon, process-based persistence |
| `logfile-analyst` | Sonnet | Auth failures, log gaps, unexpected service behavior, attacker timeline |
| `firmware-analyst` | Opus | UEFI implants, boot anomalies, SPI flash, initramfs tampering |
| `reverse-engineer` | Opus | ELF/PE/Mach-O binaries, shellcode, unpacking, deobfuscation |

---

## Network & Protocol Analysts

| Agent | Model | Trigger |
|-------|-------|---------|
| `network-analyst` | Sonnet | Network IOC, C2 pattern, beaconing, packet captures |
| `layer2-specialist` | Sonnet | ARP table anomalies, MAC flooding, VLAN integrity, STP changes |
| `layer3-specialist` | Sonnet | Routing anomalies, ICMP flood, fragmentation, asymmetric routing |
| `layer4-specialist` | Sonnet | TCP anomalies, UDP amplification, port scan, connection exhaustion |
| `layer5-specialist` | Sonnet | Session token anomalies, RPC abuse, SIP irregularities, SMB enumeration |
| `layer6-specialist` | Sonnet | Encoding anomalies, TLS downgrade, deserialization gadget chains |
| `layer7-specialist` | Sonnet | Web app anomalies, API abuse, authentication bypass, access logs |

---

## Security Analysts

| Agent | Model | Trigger |
|-------|-------|---------|
| `cybersec-analyst` | Sonnet | CVE-YYYY-NNNNN, IOC discovery, MITRE technique T1xxx |
| `certificate-analyst` | Sonnet | TLS anomalies, unexpected issuer, self-signed certs, CT log gaps |
| `encoding-specialist` | Sonnet | Suspicious encoded strings, encoding anomalies, obfuscated payloads |
| `settings-analyst` | Sonnet | Config compliance, privilege escalation via misconfiguration |
| `steganography-analyst` | Sonnet | Suspicious media files, LSB embedding, hidden payloads |
| `vuln-scanner` / `vulnerability-scanner` | Sonnet | OWASP 2025, supply chain, attack surface mapping |
| `threat-modeler` | Sonnet | Threat model, attack surface, STRIDE, risk scoring |
| `audiovideo-analyst` | Sonnet | Media metadata, deepfake indicators, AV integrity checks |
| `watchdog` | Haiku | SSL keylog files, cert stores, private key locations |
| `command-verifier` | Haiku | Command safety review, destructive command gating, shell injection |

---

## Developers

| Agent | Model | Trigger |
|-------|-------|---------|
| `python-developer` | Sonnet | Python code task, script writing, API endpoint, ORM model, tests |
| `cpp-developer` | Sonnet | ELF binary, kernel module, eBPF C, exploit, reverse engineering |
| `postgres-db-engineer` | Sonnet | PostgreSQL optimization, JSONB, advanced queries, schema design |
| `code-reviewer` | Sonnet | Pull request review, code feedback, security scanning |

---

## Frontend

| Agent | Model | Trigger |
|-------|-------|---------|
| `frontend-design` | Sonnet | Web components, landing pages, dashboards, HTML/CSS |
| `senior-frontend` | Sonnet | ReactJS, NextJS, TypeScript, Tailwind, performance optimization |

---

## Meta

| Agent | Model | Description |
|-------|-------|-------------|
| `agent-factory` | Opus | Creates new production-grade agents from description. Generates complete YAML frontmatter + system prompt with 9-chapter blueprint. |

---

## Teams

3 pre-composed team modes available (`.claude/agents/teams/`):

| Team | File | Composition |
|------|------|-------------|
| Blue Team | `blue-team.md` | Defensive — forensics analysts, detection, response |
| Red Team | `red-team.md` | Offensive simulation — exploitation, persistence, C2 |
| Purple Team | `purple-team.md` | Combined — simultaneous offense + defense |

Invoke via `cybersec-agent` with mode argument:
```
@cybersec-agent blue   # blue-team investigation
@cybersec-agent red    # red-team simulation
@cybersec-agent purple # purple-team exercise
```

---

## A2A Invocation Examples

```bash
# Route to specific agent
@cybersec-analyst CVE-2024-1234

# Route to orchestrator (auto-routes to best specialist)
investigate this IOC: 192.168.1.100

# Fanout to all agents
@fanout analyze this ELF binary: /tmp/suspicious

# List all agents
list agents
```

---

## Agent Frontmatter Schema

Every agent (except AGENT_FACTORY) must have:

```yaml
---
name: agent-name          # matches filename (kebab-case)
description: "..."        # single-line trigger description for routing
model: sonnet             # haiku | sonnet | opus
maxTurns: 30              # conversation turn limit
tools:                    # tools this agent may use
  - Read
  - Bash
disallowedTools:          # optional — read-only analysts
  - Write
  - Edit
---
```

Model selection guidelines:
- **Haiku** — lightweight, fast: watchdog, command-verifier, layer2–6 specialists
- **Sonnet** — general: most analysts and developers
- **Opus** — heavy reasoning: firmware-analyst, reverse-engineer, agent-factory
