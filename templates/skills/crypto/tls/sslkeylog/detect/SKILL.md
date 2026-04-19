---
name: tls-sslkeylog-detect
description: TLS key logging management and SSLKEYLOGFILE forensics. Detects insecure keylog file permissions, unauthorized reader processes, ecapture-tls integration, TLS session decryption, and SSLKEYLOGFILE-based exfiltration indicators.
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
  - network/recon
  - threats/mitre-attack-mapper
tags:
- crypto-pki
- tls
- sslkeylog
- tls-sslkeylog
mitre_attack:
- T1041
nist_csf: []
capec: []
---

# SSLKEYLOG Skill – TLS Key Logging Management & Analysis

**Purpose:**  
This skill provides specialized handling, security analysis, and monitoring of the `SSLKEYLOGFILE` environment variable and the associated keylog file. It is critical for legitimate TLS decryption (e.g. `ecapture-tls`) while detecting misuse, insecure permissions, and potential exfiltration vectors.

---

## Automatic Behavior

When activated, this skill:

1. **Detects current SSLKEYLOGFILE configuration**
2. **Checks file permissions** (flags 0666 or world-readable as HIGH risk)
3. **Verifies ownership** and access by non-authorized processes
4. **Monitors for tampering or deletion**
5. **Integrates with ecapture-tls service status**
6. **Logs all findings** into the current session’s `iocs.md`

---

## Core Capabilities

- Detect and report insecure `SSLKEYLOGFILE` permissions (especially 0666)
- Identify which processes are reading/writing the keylog file
- Validate legitimate use vs. potential malicious access
- Monitor for sudden permission changes or file deletion
- Cross-reference with `ecapture-tls.service` status
- Recommend secure hardening steps (chmod 0600, proper ownership)
- Track keylog file size and growth rate (potential exfil indicator)

---

## Key IOCs to Always Check

| Type                 | Value / Pattern                                   | Severity  | Notes                 |
|----------------------|---------------------------------------------------|-----------|-----------------------|
| File Permission      | `SSLKEYLOGFILE` with mode 0666                    | 🔴 HIGH   | World-writable keylog |
| File Permission      | `SSLKEYLOGFILE` owned by non-root                 | 🟡 MEDIUM | Potential compromise  |
| Process Access       | Non-browser / non-ecapture process reading keylog | 🔴 HIGH   | Suspicious access     |
| Environment Variable | `SSLKEYLOGFILE=/path/to/keys.log`                 | INFO      | Active TLS logging    |
| File Growth          | Rapid increase in keylog size                     | 🟡 MEDIUM | Possible mass exfil   |

---

## Rules for the Agent

1. **Always check** `$SSLKEYLOGFILE` (or `/var/log/sslkeylogfile.txt`) at session start.
2. **Immediately flag** if the file is world-readable or world-writable.
3. **Document** current permissions, owner, and accessing processes.
4. **Cross-validate** with `ecapture-tls.service` status and `lsof`.
5. **Recommend** `chmod 0600` + proper ownership when insecure.
6. **Never assume** world-writable is benign — always treat as HIGH until proven legitimate.
7. **Log every check** in `session.log` and add relevant IOCs to `iocs.md`.
8. **Sync** findings to Shared Memory at session end.

---

## Example Output in iocs.md

```markdown
## SSLKEYLOG / TLS Key Logging IOCs

| # | Type | Value | Context | Confidence | Status |
|---|------|-------|---------|------------|--------|
| 1 | File Permission | /var/log/sslkeylogfile.txt (0666) | World-writable TLS keys | HIGH | OPEN |
| 2 | Process Access | brave (PID 1234) | Legitimate browser access | CONFIRMED | CLEARED |
| 3 | Environment | SSLKEYLOGFILE=/var/log/sslkeylogfile.txt | ecapture-tls active | MEDIUM | MONITOR |

Ready to monitor and secure SSLKEYLOGFILE.
```
---

## Extended Techniques & Tools

### SSLKEYLOGFILE Detection & Audit
```bash
# Check if SSLKEYLOGFILE is set in any running process
grep -r "SSLKEYLOGFILE" /proc/*/environ 2>/dev/null | \
  tr '\0' '\n' | grep SSLKEYLOGFILE | sort -u

# Verify permissions and ownership of keylog file
if [ -n "$SSLKEYLOGFILE" ]; then
  ls -la "$SSLKEYLOGFILE" 2>/dev/null
  stat -c "%a %U %G %n" "$SSLKEYLOGFILE" 2>/dev/null
  # World-readable = HIGH
  PERM=$(stat -c "%a" "$SSLKEYLOGFILE" 2>/dev/null)
  (( 8#${PERM:-000} & 4 )) && echo "🔴 WORLD-READABLE SSLKEYLOGFILE"
fi

# Find all keylog files on filesystem
find / -name "sslkeylog*" -o -name "*.sslkey" -o -name "ssl-key*.log" \
  -o -name "premaster*.log" 2>/dev/null | \
  grep -v "/proc\|/sys" | head -20

# Check /var/log for common keylog locations
ls -la /var/log/sslkeylog* /var/log/ecapture* 2>/dev/null
```

