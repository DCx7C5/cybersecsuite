---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects hidden data in MP3 ID3 tags and metadata fields."
domain: cybersecurity
mitre_attack:
- T1027.003
name: mp3-metadata-detect
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
