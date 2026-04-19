---
name: android-apk-analyze
description: >
  Analyze Android APK files for malicious behavior using static analysis tools including apktool, jadx, androguard, and MobSF.
domain: cybersecurity
subdomain: mobile-security
tags: [android, apk, static-analysis, mobile, malware]
nist_csf: [DE.AE-02]
model: sonnet
maxTurns: 20
tools: [Read, Write, Bash, Glob, Grep]
mitre_attack: [T1422, T1409, T1437]
capec: []
---

# Android APK Analyze

## Overview

Perform static and dynamic analysis of Android APK files to detect malicious behavior, data exfiltration, and suspicious permissions.

## Prerequisites

- `apktool`, `jadx`, `androguard` or `MobSF` installed
- JDK 11+ for jadx
- Python 3 with `androguard` for deep analysis

## Procedure

### Step 1 — Decompile APK

```bash
APK="/path/to/target.apk"
apktool d "$APK" -o /tmp/apk-decompiled
```

### Step 2 — Extract Java source

```bash
jadx "$APK" -d /tmp/apk-jadx
```

### Step 3 — Check permissions

```bash
cat /tmp/apk-decompiled/AndroidManifest.xml | grep -i "uses-permission"
```

### Step 4 — Hunt for IOCs

```bash
grep -r "http[s]\?://" /tmp/apk-decompiled/ --include="*.smali"
grep -rE "(API_KEY|SECRET|PASSWORD|token)" /tmp/apk-decompiled/ -i
```

### Step 5 — Hash and record

```bash
HASH=$(b2sum -l 256 "$APK" | awk '{print $1}')
echo "blake2b:$HASH  $APK"
```

## MITRE ATT&CK

| Technique | Name |
|-----------|------|
| T1422 | System Network Configuration Discovery |
| T1409 | Access Stored Application Data |
