---
capec:
- CAPEC-186
cve: []
cwe:
- CWE-311
description: ">\n  Detects hidden content in DOCX metadata, revisions, and XML comments."
domain: cybersecurity
mitre_attack:
- T1027.003
name: docx-metadata-detect
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
