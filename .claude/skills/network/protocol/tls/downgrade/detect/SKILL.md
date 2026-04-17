---
name: protocol-tls-downgrade-detect
description: >
  Detect TLS downgrade attacks, BEAST, POODLE, CRIME, and DROWN vulnerabilities by auditing cipher suites, protocol versions, and certificate validation failures.
action: detect
domain: cybersecurity
subdomain: network-protocol-analysis
tags:
  - tls-downgrade
  - ssl
  - poodle
  - beast
  - cipher-suite
  - testssl
  - sslyze
nist_csf:
  - DE.CM-04
  - PR.DS-02
mitre:
  - T1040
  - T1557
cwe:
  - CWE-757
  - CWE-326
---
