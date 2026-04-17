---
name: tshark
description: Automate network traffic analysis using tshark and pyshark for protocol statistics, suspicious flow detection,
action: tshark
  DNS anomaly identification, and IOC extraction from PCAP files
domain: cybersecurity
subdomain: network-security
tags:
- tshark
- pyshark
- pcap
- packet-analysis
- network-forensics
- wireshark
- traffic-analysis
version: '1.0'
author: dcx7c5
license: Apache-2.0
nist_csf:
- PR.IR-01
- DE.CM-01
- ID.AM-03
- PR.DS-02
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
source: Anthropic-Cybersecurity-Skills
mitre_attack:
- T1040
- T1041
- T1059
- T1071.001
- T1562.001
---

# Performing Network Traffic Analysis with TShark

## Overview

This skill automates packet capture analysis using tshark (Wireshark CLI) and pyshark (Python wrapper). It extracts protocol distribution statistics, identifies suspicious network flows (port scans, beaconing, data exfiltration), extracts IOCs (IPs, domains, URLs), and detects DNS tunneling patterns from PCAP files.


## When to Use

- When conducting security assessments that involve performing network traffic analysis with tshark
- When following incident response procedures for related security events
- When performing scheduled security testing or auditing activities
- When validating security controls through hands-on testing

## Prerequisites

- tshark (Wireshark CLI) installed and in PATH
- Python 3.8+ with pyshark library
- PCAP or PCAPNG capture file for analysis

## Steps

1. **Extract Protocol Statistics** — Generate protocol hierarchy and conversation statistics from the capture
2. **Identify Top Talkers** — Rank source/destination IPs by volume and connection count
3. **Detect Suspicious Flows** — Flag port scanning patterns, unusual port usage, and high-frequency connections
4. **Extract Network IOCs** — Pull unique IPs, domains from DNS queries, and URLs from HTTP traffic
5. **Analyze DNS Traffic** — Detect DNS tunneling via high-entropy subdomain queries and excessive TXT records
6. **Generate Analysis Report** — Produce structured report with flow summaries and threat indicators

## Expected Output

- JSON report with protocol statistics and top talkers
- Suspicious flow detections with severity ratings
- Extracted IOCs (IPs, domains, URLs)
- DNS anomaly analysis results


---

## CyberSecSuite Integration

```bash
# Open a case before starting investigation
mcp__cybersec__case_open --title "tshark" --type investigation

# Persist findings to PostgreSQL
mcp__cybersec__add_finding --title "..." --severity high --description "..."

# Log IOCs
mcp__cybersec__add_ioc --type domain --value "..." --confidence 0.9

# Map to MITRE
mcp__cybersec__suggest_mitre --description "..."
```

**Agent:** `@cybersec-agent` → delegates to appropriate specialist
