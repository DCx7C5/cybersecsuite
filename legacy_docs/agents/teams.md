# Team Modes

CyberSecSuite supports three pre-composed multi-agent team modes.

Enabled by `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `.claude/settings.json`.

---

## Teams

| Team        | File             | Focus                                                |
|-------------|------------------|------------------------------------------------------|
| Blue Team   | `blue-team.md`   | Defensive investigation, detection, incident response |
| Red Team    | `red-team.md`    | Offensive simulation, exploitation, persistence, C2  |
| Purple Team | `purple-team.md` | Simultaneous offense + defense coordination          |

---

## Invocation

```bash
# Via cybersec-agents orchestrator
@cybersec-agents blue    # Blue-team investigation
@cybersec-agents red     # Red-team simulation
@cybersec-agents purple  # Purple-team exercise

# Direct team invocation
@blue-team [prompt]
@red-team [prompt]
@purple-team [prompt]
```

---

## Blue Team Composition

Focus: detect, contain, investigate, remediate.

Key agents included:
- `filesystem-analyst` — file system forensics
- `kernel-analyst` — kernel + rootkit analysis
- `memory-analyst` — memory forensics
- `persistence-analyst` — persistence mechanisms
- `network-analyst` — network IOC + C2 detection
- `logfile-analyst` — log analysis + timeline
- `cybersec-analyst` — CVE + MITRE mapping
- `watchdog` — credential + cert monitoring

---

## Red Team Composition

Focus: simulate attacker TTPs, find exploitable paths.

Key agents included:
- `reverse-engineer` — binary analysis + shellcode
- `firmware-analyst` — firmware/UEFI exploitation
- `vuln-scanner` — vulnerability discovery
- `cpp-developer` — exploit development
- `encoding-specialist` — payload encoding/evasion
- `steganography-analyst` — covert channel analysis

---

## Purple Team Composition

Combined simultaneous offense + defense. Coordinates red + blue in parallel for continuous adversarial testing.

---

## Configuration

Teams are defined in `.claude/agents/teams/*.md`. Each file has YAML frontmatter specifying the `model`, `tools`, and `agents` array listing the sub-agents to include:

```yaml
---
name: blue-team
description: "Blue team defensive investigation"
model: sonnet
agents:
  - filesystem-analyst
  - kernel-analyst
  - memory-analyst
  - persistence-analyst
  - network-analyst
  - logfile-analyst
  - cybersec-analyst
  - watchdog
---
```

Teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Set in `.claude/settings.json` or by running `make css-first-setup`.
