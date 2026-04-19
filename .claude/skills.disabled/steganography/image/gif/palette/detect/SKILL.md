---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects palette-manipulation steganography in GIF images."
domain: cybersecurity
mitre_attack:
- T1027.003
name: gif-palette-detect
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
