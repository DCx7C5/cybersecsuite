---
name: kernel-syscall-audit-monitor
description: Linux auditd framework for real-time syscall monitoring, audit rule configuration, and forensic log analysis. Covers auditctl, ausearch, aureport, and correlation with threat actor TTPs.
domain: cybersecurity
subdomain: endpoint-forensics
tags:
- linux
- auditd
- syscall
- kernel
- forensics
- blue-team
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1059
- T1070.002
- T1562.012
- T1543.002
nist_csf:
- DE.CM-01
- DE.AE-02
- RS.AN-03
capec: []
---

# Linux Audit Syscall Monitor

## Overview

Linux `auditd` is the kernel-level auditing framework that intercepts and logs system calls (syscalls) in real time. This skill covers configuration, rule authoring, live monitoring, and forensic log analysis to detect malicious activity including privilege escalation, file tampering, and credential access.

## When to Use

- When baseline syscall activity needs to be recorded for anomaly detection
- When investigating a suspected compromise on a Linux endpoint
- When implementing compliance-driven audit logging (PCI-DSS, CIS Benchmark)
- When detecting MITRE techniques involving command execution, file writes, or auth bypass

## Prerequisites

- `auditd` installed and running (`systemctl status auditd`)
- Root or `CAP_AUDIT_CONTROL` capability
- `/etc/audit/audit.rules` or `/etc/audit/rules.d/` writable

## Core Commands

### Check Audit Status
```bash
auditctl -s                        # Kernel audit status
systemctl status auditd
cat /etc/audit/auditd.conf
```

### List Active Rules
```bash
auditctl -l                        # All active rules
cat /etc/audit/rules.d/*.rules
```

### Add Critical Rules
```bash
# Monitor /etc/passwd and /etc/shadow writes
auditctl -w /etc/passwd -p wa -k identity_change
auditctl -w /etc/shadow -p wa -k identity_change

# Monitor setuid/setgid executions
auditctl -a always,exit -F arch=b64 -S execve -F euid=0 -F auid>=1000 -k privesc

# Monitor ptrace (process injection)
auditctl -a always,exit -F arch=b64 -S ptrace -k process_injection

# Monitor module loading (LKM rootkits)
auditctl -w /sbin/insmod -p x -k module_load
auditctl -w /sbin/rmmod  -p x -k module_load
auditctl -a always,exit -F arch=b64 -S init_module -S finit_module -k module_load

# Monitor cron modifications
auditctl -w /etc/cron.d    -p wa -k cron_persistence
auditctl -w /var/spool/cron -p wa -k cron_persistence

# Monitor SSH key changes
auditctl -w /root/.ssh -p wa -k ssh_key_change
```

### Search Audit Logs
```bash
# By key tag
ausearch -k identity_change --interpret

# By user
ausearch -ua 1000 -ts today --interpret

# By syscall
ausearch -sc execve -ts yesterday --interpret | head -200

# Failed logins
ausearch -m USER_AUTH -sv no -ts today

# Privileged command executions
ausearch -k privesc --interpret | grep -E "exe=|comm="
```

### Generate Reports
```bash
# Summary report
aureport --summary

# Failed events
aureport --failed

# Login activity
aureport --auth

# Executable usage
aureport --executable --summary
```

## Forensic Analysis Workflow

1. **Snapshot rules at investigation start**: `auditctl -l > /tmp/audit_rules_snapshot.txt`
2. **Check for rule tampering**: compare against baseline
3. **Extract relevant timeframe**: `ausearch -ts <start> -te <end> -k <key>`
4. **Correlate with /var/log/auth.log** and `/var/log/syslog`
5. **Map events to MITRE ATT&CK techniques**

## MITRE ATT&CK Mapping

| Rule Key | Technique |
|---|---|
| `identity_change` | T1003.008 — /etc/passwd and /etc/shadow |
| `module_load` | T1547.006 — Kernel Modules and Extensions |
| `process_injection` | T1055 — Process Injection |
| `cron_persistence` | T1053.003 — Cron |
| `privesc` | T1068 — Exploitation for Privilege Escalation |

## IOC Indicators

- Audit daemon stopped unexpectedly → T1562.012 (Disable Security Tools)
- Rules cleared (`auditctl -D`) without admin action → Active evasion
- `NETFILTER_CFG` events without change management → Firewall tampering

