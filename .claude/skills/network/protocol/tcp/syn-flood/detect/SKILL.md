---
name: protocol-tcp-syn-flood-detect
description: >
  Detect TCP SYN flood denial-of-service attacks by monitoring half-open connection state, SYN cookie effectiveness, and rate-based anomalies with netstat, ss, and iptables counters.
action: detect
domain: cybersecurity
subdomain: network-protocol-analysis
tags:
  - syn-flood
  - dos
  - tcp
  - rate-limiting
  - iptables
  - kernel-netstat
nist_csf:
  - DE.CM-01
  - PR.IR-01
mitre:
  - T1498.001
cwe:
  - CWE-400
capec: []
---
