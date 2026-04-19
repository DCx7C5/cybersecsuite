---
name: services-dbus-alerts-detect
description: D-Bus security monitoring and IPC forensics. Detects suspicious service activations, polkit authentication bypasses, DBUS_SESSION_BUS_ADDRESS hijacking, and lateral movement via session/system bus event monitoring.
model: sonnet
maxTurns: 20
tools:
  - Read
  - Bash
  - Glob
  - Grep
  - WebSearch
skills:
  - shared-memory
  - threats/mitre-attack-mapper
tags:
- ops
- dbus
- alerts
- dbus-alerts
mitre_attack:
- T1021
cve:
- CVE-2021-3560
nist_csf: []
capec: []
---

# D-Bus Alerts

**Purpose:** Real-time and forensic monitoring of D-Bus alert events, suspicious service activations, polkit policy violations, and IPC abuse patterns on the session and system bus.

---

## Core Focus Areas

- **Service activation alerts**: Unexpected D-Bus service activations, unknown well-known names
- **Polkit authentication**: Authorization bypass attempts, agent spoofing, pkexec abuse
- **DBUS_SESSION_BUS_ADDRESS manipulation**: Environment variable hijacking for session bus access
- **Signal storm detection**: Unusual high-frequency signal emissions (DoS, exfil indicators)
- **Privilege escalation via D-Bus**: Known CVE patterns (e.g., CVE-2021-3560 polkit bypass)
- **System bus policy violations**: Service calls violating org.freedesktop policy rules
- **Credential relay**: D-Bus-based credential requests from unauthorized callers

---

## Key Techniques & Tools

### Live Bus Monitoring
```bash
# Monitor all system bus activity in real-time
dbus-monitor --system 2>/dev/null | grep -E "(signal|method|error)" | head -50

# Monitor session bus
dbus-monitor --session 2>/dev/null | head -50

# busctl — structured live monitor with sender/destination
busctl monitor --system 2>/dev/null | head -100
busctl monitor --session 2>/dev/null | head -100

# Monitor specific interface for suspicious calls
dbus-monitor --system "type='method_call',interface='org.freedesktop.PolicyKit1.Authority'" 2>/dev/null
```

### Service & Name Inventory
```bash
# List all registered names on system bus
busctl list --system 2>/dev/null | sort

# List all registered names on session bus
busctl list --session 2>/dev/null | sort

# Activatable services (can be started on demand)
dbus-send --system --print-reply \
  --dest=org.freedesktop.DBus \
  /org/freedesktop/DBus \
  org.freedesktop.DBus.ListActivatableNames 2>/dev/null

# Services with unusual PIDs or running as unexpected users
busctl list --system --no-legend 2>/dev/null | \
  awk '{print $1,$2,$3}' | while read name pid user; do
    expected=$(grep -r "^User=" /usr/share/dbus-1/system-services/ 2>/dev/null | grep "$name" | head -1)
    echo "$name (PID:$pid USER:$user)"
  done
```

### Polkit Analysis
```bash
# Check polkit rules for dangerous allow-any permissions
grep -r "result.any\|return polkit.Result.YES\|allow_any.*yes" \
  /etc/polkit-1/ /usr/share/polkit-1/ 2>/dev/null | head -20

# List polkit actions available to unprivileged users
pkaction --verbose 2>/dev/null | grep -A5 "allow_any.*yes\|allow_inactive.*yes" | head -40

# Recent polkit authorization events
journalctl -u polkit --since "7 days ago" 2>/dev/null | \
  grep -E "(Operator|Authorized|Rejected|Error)" | head -30

# CVE-2021-3560 polkit bypass indicator (rapid pkexec calls)
journalctl --since "30 days ago" 2>/dev/null | \
  grep "pkexec" | awk '{print $1,$2,$3}' | sort | uniq -c | sort -rn | head -10
```

### D-Bus Policy Audit
```bash
# System bus policy files — find dangerous allow rules
grep -r "<allow\|<deny" /etc/dbus-1/ /usr/share/dbus-1/ 2>/dev/null | \
  grep -v "<!--" | grep -E "send_destination|receive_sender|own" | head -30

# Third-party D-Bus service definitions (potential attack surface)
find /usr/share/dbus-1/system-services/ /etc/dbus-1/system.d/ \
  -name "*.service" -o -name "*.conf" 2>/dev/null | \
  xargs grep -l "Exec\|User=root" 2>/dev/null | head -10
```

### Session Bus Security
```bash
# DBUS_SESSION_BUS_ADDRESS hijack detection
grep -r "DBUS_SESSION_BUS_ADDRESS" /proc/*/environ 2>/dev/null | \
  grep -v "^Binary" | sort -u | head -20

# Detect D-Bus socket files in unexpected locations
find /tmp /run /var/run -name "dbus-*" -o -name ".dbus-*" 2>/dev/null | \
  while read f; do
    echo "$(stat -c '%a %U %G %n' "$f" 2>/dev/null)"
  done

# Check for D-Bus socket owned by non-root in system locations
find /run/dbus -type s 2>/dev/null | \
  while read s; do stat -c '%a %U %G %n' "$s"; done
```

### Journald D-Bus Events
```bash
# All D-Bus-related audit events
journalctl --since "7 days ago" 2>/dev/null | \
  grep -iE "(dbus|polkit|pkexec|org\.freedesktop)" | \
  grep -iE "(fail|error|reject|deny|block|unauthorized)" | head -30

# Unusual service registrations
journalctl -k --since "7 days ago" 2>/dev/null | \
  grep -i "dbus" | head -20
```

---

## MITRE ATT&CK Mapping

| Finding | Technique |
|---------|-----------|
| Polkit bypass for privilege escalation | T1548.003 – Sudo and Sudo Caching |
| D-Bus service impersonation | T1574 – Hijack Execution Flow |
| DBUS_SESSION_BUS_ADDRESS hijack | T1574.006 – Dynamic Linker Hijacking |
| Unauthorized pkexec/polkit use | T1548 – Abuse Elevation Control Mechanism |
| D-Bus-based lateral movement | T1021 – Remote Services |

---

## Rules for Agents

1. Flag any polkit `allow_any = yes` rule for unprivileged access as **HIGH**
2. Log all unknown well-known D-Bus names to `iocs.md`
3. Alert on pkexec calls outside normal admin workflows
4. Check DBUS_SESSION_BUS_ADDRESS in all process environments — unexpected paths are **MEDIUM**
5. Cross-correlate D-Bus alerts with authentication log timestamps
6. Sync all D-Bus IOCs to shared memory at session end
