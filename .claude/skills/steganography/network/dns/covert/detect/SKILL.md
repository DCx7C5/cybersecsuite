---
name: network-dns-covert-detect
description: Detects DNS-based covert channel steganography via query entropy analysis.
domain: cybersecurity
subdomain: steganography
tags:
- steganography
- hidden-data
- detect
mitre_attack:
- T1027.003
cve: []
cwe:
- CWE-311
nist_csf: []
capec:
- CAPEC-186
---
## Overview

Detects steganographically hidden data in carrier files using statistical analysis and tool-assisted extraction.

## Usage

```
Use when investigating suspicious media files for hidden payloads or covert communication channels.
```
