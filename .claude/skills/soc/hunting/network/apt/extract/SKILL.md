---
name: hunting-network-apt-extract
description: Network APT hunting — capture and analyze traffic for C2 beaconing, ARP spoofing, DNS anomalies, and unusual outbound connections on Linux. Uses ip, ss, tcpdump, and ARP table analysis.
domain: cybersecurity
subdomain: network-forensics
tags:
- network
- apt
- c2
- arp
- dns
- beaconing
- linux
mitre_attack:
- T1071
- T1071.001
- T1041
- T1090
- T1557.002
cve: []
cwe: []
nist_csf:
- DE.CM-1
- DE.CM-7
capec:
- CAPEC-609
---
## Overview

Network-layer APT hunting on Linux. Checks ARP table for duplicate MAC entries (spoofing), active connections for unusual ports/destinations, DNS queries for tunneling indicators, and optionally captures raw traffic via tcpdump for post-analysis. All findings written to session findings.md.

## Usage

```
Invoke when: suspected C2, lateral movement, exfiltration, or ARP/DNS poisoning.
Options: --capture (live tcpdump), --analyze (inspect existing pcap), --duration SECONDS
```

## Checks

| Check | Tool | Indicator |
|---|---|---|
| ARP table | `ip neigh` | Duplicate IPs with different MACs |
| Active connections | `ss -tnp` | Unusual ports, foreign IPs, suspicious processes |
| DNS | `/etc/resolv.conf`, `ss` | Non-standard DNS servers, high-volume lookups |
| Traffic capture | `tcpdump` | Beaconing intervals, large outbound transfers |

## MITRE Coverage

| Technique | Description |
|---|---|
| T1071 | Application Layer Protocol C2 |
| T1071.001 | C2 over HTTP/HTTPS |
| T1041 | Exfiltration Over C2 Channel |
| T1090 | Proxy / Traffic Tunneling |
| T1557.002 | ARP Cache Poisoning |
