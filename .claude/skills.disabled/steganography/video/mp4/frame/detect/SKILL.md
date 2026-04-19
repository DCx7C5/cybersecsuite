---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects inter-frame steganography in MP4 video via frame-difference\
  \ analysis."
domain: cybersecurity
mitre_attack:
- T1027.003
name: mp4-frame-detect
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
