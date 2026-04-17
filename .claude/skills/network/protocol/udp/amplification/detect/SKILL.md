---
name: protocol-udp-amplification-detect
description: >
  Detect UDP amplification and reflection DDoS attacks targeting DNS, NTP, SSDP, Memcached, and QUIC endpoints by analyzing traffic asymmetry and source IP diversity.
action: detect
domain: cybersecurity
subdomain: network-protocol-analysis
tags:
  - udp-amplification
  - ddos
  - reflection
  - ntp
  - dns
  - memcached
  - ssdp
nist_csf:
  - DE.CM-01
  - PR.IR-01
mitre:
  - T1498.002
cwe:
  - CWE-400
---
