---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects DCT-domain steganography in JPEG images using StegDetect\
  \ or F5 analysis."
domain: cybersecurity
mitre_attack:
- T1027.003
name: jpg-dct-detect
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