### Unauthorized Keylog Reader Detection
```bash
# Who has the keylog file open (lsof)
[ -n "$SSLKEYLOGFILE" ] && lsof "$SSLKEYLOGFILE" 2>/dev/null

# Processes with inotify watches on keylog (monitoring it)
for pid in $(ps -eo pid --no-headers | tr -d ' '); do
  cat /proc/$pid/fdinfo/* 2>/dev/null | grep -q "inotify" && \
    ls -la /proc/$pid/fd 2>/dev/null | grep "$SSLKEYLOGFILE" && \
    echo "WATCHER PID: $pid ($(cat /proc/$pid/comm 2>/dev/null))"
done 2>/dev/null | head -10

# File access audit (auditd)
ausearch -f "$SSLKEYLOGFILE" --start "today" 2>/dev/null | head -20
```

### ecapture-tls Integration
```bash
# ecapture-tls service status
systemctl status ecapture-tls 2>/dev/null | head -10
systemctl is-active ecapture-tls 2>/dev/null

# ecapture process check
pgrep -a ecapture 2>/dev/null
pgrep -a tls_capture 2>/dev/null

# ecapture output directory
ls -la /var/log/ecapture/ 2>/dev/null
ls -la /tmp/ecapture* 2>/dev/null
```

### TLS Session Decryption (Wireshark/tshark)
```bash
# Decrypt TLS traffic using keylog file (tshark)
tshark -r capture.pcap \
  -o "tls.keylog_file:$SSLKEYLOGFILE" \
  -Y "tls" -T fields \
  -e frame.time -e ip.src -e ip.dst \
  -e http.request.method -e http.request.uri \
  -e http.response.code 2>/dev/null | head -30

# Extract decrypted HTTP/2 streams
tshark -r capture.pcap \
  -o "tls.keylog_file:$SSLKEYLOGFILE" \
  -Y "http2" -T fields \
  -e ip.src -e ip.dst -e http2.headers.method \
  -e http2.headers.path -e http2.headers.status 2>/dev/null | head -20

# Export decrypted data
tshark -r capture.pcap \
  -o "tls.keylog_file:$SSLKEYLOGFILE" \
  --export-objects "http,/tmp/tls_exports/" 2>/dev/null
ls /tmp/tls_exports/ 2>/dev/null | head -10
```

### SSLKEYLOGFILE Exfiltration Indicators
```bash
# Rapid keylog file size growth (potential exfiltration)
if [ -n "$SSLKEYLOGFILE" ] && [ -f "$SSLKEYLOGFILE" ]; then
  SIZE1=$(stat -c "%s" "$SSLKEYLOGFILE" 2>/dev/null)
  sleep 5
  SIZE2=$(stat -c "%s" "$SSLKEYLOGFILE" 2>/dev/null)
  DELTA=$(( SIZE2 - SIZE1 ))
  echo "Growth in 5s: ${DELTA} bytes"
  [ "$DELTA" -gt 10000 ] && echo "⚠ HIGH GROWTH RATE — potential mass TLS capture"
fi

# Network connections from keylog file path processes
lsof "$SSLKEYLOGFILE" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u | \
  while read pid; do
    echo "PID $pid connections:"
    ss -tp 2>/dev/null | grep "pid=$pid," | head -5
  done

# Keylog file copied to unusual location
find /tmp /home /var/tmp -name "*.sslkey" -o -name "*premaster*" \
  -o -name "*keylog*" 2>/dev/null | grep -v "$SSLKEYLOGFILE" | head -5
```

### Hardening Recommendations
```bash
# Set secure permissions on keylog file
chmod 0600 "$SSLKEYLOGFILE" 2>/dev/null
chown root:root "$SSLKEYLOGFILE" 2>/dev/null

# Verify fix
stat -c "%a %U %G" "$SSLKEYLOGFILE" 2>/dev/null

# Set auditd watch on keylog file
sudo auditctl -w "$SSLKEYLOGFILE" -p rwa -k sslkeylog_access 2>/dev/null
```

---

## MITRE ATT&CK Mapping

| Finding                               | Technique                            |
|---------------------------------------|--------------------------------------|
| World-readable SSLKEYLOGFILE          | T1552.004 – Private Keys             |
| Unauthorized process reading keylog   | T1040 – Network Sniffing             |
| Keylog file copied/exfiltrated        | T1041 – Exfiltration Over C2 Channel |
| TLS session decrypted for C2 analysis | T1573 – Encrypted Channel            |

---

**Ready to use.**

