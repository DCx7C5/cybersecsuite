---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects least-significant-bit steganography in BMP images via statistical\
  \ tests."
domain: cybersecurity
mitre_attack:
- T1027.003
name: bmp-lsb-detect
nist_csf: []
subdomain: steganography
tags:
- steganography
- hidden-data
- detect
---


## Overview

Detects steganographically hidden data in carrier files using statistical analysis and tool-assisted extraction.

## Usage

```
Use when investigating suspicious media files for hidden payloads or covert communication channels.
```
